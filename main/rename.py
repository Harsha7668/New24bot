import time, os, subprocess
from pyrofork import Client, filters
from pyrofork.types import InlineKeyboardMarkup, InlineKeyboardButton
from main.utils import progress_message, humanbytes
from helper.ffmpeg import change_video_metadata

@Client.on_message(filters.command("rename") & filters.chat(GROUP))
async def rename_file(bot, msg):
    if len(msg.command) < 2 or not msg.reply_to_message:
        return await msg.reply_text("Please reply to a file, video, or audio with the new filename and extension (e.g., .mkv, .mp4, .zip).")

    reply = msg.reply_to_message
    media = reply.document or reply.audio or reply.video
    if not media:
        return await msg.reply_text("Please reply to a file, video, or audio with the new filename and extension (e.g., .mkv, .mp4, .zip).")

    new_name = msg.text.split(" ", 1)[1]
    
    # Retrieve user-specific prefix, caption template, and metadata from the database
    prefix = await db.get_user_prefix(msg.from_user.id)
    caption_template = await db.get_user_caption(msg.from_user.id)
    video_title, audio_title, subtitle_title = await db.get_metadata_titles(msg.from_user.id)

    if prefix:
        new_name = f"{prefix} - {new_name}"

    sts = await msg.reply_text("🚀 Downloading... ⚡")
    c_time = time.time()
    downloaded = await reply.download(file_name=new_name, progress=progress_message, progress_args=("🚀 Download Started... ⚡️", sts, c_time))
    filesize = humanbytes(media.file_size)

    if caption_template:
        caption = caption_template.format(
            filename=new_name,
            filesize=filesize,
            duration="N/A"  # Adjust if duration is available
        )
    else:
        caption = f"📕 Name ➠ : {new_name}\n\n🔗 Size ➠ : {filesize}\n\n⏰ Duration ➠ : N/A"

    # Apply metadata if titles are available
    if video_title or audio_title or subtitle_title:
        output_path = f"/path/to/output/{new_name}"  # Adjust the path as needed
        change_video_metadata(downloaded, video_title, audio_title, subtitle_title, output_path)
        downloaded = output_path

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

    # Create inline buttons for selecting upload type
    buttons = [
        [InlineKeyboardButton("Upload as Video", callback_data="upload_video"),
         InlineKeyboardButton("Upload as Document", callback_data="upload_document")]
    ]
    await sts.edit("Choose how to upload the file:", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query()
async def handle_upload_callback(bot, query):
    user_id = query.from_user.id
    msg = query.message
    reply = msg.reply_to_message
    media = reply.document or reply.video or reply.audio

    if not media:
        return await query.answer("No media found to upload.", show_alert=True)

    # Get the user's caption from the database
    caption_template = await db.get_user_caption(user_id)
    if caption_template:
        caption = caption_template.format(
            filename=media.file_name,
            filesize=humanbytes(media.file_size),
            duration="N/A"  # Adjust if duration is available
        )
    else:
        caption = f"📕 Name ➠ : {media.file_name}\n\n🔗 Size ➠ : {humanbytes(media.file_size)}\n\n⏰ Duration ➠ : N/A"

    await msg.edit_text("🚀 Processing your request...")

    c_time = time.time()
    downloaded = await reply.download(progress=progress_message, progress_args=("🚀 Downloading...", msg, c_time))
    
    if query.data == "upload_video":
        await msg.edit_text("💠 Uploading as video... ⚡")
        try:
            await bot.send_video(msg.chat.id, video=downloaded, caption=caption, thumb=og_thumbnail, progress=progress_message, progress_args=("💠 Upload Started... ⚡", msg, c_time))
        except Exception as e:
            return await msg.edit_text(f"Error: {e}")
    elif query.data == "upload_document":
        await msg.edit_text("💠 Uploading as document... ⚡")
        try:
            await bot.send_document(msg.chat.id, document=downloaded, caption=caption, thumb=og_thumbnail, progress=progress_message, progress_args=("💠 Upload Started... ⚡", msg, c_time))
        except Exception as e:
            return await msg.edit_text(f"Error: {e}")

    os.remove(downloaded)
    await msg.delete()
