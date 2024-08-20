import aiohttp
import os
import time
from helper.database import db

async def gofile_upload(file_path, file_name, gofile_api_key):
    gofile_api_key = await db.get_gofile_api_key(user_id)

    if not gofile_api_key:
        return await msg.reply_text("Gofile API key is not set. Use /gofilesetup {your_api_key} to set it.")
        
    upload_url = "https://store1.gofile.io/uploadFile"

    try:
        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as file:
                form_data = aiohttp.FormData()
                form_data.add_field('file', file, filename=file_name)
                headers = {"Authorization": f"Bearer {gofile_api_key}"} if gofile_api_key else {}

                async with session.post(upload_url, headers=headers, data=form_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('status') == 'ok':
                            download_url = data.get('data', {}).get('downloadPage')
                            return download_url
                        else:
                            return f"GoFile upload failed: {data.get('message', 'Unknown error')}"
                    else:
                        return f"Error during GoFile upload: Status code {response.status}"
    except Exception as e:
        return f"Error during GoFile upload: {e}"
