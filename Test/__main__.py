# _main_.py

import logging, os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from Test.Main.manager import downloadManager
from Test.utility.variables import BOT, MSG, Messages, BotTimes
from Test.asyncio import get_event_loop

app = Client("download_bot")

# Dictionary to store user input temporarily
user_input = {}
downloader_type = None

# Start command
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Repository", url="https://github.com/YourRepo")],
            [InlineKeyboardButton("Support", url="https://t.me/YourSupport")],
        ]
    )
    await message.reply_text("Hello! I can help you download from various sources.", reply_markup=keyboard)

# Download command to select download type
@app.on_message(filters.command("download") & filters.private)
async def download(client, message):
    global downloader_type
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("JPG4", callback_data="jpg4")],
            [InlineKeyboardButton("Cyberdrop", callback_data="cyberdrop")],
            [InlineKeyboardButton("Saint2", callback_data="saint2")],
        ]
    )
    await message.reply_text("Choose the download type:", reply_markup=keyboard)

# Handle download type selection
@app.on_callback_query()
async def handle_options(client, callback_query):
    global downloader_type
    downloader_type = callback_query.data  # Set the downloader type based on user's choice
    await callback_query.message.delete()

    if downloader_type == "jpg4":
        await callback_query.message.reply_text("Please enter the starting URL for JPG4:")
    elif downloader_type == "cyberdrop":
        await callback_query.message.reply_text("Please enter the Cyberdrop URLs (comma-separated):")
    elif downloader_type == "saint2":
        await callback_query.message.reply_text("Please enter the Saint2 embed links (comma-separated):")

# Handle text inputs for different steps
@app.on_message(filters.text & filters.private)
async def handle_input(client, message):
    global user_input, downloader_type

    # Based on the current step, collect the relevant input
    if downloader_type == "jpg4":
        if "start_url" not in user_input:
            user_input["start_url"] = message.text
            await message.reply_text("Please enter the ending URL for JPG4:")
        elif "end_url" not in user_input:
            user_input["end_url"] = message.text
            await message.reply_text("Please enter the page range (e.g., 1-5):")
        elif "page_range" not in user_input:
            user_input["page_range"] = message.text
            # Start the download
            await downloadManager(user_input, downloader_type)
            user_input.clear()  # Reset input after task

    elif downloader_type == "cyberdrop":
        if "urls" not in user_input:
            user_input["urls"] = message.text.split(',')
            await message.reply_text("Please enter the directory to save the videos:")
        elif "save_directory" not in user_input:
            user_input["save_directory"] = message.text
            # Start the download
            await downloadManager(user_input, downloader_type)
            user_input.clear()

    elif downloader_type == "saint2":
        if "embed_links" not in user_input:
            user_input["embed_links"] = message.text.split(',')
            await message.reply_text("Please enter the Saint2 download links (comma-separated):")
        elif "download_links" not in user_input:
            user_input["download_links"] = message.text.split(',')
            await message.reply_text("Please enter the directory to save the downloads:")
        elif "output_directory" not in user_input:
            user_input["output_directory"] = message.text
            # Start the download
            await downloadManager(user_input, downloader_type)
            user_input.clear()


# Handling button clicks for download types
@app.on_callback_query()
async def handle_options(client, callback_query):
    download_type = callback_query.data
    await callback_query.message.delete()

    # Start the download process based on the selected type
    await callback_query.message.reply_text(f"Starting download with {download_type} downloader...")
    BOT.State.task_going = True
    event_loop = get_event_loop()
    event_loop.create_task(downloadManager(BOT.SOURCE, download_type))
    BOT.State.task_going = False

logging.info("Bot is running...")
app.run()
