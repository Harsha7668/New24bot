from pyrogram import Client, filters
from helper.database import db
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MessageNotModified

@Client.on_message(filters.command("setthumbnail") & filters.private)
async def set_thumbnail(bot, msg):
    if msg.reply_to_message and msg.reply_to_message.photo:
        # Reply to a photo message
        thumbnail_file_id = msg.reply_to_message.photo.file_id
    elif len(msg.command) == 2:
        # Provide a file ID in the command
        thumbnail_file_id = msg.text.split(" ", 1)[1]
    else:
        return await msg.reply_text("Please reply to a photo or provide a file ID of the thumbnail.")

    # Save the thumbnail file ID in the database
    result = await db.set_thumbnail(msg.from_user.id, thumbnail_file_id)
    
    if result:
        await msg.reply_text("✅ Thumbnail set successfully!")
    else:
        await msg.reply_text("❌ Failed to set thumbnail. Please try again.")


 
@Client.on_message(filters.command("viewthumbnail") & filters.private)
async def view_thumbnail(bot, msg):
    # Retrieve the thumbnail file ID from the database
    thumbnail_file_id = await db.get_thumbnail(msg.from_user.id)
    
    if thumbnail_file_id:
        try:
            # Send the thumbnail image to the user
            await bot.send_photo(msg.chat.id, photo=thumbnail_file_id, caption="Here is your current thumbnail.")
        except Exception as e:
            await msg.reply_text(f"Error sending thumbnail: {e}")
    else:
        await msg.reply_text("You do not have a thumbnail set.")

@Client.on_message(filters.command("setcaption") & filters.private)
async def set_caption(bot, msg):
    if len(msg.command) < 2:
        return await msg.reply_text("Please provide a caption. Example: `/setcaption 📕 Name ➠ : {filename}\n\n🔗 Size ➠ : {filesize}\n\n⏰ Duration ➠ : {duration}`")

    caption_template = msg.text.split(" ", 1)[1]
    
    # Store the caption template in the database
    await db.set_user_caption(msg.from_user.id, caption_template)
    await msg.reply_text("✅ Caption template set successfully!")

@Client.on_message(filters.command("setprefix") & filters.private)
async def set_prefix(bot, msg):
    if len(msg.command) < 2:
        return await msg.reply_text("Please provide a prefix. Example: `/setprefix @yourprefix`")

    prefix = msg.text.split(" ", 1)[1]
    
    # Store the prefix in the database
    await db.set_user_prefix(msg.from_user.id, prefix)
    await msg.reply_text(f"✅ Prefix set to: {prefix}")

@Client.on_message(filters.private & filters.command("setmetadata"))
async def set_metadata_command(client, msg):
    if len(msg.command) < 2:
        await msg.reply_text("Invalid command format. Use: /setmetadata video_title | audio_title | subtitle_title")
        return
    
    titles = msg.text.split(" ", 1)[1].split(" | ")
    if len(titles) != 3:
        await msg.reply_text("Invalid number of titles. Use: /setmetadata video_title | audio_title | subtitle_title")
        return
    
    user_id = msg.from_user.id
    await db.save_metadata_titles(user_id, titles[0].strip(), titles[1].strip(), titles[2].strip())
    
    await msg.reply_text("Metadata titles set successfully ✅.")

"""
@Client.on_message(filters.command("uploadsettings") & filters.private)
async def upload_settings(bot, msg):
    user_id = msg.from_user.id
    # Fetch current preference
    user_upload_type = await db.get_user_upload_type(user_id)
    
    # Define buttons based on current preference
    document_button = InlineKeyboardButton(
        "📄 Upload as Document ✅" if user_upload_type == "document" else "📄 Upload as Document ❌",
        callback_data="set_upload_document"
    )
    video_button = InlineKeyboardButton(
        "📹 Upload as Video ✅" if user_upload_type == "video" else "📹 Upload as Video ❌",
        callback_data="set_upload_video"
    )
    
    buttons = [[document_button], [video_button]]
    
    await msg.reply_text(
        "Select your upload type:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query()
async def handle_upload_settings_callback(bot, query):
    user_id = query.from_user.id
    
    if query.data  "set_upload_document":
        await db.set_user_upload_type(user_id, "document")
        await query.answer("Upload type set to Document.", show_alert=True)
        
    elif query.data == "set_upload_video":
        await db.set_user_upload_type(user_id, "video")
        await query.answer("Upload type set to Video.", show_alert=True)
    
    # Update message with the new button state
    user_upload_type = await db.get_user_upload_type(user_id)
    document_button = InlineKeyboardButton(
        "📄 Upload as Document ✅" if user_upload_type == "document" else "📄 Upload as Document ❌",
        callback_data="set_upload_document"
    )
    video_button = InlineKeyboardButton(
        "📹 Upload as Video ✅" if user_upload_type == "video" else "📹 Upload as Video ❌",
        callback_data="set_upload_video"
    )
    
    buttons = [[document_button], [video_button]]
    
    # Only edit the message if there is a change
    current_text = query.message.text
    new_text = "Select your upload type:"
    current_markup = query.message.reply_markup
    new_markup = InlineKeyboardMarkup(buttons)
    
    if current_text != new_text or current_markup != new_markup:
        try:
            await query.message.edit_text(
                new_text,
                reply_markup=new_markup
            )
        except MessageNotModified:
            # Handle the case where the message content hasn't changed
            pass

"""

@Client.on_message(filters.private & filters.command("gdriveid"))
async def gdrive_id(bot, msg):
    user_id = msg.from_user.id
    command_parts = msg.text.split(" ", 1)
    
    if len(command_parts) < 2:
        return await msg.reply_text("Please provide your Google Drive folder ID. Usage: /gdriveid {your_folder_id}")
    
    gdrive_folder_id = command_parts[1].strip()
    
    # Save the Google Drive folder ID to the database
    await db.set_gdrive_folder_id(user_id, gdrive_folder_id)
    
    await msg.reply_text("Google Drive folder ID has been successfully set.")



@Client.on_message(filters.private & filters.command("gofilesetup"))
async def gofile_setup(bot, msg):
    user_id = msg.from_user.id
    command_parts = msg.text.split(" ", 1)
    
    if len(command_parts) < 2:
        return await msg.reply_text("Please provide your Gofile API key. Usage: /gofilesetup {your_api_key}")
    
    gofile_api_key = command_parts[1].strip()
    
    # Save the Gofile API key to the database
    await db.set_gofile_api_key(user_id, gofile_api_key)
    
    await msg.reply_text("Gofile API key has been successfully set.")


from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

@Client.on_message(filters.private & filters.command("uploaddestinations"))
async def upload_destinations(bot, msg):
    user_id = msg.from_user.id
    
    # Fetch current settings
    current_destination = await db.get_user_upload_destination(user_id)

    # Define buttons based on current settings
    telegram_button = InlineKeyboardButton(
        "📦 Upload to Telegram ✅" if current_destination == "telegram" else "📦 Upload to Telegram ❌",
        callback_data="set_upload_telegram"
    )
    gdrive_button = InlineKeyboardButton(
        "🌐 Upload to Google Drive ✅" if current_destination == "gdrive" else "🌐 Upload to Google Drive ❌",
        callback_data="set_upload_gdrive"
    )
    gofile_button = InlineKeyboardButton(
        "🔗 Upload to Gofile ✅" if current_destination == "gofile" else "🔗 Upload to Gofile ❌",
        callback_data="set_upload_gofile"
    )

    buttons = [
        [telegram_button, gdrive_button, gofile_button]
    ]
    
    await msg.reply_text(
        "Select your upload destinations:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query()
async def handle_callback(bot, query):
    user_id = query.from_user.id
    data = query.data.split("_")

    if len(data) < 3:
        return  # Invalid callback data

    action = data[0]
    setting = data[1]
    value = data[2]

    if action == "set":
        if setting == "upload":
            if value in ["telegram", "gdrive", "gofile"]:
                await db.set_user_upload_destination(user_id, value)
                await query.answer(f"Upload destination set to {value.capitalize()}.", show_alert=True)
        elif setting == "upload_type":
            if value in ["document", "video"]:
                await db.set_user_upload_type(user_id, value)
                await query.answer(f"Upload type set to {value.capitalize()}.", show_alert=True)

        # Update message with new button states
        await upload_destinations(bot, query.message)  # Update upload destinations
        await upload_settings(bot, query.message)  # Update upload type
