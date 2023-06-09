import discord
from discord.ext import commands
import shutil
import os
import uuid
import functools
import subprocess
from dotenv import load_dotenv
from copy import deepcopy


load_dotenv()


DISCORD_TOKEN = deepcopy(os.getenv("BOT_TOKEN"))


bot = commands.Bot("!", intents=discord.Intents.all())


async def run_blocking(blocking_func, *args, **kwargs):
    """Runs a blocking function in a non-blocking way"""
    func = functools.partial(blocking_func, *args, **kwargs) # `run_in_executor` doesn't support kwargs, `functools.partial` does
    return await bot.loop.run_in_executor(None, func)


@bot.event
async def on_ready():
    print("Bot is ready")


@bot.command()
async def python(ctx: commands.Context):
    if ctx.message.reference is None:
        await ctx.send("You must reply to a Python code block!")
        return
    channel = bot.get_channel(ctx.message.reference.channel_id)
    msg = await channel.fetch_message(ctx.message.reference.message_id)
    txt = msg.content
    if not txt.startswith("```py") or not txt.endswith("```"):
        await ctx.send("The message you're replying to must be a Python code block!")
        return
    txt = txt[5:][:-3]
    bot_msg = None
    previous_line = None
    p = subprocess.Popen(["timeout", "120", "python", "-c", txt], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(p.stdout.readline, b""):
        if line.decode() not in ("\n", "") and bot_msg is None:
            bot_msg = await channel.send(line.decode())
            previous_line = deepcopy(line.decode())
        elif line not in ("\n", "") and bot_msg is not None:
            bot_msg = await bot_msg.edit(content=previous_line + line.decode())
            previous_line = deepcopy(previous_line + line.decode())


@bot.command()
async def manim(ctx: commands.Context, arg1, arg2):
    if ctx.message.reference is None:
        await ctx.send("You must reply to a Python code block!")
        return
    channel = bot.get_channel(ctx.message.reference.channel_id)
    msg = await channel.fetch_message(ctx.message.reference.message_id)
    txt = msg.content
    if not txt.startswith("```py") or not txt.endswith("```"):
        await ctx.send("The message you're replying to must be a Python code block!")
        return
    txt = txt[5:][:-3]
    filename = str(uuid.uuid4()) + ".py"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(txt)
    process = subprocess.Popen(["timeout", "120", "manim", filename, arg1, "-o", arg2], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(process.stdout.readline, b''):
        pass
    media_file = os.path.join("media", "videos", filename[:-3], "1080p60", arg2)
    if not os.path.exists(media_file):
        media_file = os.path.join("media", "images", filename[:-3], arg2)
    if os.path.exists(media_file):
        await ctx.send("Here is your Manim media file!", file=discord.File(media_file))
    else:
        await ctx.send("There was an error, please check your code!")
    os.remove(filename)
    shutil.rmtree("media")
    shutil.rmtree("__pycache__")


@bot.command()
async def matplotlib(ctx: commands.Context, arg):
    if ctx.message.reference is None:
        await ctx.send("You must reply to a Python code block!")
        return
    channel = bot.get_channel(ctx.message.reference.channel_id)
    msg = await channel.fetch_message(ctx.message.reference.message_id)
    txt = msg.content
    if not txt.startswith("```py") or not txt.endswith("```"):
        await ctx.send("The message you're replying to must be a Python code block!")
        return
    txt = txt[5:][:-3]
    filename = str(uuid.uuid4()) + ".py"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(txt)
    p = subprocess.Popen(["timeout", "120", "python", filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(p.stdout.readline, b""):
        pass
    if not os.path.exists(arg):
        await channel.send("There's not any file with that name!")
    else:
        await channel.send("Here is your Matplotlib figure!", file=discord.File(arg))
    os.remove(filename)
    os.remove(arg)


os.environ["BOT_TOKEN"] = ""
os.environ["OAUTH2_TOKEN"] = ""

with open(".env", "w") as f:
    f.write("Access denied!")

bot.run(DISCORD_TOKEN)