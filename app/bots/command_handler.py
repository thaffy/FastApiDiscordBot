import asyncio
import math
import pandas as pd
from typing import Optional, List

from discord import Message
from discord.ext import commands

from app.calculators.flipping_calculator import FlippingCalculator
from app.config import settings
from app.constants import constants
from app.models.runescape import LatestItemsResponse, FlippingResult, DiscordFlippingResult, OsrsItem
from app.utils.logger import logger


class CommandHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.item_last_message: Optional[Message] = None
        self.flipping_calculator = FlippingCalculator()

    @staticmethod
    def get_emoji_by_roi(roi: float) -> str:
        emoji = "👀"
        if roi <= 0:  # idk if this is correct, seems like a lot of elif statements
            emoji = "🟥"
        elif roi <= 3:
            emoji = ":yellow_square:"
        elif roi <= 10:
            emoji = "🟦"
        elif roi <= 30:
            emoji = "🟩"

        return emoji

    def format_item_details(self, calc: FlippingResult, item: OsrsItem, volume: int) -> str:
        """Format item details for Discord message."""
        buy_limit_info = (
            "Item likely has no buy limit"
            if item.limit == 100000
            else ""
        )

        return (
            f"### **{item.name}** \t {self.get_emoji_by_roi(roi=calc.roi_percentage)}\n"
            f"Low Price {calc.low_price:,}gp / High Price {calc.high_price:,}gp\n"
            f"Difference: {calc.price_diff:,}gp\n"
            f"Buy limit: {item.limit:,} *({calc.cash_needed:,}gp to exhaust {buy_limit_info})*\n"
            f"Volume: {volume:,}\n"
            f"\n"
            f"Profit per item: **{calc.profit_per_item:,}gp** per item "
            f"(No tax: ||{calc.profit_per_item_no_tax:,}gp||)\n"
            f"Max Profit: **{calc.total_profit:,}gp** per buy limit "
            f"(No tax: ||{calc.profit_no_tax:,}gp||)\n"
            f"ROI: **{calc.roi_percentage:.2f}%**\n"
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, *args, **kwargs):
        logger.error(f"Error in command {ctx}: {args} {kwargs}")
        await ctx.message.add_reaction("🤡")

    @commands.command(name='ping', help='Responds with pong')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def ping(self, ctx: commands.Context):
        """Simple ping command to test bot responsiveness"""
        await ctx.send('pong')

    @commands.command(name='commands', help='List all available commands')
    async def get_commands(self, ctx: commands.Context):
        """List all available commands"""
        curr_commands = [f"{command.name}: {command.help}" for command in self.bot.commands]
        await ctx.send("Current commands are:\n" + "\n".join(f"{settings.DISCORD_COMMAND_PREFIX}{cmd}" for cmd in curr_commands))

    @commands.command(name='ranks')
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def get_players_rank(self,ctx: commands.Context):
        from app.dependencies import get_dota_service
        dota_service = get_dota_service()
        ids = constants.get_player_ids()

        result = ""

        for player_id in ids:
            response = await dota_service.get_player(player_id)
            personaname = response["profile"]["personaname"]
            rank = constants.get_dota_rank_by_tier(response["rank_tier"])
            result += f"{personaname} is {rank} \n"

        await ctx.send(result)

    @commands.command(name='rank',help="<dota id> - Get rank of a player")
    async def get_player_rank(self,ctx: commands.Context,dota_id: int):
        from app.dependencies import get_dota_service
        dota_service = get_dota_service()
        response = await dota_service.get_player(dota_id)
        personaname = response["profile"]["personaname"]
        rank = constants.get_dota_rank_by_tier(response["rank_tier"])
        await ctx.send(f"{personaname} is {rank}")

    @commands.command(name='match',help="<match id> - Get match details")
    async def get_match_details(self,ctx: commands.Context,match_id: int):
        from app.dependencies import get_dota_service
        dota_service = get_dota_service()
        response = await dota_service.get_match(match_id)

        string = f"### Match ID: {response['match_id']} \n"
        i = 0
        for player in response["players"]:
            hero = constants.DOTAHEROESLIST.get(player["hero_id"]).localized_name
            persona = player["personaname"] if "personaname" in player else player["name"] if "name" in player else "Anonymous"
            rank_tier = constants.get_dota_rank_by_tier(player["rank_tier"]) if "rank_tier" in player else "Uncalibrated"
            won = player["win"] == 1
            string += f"{persona} ({hero}) is rank {rank_tier} \n"
            if i == 4:
                string += "\n"
            i += 1


        await ctx.send(string)

    @commands.command(name='item', help='"<item name>" - price check, profit/loss calculator, ROI calculator')
    async def get_osrs_item(self, ctx: commands.Context, item_id: str, limit: Optional[int]):
        from app.dependencies import get_osrs_service
        osrs_service = get_osrs_service()
        item = osrs_service.get_osrs_item_by_name(item_id)

        if limit is not None:
            item.limit = limit

        if item is None:
            await ctx.send(f"Item with name {item_id} not found.")
        else:
            volumes = await osrs_service.get_volumes()
            scaled_volumes = volumes.get_scaled_volumes()
            price = await osrs_service.get_latest_by_item_id(item.id)

            volume = volumes.get_volume(item.name)
            scaled_volume = scaled_volumes.get(item.name)


            result = self.flipping_calculator.calculate(item,price)
            url = "<https://oldschool.runescape.wiki/w/Exchange:" + item.name.replace(" ", "_") + ">"
            item.name = f"[{item.name}]({url})"
            string = self.format_item_details(result, item, volume)

            reply = await ctx.send(string)

            if result.roi_percentage > 0:
                await reply.add_reaction("💰")
            else:
                await reply.add_reaction("🤡")


    @commands.command(name='calc', help='<amount> <buy price> <sell price> - pure calculator')
    async def calculate_finished_transaction_roi(self,ctx: commands.Context,amount: int, buy: int, sell: int):
        if amount < 1:
            await ctx.send("Learn to buy items you idiot 🤡")
            return

        total_invested = buy * amount
        profit = ((sell * 0.99) - buy) * amount
        roi = (profit / total_invested) * 100 if total_invested > 0 else 0

        break_even_point = buy + (buy * 0.01)

        profit = math.floor(profit)
        break_even_point = math.ceil(break_even_point)

        string = ""
        if roi < 0:
            string += "### Dont quit your day job... \n"
        else:
            string += "### Stonks! \n"

        string += f"Total invested: {total_invested:,}gp \n"

        if profit < 0:
            string += f"Loss: **{profit:,}gp** \n"
        else:
            string += f"Profit: **{profit:,}gp** \n"

        string += f"ROI: **{roi:.2f}%** {self.get_emoji_by_roi(roi)} \n"
        string += f"Panicking? Break even sell price: {break_even_point:,}gp \n"

        await ctx.send(string)

    @commands.command(name='items')
    async def get_items(self,ctx: commands.Context, max_roi = 70):

        await ctx.send("This command is currently disabled")
        return


        from app.dependencies import get_osrs_service
        osrs_service = get_osrs_service()

        item_mappings = osrs_service.OSRS_ITEM_MAPPINGS
        prices = await osrs_service.get_latest()  # This should ideally be a LatestItemsResponse
        volumes = await osrs_service.get_volumes()
        scaled_volumes = volumes.get_scaled_volumes()

        # Check if prices is a LatestItemsResponse or dict, and extract data accordingly
        latest_data = prices.data if isinstance(prices, LatestItemsResponse) else prices.get("data", {})

        # Flatten volumes and add details from OsrsItem and LatestItemsResponse
        data = []
        for item_name, volume in scaled_volumes.items():
            # Find the matching OsrsItem based on the name
            osrs_item = next((item for item in item_mappings.values() if item.name == item_name), None)

            if osrs_item:
                # Find matching LatestItemEntry using the item id as a string
                latest_entry = latest_data.get(str(osrs_item.id), None)

                # Append all details to the data list
                data.append({
                    "item name": item_name,
                    "volume": volume,
                    "examine": osrs_item.examine,
                    "id": osrs_item.id,
                    "members": osrs_item.members,
                    "lowalch": osrs_item.lowalch,
                    "limit": osrs_item.limit,
                    "value": osrs_item.value,
                    "highalch": osrs_item.highalch,
                    "icon": osrs_item.icon,
                    "latest_high": latest_entry["high"] if latest_entry else None,
                    "latest_highTime": latest_entry["highTime"] if latest_entry else None,
                    "latest_low": latest_entry["low"] if latest_entry else None,
                    "latest_lowTime": latest_entry["lowTime"] if latest_entry else None,
                })

        # Create the DataFrame
        df = pd.DataFrame(data)
        filtered_df = df[(df["volume"] >= 0)]

        string = " Top 10 items sorted by ROI \n"

        items: List[DiscordFlippingResult] = []
        for index, row in filtered_df.iterrows():
            calc = self.flipping_calculator.calculate_v2(row["limit"], row["latest_high"], row["latest_low"],row["item name"])
            items.append(DiscordFlippingResult(
                item_name=calc.item_name,
                high_price=calc.high_price,
                low_price=calc.low_price,
                total_profit=calc.total_profit,
                roi_percentage=calc.roi_percentage,
                cash_needed=calc.cash_needed
            ))

        calc_data = [item.model_dump() for item in items]
        calc_df = pd.DataFrame(calc_data).sort_values(by="roi_percentage", ascending=False)

        filtered_df = calc_df[(calc_df["roi_percentage"] < max_roi) & (calc_df["total_profit"] > 200000)]

        strings = []
        # Header with column names and a separator
        strings.append("Item Name       |  Buy Price  |  Sell Price | Profit      | Cash Needed  | ROI")
        strings.append("--------------------------------------------------------------------------------")

        for i in range(len(filtered_df.head(20))):
            row = filtered_df.iloc[i]
            # Format each row with consistent padding for each column
            strings.append(
                f"{row.item_name[:15]:<15} | {row.low_price:>9,}gp | {row.high_price:>9,}gp | "
                f"{row.total_profit:>9,}gp | {row.cash_needed:>10,}gp | {math.floor(row.roi_percentage):>5.2f}%"
            )

        # Join the lines into a single string with monospaced formatting
        result_string = "```\n" + "\n".join(strings) + "\n```"

        # Check length and send the message
        if len(result_string) < 2000:
            await ctx.send(result_string)
        else:
            await ctx.send("The output is too long to send in a single message.")


    @commands.command(name='in', help='Register a buy transaction')
    async def incoming_trade(self,ctx: commands.Context, item_name: str, amount: int, buy: int):
        break_even = buy * 1.01
        total_invest = buy * amount

        string = f"Locked in {amount:,} {item_name} at {buy:,}gp each \n"
        string += f"Total investment: {total_invest:,}gp \n"
        string += f"Break even sell price: {math.ceil(break_even):,}gp \n"

        await ctx.send(string)

    @commands.command(name='out', help='Register a sell transaction')
    async def outgoing_trade(self,ctx: commands.Context, item_name: str, amount: int, sell: int):
        total_sale = sell * amount
        string = f"Sold {amount:,} {item_name} at {sell:,}gp each \n"
        string += f"Total sale: {total_sale:,}gp \n"

        await ctx.send(string)

    @commands.command(name='pos' , help='Check your current position (Items held, cash, total value)')
    async def trader_position(self,ctx: commands.Context):
        author = ctx.author
        string = "hi"
        await ctx.reply(string)

        pass



