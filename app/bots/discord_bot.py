from datetime import datetime

from discord import Message
from discord.ext import commands
from discord.ext.commands import Context

from app.config import settings
from app.constants import constants
from app.utils.logger import logger

intents = settings.DISCORD_INTENTS
intents.members = True
intents.message_content = True
bot = commands.Bot(
    command_prefix=settings.DISCORD_COMMAND_PREFIX,
    intents=intents)

# Cooldown duration
LLM_LAST_MESSAGE_SENT = None

@bot.event
async def on_connect():
    logger.info(f"Connected to Discord with appid {bot.application.id}")

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")

@bot.event
async def on_message(message : Message):
    global LLM_LAST_MESSAGE_SENT
    if message.author == bot.user:
        return
    logger.info(f"{message.guild.name}/#{message.channel.name.lower()}: {message.author}: {message.content}")

    if message.content is not None and message.content.strip().startswith(settings.DISCORD_COMMAND_PREFIX):
        await bot.process_commands(message) ## This is required to process commands
        return



    predefined_response = constants.get_predefined_response(message.content)
    if predefined_response:
        await message.channel.send(predefined_response)
        return

    ### LLM Reponse Logic beyond this point ###
    if message.channel.name.lower() != "deltabotshome":
        return

    now = datetime.now()

    # Check if we are within the cooldown period
    if LLM_LAST_MESSAGE_SENT and now - LLM_LAST_MESSAGE_SENT < settings.LLM_COOLDOWN_DURATION:
        logger.info("LLM is on cooldown...")
        return


    from app.dependencies import get_gemini_service

    if message.content is not None and message.content.strip().endswith('?'):
        prompt = "Write a summarized, intelligent answer to this question (FEWER THAN 2000 CHARACTERS IN LENGTH!)"
    else:
        prompt = "Reply in 1-3 sentences to the following text:"


    llm = get_gemini_service()
    try:
        resp = await llm.generate(f"{prompt}: {message.content}")
    except Exception as e:
        logger.error(f"Error generating LLM response: {e}")
        return
    LLM_LAST_MESSAGE_SENT = now
    if resp != "Please provide me with the question you'd like me to answer. I need the question to understand what you're asking and provide a summarized, intelligent response.":
        await message.channel.send(resp)


@bot.event
async def on_command_error(ctx: Context, *args, **kwargs):
    logger.error(f"Error in event {ctx}: {args} {kwargs}")

@bot.command(name='ping', help='Responds with pong')
@commands.cooldown(1, 30, commands.BucketType.user)
async def ping(ctx : Context):
    await ctx.send('pong')

@bot.command(name='commands',help='List all available commands')
async def get_commands(ctx: Context):
    curr_commands = [f"{command.name}: {command.help}" for command in bot.commands]
    await ctx.send("Current commands are:\n" + "\n".join(f"!{cmd}" for cmd in curr_commands))

@bot.command(name='ranks')
async def get_player_rank(ctx: Context):
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

@bot.command(name='planked')
async def player_planked(ctx: Context, name: str):
    from app.dependencies import get_gemini_service
    llm = get_gemini_service()
    resp = await llm.generate(f"Write a rude and witty reponse to {name} planking. (planking in this context means dying in Runescape. Keep it to 1-3 sentences, NEVER exceed 2000 characters)")

    await ctx.send(f"{name} just planked. {resp}")

@bot.command(name='brainrot')
async def brainrot_video(ctx: Context):
    await ctx.send("https://www.youtube.com/watch?v=sVn4sBxLokA&t=114s")




