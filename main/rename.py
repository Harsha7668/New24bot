import time, os, subprocess
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from main.utils import progress_message, humanbytes
from helper.ffmpeg import change_video_metadata
from helper.database import db


@Client.on_message(filters.command("rename") & filters.private & filters.reply)
async def upload_file(client, message):
    reply_message = message.reply_to_message
    media = reply_message.document or reply_message.video or reply_message.audio

    if not media:
        return await message.reply_text("Please reply to a file, video, or audio that you want to upload.")

    # Prompt the user to enter a new filename using ForceReply
    await message.reply("Please enter the new filename (with or without extension):", reply_markup=ForceReply(selective=True))

@Client.on_message(filters.private & filters.reply)
async def refunc(client, message):
    reply_message = message.reply_to_message
    if (reply_message.reply_markup) and isinstance(reply_message.reply_markup, ForceReply):
        new_name = message.text

        # Retrieve user-specific prefix from the database
        prefix = await db.get_user_prefix(message.from_user.id)
        if prefix:
            new_name = f"{prefix} - {new_name}"

        await message.delete()  # Delete the user's filename message
        msg = await client.get_messages(message.chat.id, reply_message.id)
        file = msg.reply_to_message
        media = file.document or file.video or file.audio

        if not "." in new_name:
            if "." in media.file_name:
                extn = media.file_name.rsplit('.', 1)[-1]
            else:
                extn = "mkv"
            new_name = new_name + "." + extn
        await reply_message.delete()

        # Create inline buttons for selecting upload type
        buttons = [[InlineKeyboardButton("📁 Dᴏᴄᴜᴍᴇɴᴛ", callback_data="upload_document")]]
        if media.mime_type.startswith("video/"):
            buttons.append([InlineKeyboardButton("🎥 Vɪᴅᴇᴏ", callback_data="upload_video")])
        elif media.mime_type.startswith("audio/"):
            buttons.append([InlineKeyboardButton("🎵 Aᴜᴅɪᴏ", callback_data="upload_audio")])

        await message.reply(
            text=f"**Sᴇʟᴇᴄᴛ Tʜᴇ Oᴜᴛᴩᴜᴛ Fɪʟᴇ Tyᴩᴇ**\n**• Fɪʟᴇ Nᴀᴍᴇ :-** `{new_name}`",
            reply_to_message_id=file.id,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

@Client.on_callback_query()
async def handle_upload_callback(client, query):
    user_id = query.from_user.id
    msg = query.message
    file = msg.reply_to_message
    media = file.document or file.video or file.audio
    if not media:
        return await query.answer("No media found to upload.", show_alert=True)

    new_name = msg.text.split(":")[1].strip().strip("`")  # Extract filename from message text

    # Download the media file with the new name
    sts = await msg.edit_text("🚀 Downloading...")
    c_time = time.time()
    downloaded = await file.download(file_name=new_name, progress=progress_message, progress_args=("🚀 Downloading...", sts, c_time))

    # Get the user's caption from the database
    caption_template = await db.get_user_caption(user_id)
    filesize = humanbytes(media.file_size)
    caption = caption_template.format(filename=new_name, filesize=filesize) if caption_template else f"📕 Name ➠ : {new_name}\n\n🔗 Size ➠ : {filesize}"

    if query.data == "upload_video":
        await msg.edit_text("💠 Uploading as video... ⚡")
        await client.send_video(msg.chat.id, video=downloaded, caption=caption, progress=progress_message, progress_args=("💠 Upload Started... ⚡", msg, c_time))
    elif query.data == "upload_document":
        await msg.edit_text("💠 Uploading as document... ⚡")
        await client.send_document(msg.chat.id, document=downloaded, caption=caption, progress=progress_message, progress_args=("💠 Upload Started... ⚡", msg, c_time))
    elif query.data == "upload_audio":
        await msg.edit_text("💠 Uploading as audio... ⚡")
        await client.send_audio(msg.chat.id, audio=downloaded, caption=caption, progress=progress_message, progress_args=("💠 Upload Started... ⚡", msg, c_time))

    # Cleanup
    os.remove(downloaded)
    await msg.delete()
