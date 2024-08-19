import time, os, subprocess
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from main.utils import progress_message, humanbytes
from helper.ffmpeg import change_video_metadata
from helper.database import db
from pyrogram.types import Document, Video


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
            output_file = f"modified_{new_name}"  # Set output file name with prefix to avoid overwrite
            await safe_edit_message(sts, "💠 Changing metadata... ⚡")
            try:
                change_video_metadata(downloaded, video_title, audio_title, subtitle_title, output_file)
            except Exception as e:
                await safe_edit_message(sts, f"Error changing metadata: {e}")
                os.remove(downloaded)
                return

            # Upload the file
            try:
                await bot.send_document(msg.chat.id, document=output_file, thumb=og_thumbnail, caption=cap, progress=progress_message, progress_args=("💠 Upload Started... ⚡", sts, c_time))
            except Exception as e:
                return await sts.edit(f"Error: {e}")

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
            output_file = f"modified_{new_name}"  # Set output file name with prefix to avoid overwrite
            await safe_edit_message(sts, "💠 Changing metadata... ⚡")
            try:
                change_video_metadata(downloaded, video_title, audio_title, subtitle_title, output_file)
            except Exception as e:
                await safe_edit_message(sts, f"Error changing metadata: {e}")
                os.remove(downloaded)
                return

            # Upload the file
            try:
                await bot.send_video(msg.chat.id, video=output_file, thumb=og_thumbnail, caption=cap, progress=progress_message, progress_args=("💠 Upload Started... ⚡", sts, c_time))
            except Exception as e:
                return await sts.edit(f"Error: {e}")

            os.remove(downloaded)
            os.remove(output_file)
            await sts.delete()
        else:
            await msg.reply_text("Error: The file is not a video.")
