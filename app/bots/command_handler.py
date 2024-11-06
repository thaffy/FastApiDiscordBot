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