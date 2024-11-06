import math

from discord.ext import commands

from app.calculators.flipping_calculator import FlippingCalculator
from app.constants import constants
from app.utils.logger import logger
class CommandHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.flipping_calculator = FlippingCalculator()

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, *args, **kwargs):
        logger.error(f"Error in command {ctx}: {args} {kwargs}")

    @commands.command(name='ping', help='Responds with pong')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def ping(self, ctx: commands.Context):
        """Simple ping command to test bot responsiveness"""
        await ctx.send('pong')

    @commands.command(name='commands', help='List all available commands')
    async def get_commands(self, ctx: commands.Context):
        """List all available commands"""
        curr_commands = [f"{command.name}: {command.help}" for command in self.bot.commands]
        await ctx.send("Current commands are:\n" + "\n".join(f"!{cmd}" for cmd in curr_commands))

    @commands.command(name='ranks')
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def get_player_rank(self,ctx: commands.Context):
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

    @commands.command(name='item')
    async def get_osrs_item(self, ctx: commands.Context, item_id: str):
        from app.dependencies import get_osrs_service
        item = constants.get_osrs_item_by_name(item_id)

        if item is None:
            await ctx.send(f"Item with id {item_id} not found.")
        else:

            osrs_service = get_osrs_service()

            price = await osrs_service.get_latest_by_item_id(item.id)

            calc = self.flipping_calculator.calculate(item, price)

            emoji = "🟥" if calc.roi_percentage < 0 else "🟩"

            string = ""
            string += f"### **{item.name}** {emoji}\n"
            string += f"Low Price {calc.low_price:,}gp / High Price {calc.high_price:,}gp \n"
            string += f"Difference: {calc.price_diff:,}gp \n"
            string += f"Buy limit: {item.limit} *({calc.cash_needed:,}gp to exhaust)* \n"
            string += f"\n"
            string += f"Profit per item: **{calc.profit_per_item:,}gp** per item \n"
            string += f"Max Profit: **{calc.total_profit:,}gp** per buy limit (No tax: ||{calc.profit_no_tax:,}gp||) \n"
            string += f"ROI: **{calc.roi_percentage:.2f}%** \n"
            reply = await ctx.send(string)

            if calc.roi_percentage > 0:
                await reply.add_reaction("💰")
            else:
                await reply.add_reaction("🤡")


    @commands.command(name='calc')
    async def calculate_finished_transaction_roi(self,ctx: commands.Context,amount: int, buy: int, sell: int):
        total_invested = buy * amount
        profit = ((sell * 0.99) - buy) * amount
        roi = (profit / total_invested) * 100 if total_invested > 0 else 0

        break_even_point = buy + (buy * 0.01)

        profit = math.floor(profit)
        break_even_point = math.ceil(break_even_point)

        string = ""
        if roi < 0:
            string += "Dont quit your day job.. \n"
        else:
            string += "Stonks! \n"

        string += f"Total invested: {total_invested:,}gp \n"

        if profit < 0:
            string += f"Loss: {profit:,}gp \n"
        else:
            string += f"Profit: {profit:,}gp \n"

        string += f"ROI: {roi:.2f}% \n"
        string += f"Panicking? Break even sell price: {break_even_point:,}gp \n"

        await ctx.send(string)