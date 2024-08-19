import time, os, subprocess
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from main.utils import progress_message, humanbytes
from helper.ffmpeg import change_video_metadata
from helper.database import db


from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import os
import time

@Client.on_message(filters.command("rename") & filters.private & filters.reply)
async def rename_file(bot, msg):
    if len(msg.command) < 2:
        return await msg.reply_text("Please provide a new filename with the extension (e.g., .mkv, .mp4, .zip).")

    reply = msg.reply_to_message
    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a file, video, or audio with the new filename and extension (e.g., .mkv, .mp4, .zip).")

    new_name = msg.text.split(" ", 1)[1]

    # Add user-specific prefix
    prefix = await db.get_user_prefix(msg.from_user.id)
    if prefix:
        new_name = f"{prefix} - {new_name}"

    sts = await msg.reply_text("🚀 Downloading... ⚡")
    c_time = time.time()
    downloaded = await reply.download(file_name=new_name, progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    filesize = humanbytes(media.file_size)

    # Generate caption with metadata
    caption_template = await db.get_user_caption(msg.from_user.id)
    if caption_template:
        try:
            cap = caption_template.format(file_name=new_name, file_size=filesize)
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

    # Store file info temporarily for the next action (upload as document or video)
    await db.store_temp_file_info(msg.from_user.id, {
        "file_path": downloaded,
        "new_name": new_name,
        "caption": cap,
        "thumbnail": og_thumbnail,
        "file_size": os.path.getsize(downloaded),
    })

    # Show inline buttons for selecting upload type
    buttons = [
        [InlineKeyboardButton("📁 Upload as Document", callback_data="upload_document")],
        [InlineKeyboardButton("🎥 Upload as Video", callback_data="upload_video")]
    ]
    await sts.edit("Select your upload type:", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query()
async def handle_upload_callback(bot, query):
    user_id = query.from_user.id
    file_info = await db.get_temp_file_info(user_id)
    if not file_info:
        return await query.answer("No file information found. Please try again.", show_alert=True)

    file_path = file_info['file_path']
    new_name = file_info['new_name']
    caption = file_info['caption']
    thumbnail = file_info['thumbnail']

    if query.data == "upload_document":
        await query.message.edit_text("💠 Uploading as document... ⚡")
        try:
            await bot.send_document(query.message.chat.id, document=file_path, thumb=thumbnail, caption=caption, progress=progress_message, progress_args=("💠 Upload Started... ⚡", query.message, time.time()))
        except Exception as e:
            return await query.message.edit_text(f"Error: {e}")
    elif query.data == "upload_video":
        await query.message.edit_text("💠 Uploading as video... ⚡")
        try:
            await bot.send_video(query.message.chat.id, video=file_path, thumb=thumbnail, caption=caption, progress=progress_message, progress_args=("💠 Upload Started... ⚡", query.message, time.time()))
        except Exception as e:
            return await query.message.edit_text(f"Error: {e}")

    os.remove(file_path)
    await query.message.delete()
