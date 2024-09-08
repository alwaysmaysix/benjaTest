# manager.py
# copyright 2023 © YourName

import logging
from natsort import natsorted
from datetime import datetime
from asyncio import sleep
from concurrent.futures import ThreadPoolExecutor
from Test.Main.jpg4.main import download_images as download_jpg4
from Test.Main.cyberdrop.main import download_videos as download_cyberdrop
from Test.Main.saint2.main import download_videos as download_saint2
from Test.utility.helper import isTaskComplete, keyboard, sysINFO
from Test.utility.variables import BOT, Transfer, MSG, Messages, BotTimes

async def downloadManager(user_input, downloader_type):
    """
    Manages downloads for different types of sources.
    :param user_input: Dictionary of user inputs (e.g., URLs, directories).
    :param downloader_type: The type of downloader (jpg4, cyberdrop, saint2).
    """
    BotTimes.task_start = datetime.now()
    message = "\n<b>Please Wait...</b> ⏳\n<i>Processing...</i> 🐬"

    try:
        if downloader_type == "jpg4":
            # jpg4 specific inputs: start_url, end_url, page_range
            start_url = user_input['start_url']
            end_url = user_input['end_url']
            page_range = user_input['page_range']
            await download_jpg4(start_url, end_url, page_range)  # Pass inputs to the jpg4 downloader

        elif downloader_type == "cyberdrop":
            # cyberdrop specific inputs: urls, save_directory
            urls = user_input['urls']
            save_directory = user_input['save_directory']
            await download_cyberdrop(urls, save_directory)  # Pass inputs to the cyberdrop downloader

        elif downloader_type == "saint2":
            # saint2 specific inputs: embed_links, download_links, output_directory
            embed_links = user_input['embed_links']
            download_links = user_input['download_links']
            output_directory = user_input['output_directory']
            await download_saint2(embed_links, download_links, output_directory)  # Pass inputs to the saint2 downloader

    except Exception as e:
        logging.error(f"Error during download: {e}")
        return

    # Ensure that all tasks are completed
    while not isTaskComplete():
        await sleep(2)

async def calDownSize(sources, downloader_type):
    """
    Calculates total download size for given sources.
    :param sources: List of URLs or links.
    :param downloader_type: The type of downloader (jpg4, cyberdrop, saint2).
    """
    for link in natsorted(sources):
        try:
            if downloader_type == "jpg4":
                # Placeholder for calculating jpg4 size if needed
                Transfer.total_down_size += 0  # Replace with actual size logic if applicable
            elif downloader_type == "cyberdrop":
                # Placeholder for calculating cyberdrop size
                Transfer.total_down_size += 0  # Replace with actual size logic if applicable
            elif downloader_type == "saint2":
                # Placeholder for calculating saint2 size
                Transfer.total_down_size += 0  # Replace with actual size logic if applicable
        except Exception as e:
            logging.error(f"Error calculating size for {link}: {e}")
            await cancelTask(f"Size Calculation Error: {str(e)}")
            return

async def getDownloadName(link, downloader_type):
    """
    Determines the download name based on the link and downloader type.
    :param link: The URL or link.
    :param downloader_type: The type of downloader (jpg4, cyberdrop, saint2).
    """
    global Messages
    if len(BOT.Options.custom_name) != 0:
        Messages.download_name = BOT.Options.custom_name
        return

    if downloader_type == "jpg4":
        Messages.download_name = "JPG4_Images"
    elif downloader_type == "cyberdrop":
        Messages.download_name = "Cyberdrop_Videos"
    elif downloader_type == "saint2":
        Messages.download_name = "Saint2_Videos"
    else:
        Messages.download_name = "Unknown_Download"
