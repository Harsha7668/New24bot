import time, os, subprocess
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from main.utils import progress_message, humanbytes
from helper.ffmpeg import change_video_metadata
from helper.database import db
from pyrogram.types import Document, Video
from googleapiclient.http import MediaFileUpload
from main.gdrive import upload_to_google_drive, drive_service
from main.gofile import gofile_upload
from googleapiclient.errors import HttpError

async def safe_edit_message(message, new_text):
    try:
        if message.text != new_text:
            await message.edit(new_text)
    except Exception as e:
        print(f"Failed to edit message: {e}")

"""
@Client.on_message(filters.private & filters.command("rename"))
async def rename_file(bot, msg):
    if len(msg.command) < 2 or not msg.reply_to_message:
        return await msg.reply_text("Please reply to a file, video, or audio with the new filename and extension (e.g., .mkv, .mp4, .zip).")

    reply = msg.reply_to_message
    media = reply.document or reply.audio or reply.video

    if not media:
        return await msg.reply_text("Please reply to a file, video, or audio with the new filename and extension (e.g., .mkv, .mp4, .zip).")

    new_name = msg.text.split(" ", 1)[1]

    # Add user-specific prefix
    prefix = await db.get_user_prefix(msg.from_user.id)
    if prefix:
        new_name = f"{prefix} - {new_name}"

    # Fetch user upload settings
    user_upload_type = await db.get_user_upload_type(msg.from_user.id)
    # Fetch user upload destination
    user_destination = await db.get_user_upload_destination(msg.from_user.id)

    # Define upload settings based on user preference
    if user_upload_type == "document":
        # Handle as document
        if reply.document or reply.video:
            sts = await msg.reply_text("🚀 Downloading... ⚡")
            c_time = time.time()
            downloaded = await reply.download(file_name=new_name, progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
            filesize = humanbytes(media.file_size)

            # Retrieve metadata titles
            metadata_titles = await db.get_metadata_titles(msg.from_user.id)
            video_title = metadata_titles.get('video_title', '')
            audio_title = metadata_titles.get('audio_title', '')
            subtitle_title = metadata_titles.get('subtitle_title', '')

            # Generate caption with metadata
            caption_template = await db.get_user_caption(msg.from_user.id)
            if caption_template:
                try:
                    cap = caption_template.format(
                        file_name=new_name,
                        file_size=filesize,
                        video_title=video_title,
                        audio_title=audio_title,
                        subtitle_title=subtitle_title
                    )
                except KeyError as e:
                    return await sts.edit(text=f"Caption error: unexpected keyword ({e})")
            else:
                cap = f"{new_name}\n\n🌟 Size: {filesize}"

            # Retrieve thumbnail from the database
            thumbnail_file_id = await db.get_thumbnail(msg.from_user.id)
            og_thumbnail = None
            if thumbnail_file_id:
                try:
                    og_thumbnail = await bot.download_media(thumbnail_file_id)
                except Exception:
                    pass
            else:
                if hasattr(media, 'thumbs') and media.thumbs:
                    try:
                        og_thumbnail = await bot.download_media(media.thumbs[0].file_id)
                    except Exception:
                        pass

            # Change document metadata if applicable
            output_file = f"{new_name}"  # Set output file name with prefix to avoid overwrite
            await safe_edit_message(sts, "💠 Changing metadata... ⚡")
            try:
                change_video_metadata(downloaded, video_title, audio_title, subtitle_title, output_file)
            except Exception as e:
                await safe_edit_message(sts, f"Error changing metadata: {e}")
                os.remove(downloaded)
                return

            # Upload the file based on user upload settings
            if user_destination == "telegram":
                try:
                    await bot.send_document(msg.chat.id, document=output_file, thumb=og_thumbnail, caption=cap, progress=progress_message, progress_args=("💠 Upload Started... ⚡", sts, c_time))
                except Exception as e:
                    return await sts.edit(f"Error: {e}")
            elif user_destination == "gdrive":
                try:
                    # Upload the file to Google Drive and get the file link
                    file_link = await upload_to_google_drive(output_file, new_name, sts)
                    
                    # Check if the file link is successfully obtained
                    if file_link:
                        # Reply with the file details including the Google Drive link
                        await msg.reply_text(
                            f"File uploaded to Google Drive!\n\n"
                            f"📁 **File Name:** {new_name}\n"
                            f"💾 **Size:** {filesize}\n"
                            f"🔗 **Link:** [View File]({file_link})"
                        )
                    else:
                        await msg.reply_text("Error: Unable to retrieve the Google Drive link.")
                except Exception as e:
                    await msg.reply_text(f"Error: {e}")
            elif user_destination == "gofile":
                 try:
                    gofile_api_key = await db.get_gofile_api_key(msg.from_user.id)
                    if not gofile_api_key:
                        return await msg.reply_text("Gofile API key is not set. Use /gofilesetup {your_api_key} to set it.")
                
                    upload_result = await gofile_upload(downloaded, new_name, gofile_api_key)
                    if "http" in upload_result:
                        await msg.reply_text(f"Upload successful!\nDownload link: {upload_result}")
                    else:
                        await msg.reply_text(upload_result)

                 except Exception as e:
                     await msg.reply_text(f"Error: {e}")

            os.remove(downloaded)
            os.remove(output_file)
            await sts.delete()

    elif user_upload_type == "video":
        # Handle as video
        if reply.document or reply.video:
            sts = await msg.reply_text("🚀 Downloading... ⚡")
            c_time = time.time()
            downloaded = await reply.download(file_name=new_name, progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
            filesize = humanbytes(media.file_size)

            # Retrieve metadata titles
            metadata_titles = await db.get_metadata_titles(msg.from_user.id)
            video_title = metadata_titles.get('video_title', '')
            audio_title = metadata_titles.get('audio_title', '')
            subtitle_title = metadata_titles.get('subtitle_title', '')

            # Generate caption with metadata
            caption_template = await db.get_user_caption(msg.from_user.id)
            if caption_template:
                try:
                    cap = caption_template.format(
                        file_name=new_name,
                        file_size=filesize,
                        video_title=video_title,
                        audio_title=audio_title,
                        subtitle_title=subtitle_title
                    )
                except KeyError as e:
                    return await sts.edit(text=f"Caption error: {e}")
            else:
                cap = f"{new_name}\n\n🌟 Size: {filesize}"

            # Retrieve thumbnail from the database
            thumbnail_file_id = await db.get_thumbnail(msg.from_user.id)
            og_thumbnail = None
            if thumbnail_file_id:
                try:
                    og_thumbnail = await bot.download_media(thumbnail_file_id)
                except Exception:
                    pass
            else:
                if hasattr(media, 'thumbs') and media.thumbs:
                    try:
                        og_thumbnail = await bot.download_media(media.thumbs[0].file_id)
                    except Exception:
                        pass

            # Change video metadata if applicable
            output_file = f"{new_name}"  # Set output file name with prefix to avoid overwrite
            await safe_edit_message(sts, "💠 Changing metadata... ⚡")
            try:
                change_video_metadata(downloaded, video_title, audio_title, subtitle_title, output_file)
            except Exception as e:
                await safe_edit_message(sts, f"Error changing metadata: {e}")
                os.remove(downloaded)
                return

            # Upload the file based on user upload settings
            if user_destination == "telegram":
                try:
                    await bot.send_video(msg.chat.id, video=output_file, thumb=og_thumbnail, caption=cap, progress=progress_message, progress_args=("💠 Upload Started... ⚡", sts, c_time))
                except Exception as e:
                    return await sts.edit(f"Error: {e}")
            elif user_destination == "gdrive":
                try:
                    # Upload the file to Google Drive and get the file link
                    file_link = await upload_to_google_drive(output_file, new_name, sts)
                    
                    # Check if the file link is successfully obtained
                    if file_link:
                        # Reply with the file details including the Google Drive link
                        await msg.reply_text(
                            f"File uploaded to Google Drive!\n\n"
                            f"📁 **File Name:** {new_name}\n"
                            f"💾 **Size:** {filesize}\n"
                            f"🔗 **Link:** [View File]({file_link})"
                        )
                    else:
                        await msg.reply_text("Error: Unable to retrieve the Google Drive link.")
                except Exception as e:
                    await msg.reply_text(f"Error: {e}")
            elif user_destination == "gofile":
                try:
                    gofile_api_key = await db.get_gofile_api_key(msg.from_user.id)
                    if not gofile_api_key:
                        return await msg.reply_text("Gofile API key is not set. Use /gofilesetup {your_api_key} to set it.")
                
                    upload_result = await gofile_upload(downloaded, new_name, gofile_api_key)
                    if "http" in upload_result:
                        await msg.reply_text(f"Upload successful!\nDownload link: {upload_result}")
                    else:
                        await msg.reply_text(upload_result)

                except Exception as e:
                    await msg.reply_text(f"Error: {e}")

                finally:
                    if os.path.exists(downloaded):
                        os.remove(downloaded)
                    if os.path.exists(output_file):
                        os.remove(output_file)
                    await sts.delete()
                
"""

"""
@Client.on_message(filters.private & filters.command("rename"))
async def rename_file(bot, msg):
    if len(msg.command) < 2 or not msg.reply_to_message:
        return await msg.reply_text("Please reply to a file, video, or audio with the new filename and extension (e.g., .mkv, .mp4, .zip).")

    reply = msg.reply_to_message
    media = reply.document or reply.audio or reply.video

    if not media:
        return await msg.reply_text("Please reply to a file, video, or audio with the new filename and extension (e.g., .mkv, .mp4, .zip).")

    new_name = msg.text.split(" ", 1)[1]

    prefix = await db.get_user_prefix(msg.from_user.id)
    if prefix:
        new_name = f"{prefix} - {new_name}"

    user_upload_type = await db.get_user_upload_type(msg.from_user.id)
    user_destination = await db.get_user_upload_destination(msg.from_user.id)

    if reply.document or reply.video:
        sts = await msg.reply_text("🚀 Downloading... ⚡")
        c_time = time.time()

        try:
            downloaded = await reply.download(file_name=new_name, progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
            filesize = humanbytes(media.file_size)

            metadata_titles = await db.get_metadata_titles(msg.from_user.id)
            video_title = metadata_titles.get('video_title', '')
            audio_title = metadata_titles.get('audio_title', '')
            subtitle_title = metadata_titles.get('subtitle_title', '')

            caption_template = await db.get_user_caption(msg.from_user.id)
            cap = caption_template.format(
                file_name=new_name,
                file_size=filesize,
                video_title=video_title,
                audio_title=audio_title,
                subtitle_title=subtitle_title
            ) if caption_template else f"{new_name}\n\n🌟 Size: {filesize}"

            thumbnail_file_id = await db.get_thumbnail(msg.from_user.id)
            og_thumbnail = None
            if thumbnail_file_id:
                try:
                    og_thumbnail = await bot.download_media(thumbnail_file_id)
                except Exception:
                    pass
            elif hasattr(media, 'thumbs') and media.thumbs:
                try:
                    og_thumbnail = await bot.download_media(media.thumbs[0].file_id)
                except Exception:
                    pass

            output_file = f"{new_name}"
            await safe_edit_message(sts, "💠 Changing metadata... ⚡")
            try:
                change_video_metadata(downloaded, video_title, audio_title, subtitle_title, output_file)
            except Exception as e:
                await safe_edit_message(sts, f"Error changing metadata: {e}")
                return

            if user_destination == "telegram":
                if user_upload_type == "document":
                    await bot.send_document(msg.chat.id, document=output_file, thumb=og_thumbnail, caption=cap, progress=progress_message, progress_args=("💠 Upload Started... ⚡", sts, c_time))
                elif user_upload_type == "video":
                    await bot.send_video(msg.chat.id, video=output_file, thumb=og_thumbnail, caption=cap, progress=progress_message, progress_args=("💠 Upload Started... ⚡", sts, c_time))
            elif user_destination == "gdrive":
                file_link = await upload_to_google_drive(output_file, new_name, sts)
                if file_link:
                    await msg.reply_text(f"File uploaded to Google Drive!\n\n📁 **File Name:** {new_name}\n💾 **Size:** {filesize}\n🔗 **Link:** [View File]({file_link})")
                else:
                    await msg.reply_text("Error: Unable to retrieve the Google Drive link.")
            elif user_destination == "gofile":
                gofile_api_key = await db.get_gofile_api_key(msg.from_user.id)
                if not gofile_api_key:
                    return await msg.reply_text("Gofile API key is not set. Use /gofilesetup {your_api_key} to set it.")
                upload_result = await gofile_upload(downloaded, new_name, gofile_api_key)
                if "http" in upload_result:
                    await msg.reply_text(f"Upload successful!\nDownload link: {upload_result}")
                else:
                    await msg.reply_text(upload_result)

        except Exception as e:
            await msg.reply_text(f"Error: {e}")
        finally:
            if os.path.exists(downloaded):
                os.remove(downloaded)
            if os.path.exists(output_file):
                os.remove(output_file)
            await sts.delete()
"""

import time, os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from main.utils import progress_message, humanbytes
from helper.ffmpeg import change_video_metadata
from helper.database import db
from googleapiclient.http import MediaFileUpload
from main.gdrive import upload_to_google_drive
from main.gofile import gofile_upload

async def safe_edit_message(message, new_text):
    try:
        if message.text != new_text:
            await message.edit(new_text)
    except Exception as e:
        print(f"Failed to edit message: {e}")

@Client.on_message(filters.private & filters.command("rename"))
async def rename_file(bot, msg):
    if len(msg.command) < 2 or not msg.reply_to_message:
        return await msg.reply_text("Please reply to a file, video, or audio with the new filename and extension (e.g., .mkv, .mp4, .zip).")

    reply = msg.reply_to_message
    media = reply.document or reply.audio or reply.video

    if not media:
        return await msg.reply_text("Please reply to a file, video, or audio with the new filename and extension (e.g., .mkv, .mp4, .zip).")

    new_name = msg.text.split(" ", 1)[1]

    # Add user-specific prefix
    prefix = await db.get_user_prefix(msg.from_user.id)
    if prefix:
        new_name = f"{prefix} - {new_name}"

    # Fetch user upload settings
    user_upload_type = await db.get_user_upload_type(msg.from_user.id)
    # Fetch user upload destination
    user_destination = await db.get_user_upload_destination(msg.from_user.id)

    sts = await msg.reply_text("🚀 Downloading... ⚡")
    c_time = time.time()
    downloaded = await reply.download(file_name=new_name, progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    filesize = humanbytes(media.file_size)

    # Retrieve metadata titles
    metadata_titles = await db.get_metadata_titles(msg.from_user.id)
    video_title = metadata_titles.get('video_title', '')
    audio_title = metadata_titles.get('audio_title', '')
    subtitle_title = metadata_titles.get('subtitle_title', '')

    # Generate caption with metadata
    caption_template = await db.get_user_caption(msg.from_user.id)
    if caption_template:
        try:
            cap = caption_template.format(
                file_name=new_name,
                file_size=filesize,
                video_title=video_title,
                audio_title=audio_title,
                subtitle_title=subtitle_title
            )
        except KeyError as e:
            return await sts.edit(text=f"Caption error: unexpected keyword ({e})")
    else:
        cap = f"{new_name}\n\n🌟 Size: {filesize}"

    # Retrieve thumbnail from the database
    thumbnail_file_id = await db.get_thumbnail(msg.from_user.id)
    og_thumbnail = None
    if thumbnail_file_id:
        try:
            og_thumbnail = await bot.download_media(thumbnail_file_id)
        except Exception:
            pass
    else:
        if hasattr(media, 'thumbs') and media.thumbs:
            try:
                og_thumbnail = await bot.download_media(media.thumbs[0].file_id)
            except Exception:
                pass

    # Change metadata if applicable
    output_file = f"{new_name}"  # Set output file name with prefix to avoid overwrite
    await safe_edit_message(sts, "💠 Changing metadata... ⚡")
    try:
        change_video_metadata(downloaded, video_title, audio_title, subtitle_title, output_file)
    except Exception as e:
        await safe_edit_message(sts, f"Error changing metadata: {e}")
        os.remove(downloaded)
        return

    # Upload the file based on user upload settings
    try:
        if user_destination == "telegram":
            if user_upload_type == "document":
                await bot.send_document(msg.chat.id, document=output_file, thumb=og_thumbnail, caption=cap, progress=progress_message, progress_args=("💠 Upload Started... ⚡", sts, c_time))
            elif user_upload_type == "video":
                await bot.send_video(msg.chat.id, video=output_file, thumb=og_thumbnail, caption=cap, progress=progress_message, progress_args=("💠 Upload Started... ⚡", sts, c_time))
        elif user_destination == "gdrive":
            file_link = await upload_to_google_drive(output_file, new_name, sts)
            if file_link:
                await msg.reply_text(
                    f"File uploaded to Google Drive!\n\n"
                    f"📁 **File Name:** {new_name}\n"
                    f"💾 **Size:** {filesize}\n"
                    f"🔗 **Link:** [View File]({file_link})"
                )
            else:
                await msg.reply_text("Error: Unable to retrieve the Google Drive link.")
        elif user_destination == "gofile":
            gofile_api_key = await db.get_gofile_api_key(msg.from_user.id)
            if not gofile_api_key:
                return await msg.reply_text("Gofile API key is not set. Use /gofilesetup {your_api_key} to set it.")
        
            upload_result = await gofile_upload(output_file, new_name, gofile_api_key)
            if "http" in upload_result:
                await msg.reply_text(f"Upload successful!\nDownload link: {upload_result}")
            else:
                await msg.reply_text(upload_result)
    except Exception as e:
        await msg.reply_text(f"Error: {e}")
    finally:
        os.remove(downloaded)
        os.remove(output_file)
        await sts.delete()
