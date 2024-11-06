import math

from discord.ext import commands

from app.constants import constants
from app.utils.logger import logger
class CommandHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

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
            item.highalch = price["data"][str(item.id)]["high"]
            item.lowalch = price["data"][str(item.id)]["low"]

            string = ""
            string += f"{item.name} - {item.examine} \n"
            string += f"Low Price {item.lowalch:,}gp / High Price {item.highalch:,}gp \n"
            string += f"Buy limit: {item.limit} \n"

            profit = ((item.highalch * 0.99) - item.lowalch) * item.limit
            profit_per = (item.highalch * 0.99) - item.lowalch

            total_cost = item.lowalch * item.limit
            roi = (profit / total_cost) * 100 if total_cost > 0 else 0
            roi_per = (profit_per / item.lowalch) * 100

            profit = math.floor(profit)
            profit_per = math.floor(profit_per)

            string += f"Profit per item: {profit_per:,}gp per item \n"
            string += f"Max Profit: {profit:,}gp per buy limit \n"
            string += f"ROI: {roi:.2f}% \n"
            string += f"ROI per item: {roi_per:.2f}% \n"
            await ctx.send(string)