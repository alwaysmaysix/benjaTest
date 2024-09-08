import logging
import os
from PIL import Image
from asyncio import sleep
from os import path as ospath
from datetime import datetime
from pyrogram.errors import FloodWait
from uuid import uuid4
from Test.utility.variables import BOT, Transfer, BotTimes, Messages, MSG, Paths
from Test.utility.helper import sizeUnit, fileType, getTime, status_bar, thumbMaintainer, videoExtFix
from Test.Main.manager import downloadManager

async def progress_bar(current, total):
    global status_msg, status_head
    upload_speed = 4 * 1024 * 1024
    elapsed_time_seconds = (datetime.now() - BotTimes.task_start).seconds
    if current > 0 and elapsed_time_seconds > 0:
        upload_speed = current / elapsed_time_seconds
    eta = (Transfer.total_down_size - current - sum(Transfer.up_bytes)) / upload_speed
    percentage = (current + sum(Transfer.up_bytes)) / Transfer.total_down_size * 100
    await status_bar(
        down_msg=Messages.status_head,
        speed=f"{sizeUnit(upload_speed)}/s",
        percentage=percentage,
        eta=getTime(eta),
        done=sizeUnit(current + sum(Transfer.up_bytes)),
        left=sizeUnit(Transfer.total_down_size),
        engine="Pyrogram 💥",
    )

async def upload_file(file_path, real_name):
    global Transfer, MSG
    BotTimes.task_start = datetime.now()

    # Generate a unique name by appending a UUID
    unique_name = f"{uuid4()}_{real_name}"

    caption = f"<{BOT.Options.caption}>{BOT.Setting.prefix} {unique_name} {BOT.Setting.suffix}</{BOT.Options.caption}>"
    type_ = fileType(file_path)
    f_type = type_ if BOT.Options.stream_upload else "document"

    try:
        if f_type == "video":
            if not BOT.Options.stream_upload:
                file_path = videoExtFix(file_path)
            thmb_path, seconds = thumbMaintainer(file_path)
            with Image.open(thmb_path) as img:
                width, height = img.size

            MSG.sent_msg = await MSG.sent_msg.reply_video(
                video=file_path,
                supports_streaming=True,
                width=width,
                height=height,
                caption=caption,
                thumb=thmb_path,
                duration=int(seconds),
                progress=progress_bar,
                reply_to_message_id=MSG.sent_msg.id,
            )

        elif f_type == "audio":
            thmb_path = None if not ospath.exists(Paths.THMB_PATH) else Paths.THMB_PATH
            MSG.sent_msg = await MSG.sent_msg.reply_audio(
                audio=file_path,
                caption=caption,
                thumb=thmb_path,  # type: ignore
                progress=progress_bar,
                reply_to_message_id=MSG.sent_msg.id,
            )

        elif f_type == "document":
            if ospath.exists(Paths.THMB_PATH):
                thmb_path = Paths.THMB_PATH
            elif type_ == "video":
                thmb_path, _ = thumbMaintainer(file_path)
            else:
                thmb_path = None

            MSG.sent_msg = await MSG.sent_msg.reply_document(
                document=file_path,
                caption=caption,
                thumb=thmb_path,  # type: ignore
                progress=progress_bar,
                reply_to_message_id=MSG.sent_msg.id,
            )

        elif f_type == "photo":
            MSG.sent_msg = await MSG.sent_msg.reply_photo(
                photo=file_path,
                caption=caption,
                progress=progress_bar,
                reply_to_message_id=MSG.sent_msg.id,
            )

        Transfer.sent_file.append(MSG.sent_msg)
        Transfer.sent_file_names.append(unique_name)

    except FloodWait as e:
        await sleep(e.x)  # Wait for the specified time before retrying
        await upload_file(file_path, real_name)
    except Exception as e:
        logging.error(f"Error when uploading: {e}")

# Function to initiate uploading files from specific directories
async def upload_from_directory(directory, downloader_type):
    if not os.path.exists(directory):
        logging.error(f"Directory {directory} does not exist!")
        return

    # List files from the specified download directory
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            logging.info(f"Uploading file: {file_path}")
            await upload_file(file_path, file)

# Edit the function to manage uploads from jpg4, cyberdrop, or saint2
@app.on_message(filters.command("upload") & filters.private)
async def handle_upload(client, message):
    downloader_type = message.text.split()[1]  # Assumes command in the form `/upload <downloader_type>`

    # Map downloader types to respective download directories
    if downloader_type == "jpg4":
        download_directory = "/path/to/jpg4/downloads"
    elif downloader_type == "cyberdrop":
        download_directory = "/path/to/cyberdrop/downloads"
    elif downloader_type == "saint2":
        download_directory = "/path/to/saint2/downloads"
    else:
        await message.reply_text("Invalid downloader type. Please choose jpg4, cyberdrop, or saint2.")
        return

    await message.reply_text(f"Uploading files from {downloader_type} directory...")
    await upload_from_directory(download_directory, downloader_type)
    await message.reply_text("Upload completed!")
