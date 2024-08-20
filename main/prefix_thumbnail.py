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
    
    if query.data == "set_upload_document":
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



from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

@Client.on_message(filters.private & filters.command("settings"))
async def settings(bot, msg):
    user_id = msg.from_user.id

    # Fetch user settings from the database
    custom_thumbnail = await db.get_thumbnail(user_id)
    upload_type = await db.get_user_upload_type(user_id)
    prefix = await db.get_user_prefix(user_id)
    sample_video = await db.get_sample_video_status(user_id)
    screenshot = await db.get_screenshot_status(user_id)

    # Define status text
    thumbnail_status = "Exists" if custom_thumbnail else "Not Exists"
    prefix_status = prefix if prefix else "None"
    sample_video_status = "Enabled" if sample_video else "Disabled"
    screenshot_status = "Enabled" if screenshot else "Disabled"

    # Create settings message
    settings_text = f"""**Settings for {msg.from_user.first_name}**

Custom Thumbnail: **{thumbnail_status}**
Upload Type: **{upload_type.upper()}**
Prefix: **{prefix_status}**

Sample Video: **{sample_video_status}**
Screenshot: **{screenshot_status}**
"""

    # Create inline keyboard buttons
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Toggle Sample Video", callback_data="toggle_sample_video")],
        [InlineKeyboardButton("🔄 Toggle Screenshot", callback_data="toggle_screenshot")],
        [InlineKeyboardButton("📁 Change Upload Type", callback_data="change_upload_type")],
        [InlineKeyboardButton("📸 Set Custom Thumbnail", callback_data="set_thumbnail")],
        [InlineKeyboardButton("🔤 Set Prefix", callback_data="set_prefix")]
    ])

    await msg.reply_text(settings_text, reply_markup=keyboard)

@Client.on_callback_query(filters.regex("toggle_sample_video"))
async def toggle_sample_video(bot, callback_query):
    user_id = callback_query.from_user.id
    current_status = await db.get_sample_video_status(user_id)
    await db.update_sample_video_status(user_id, not current_status)
    await callback_query.answer("Sample Video toggled!")
    await settings(bot, callback_query.message)

@Client.on_callback_query(filters.regex("toggle_screenshot"))
async def toggle_screenshot(bot, callback_query):
    user_id = callback_query.from_user.id
    current_status = await db.get_screenshot_status(user_id)
    await db.update_screenshot_status(user_id, not current_status)
    await callback_query.answer("Screenshot toggled!")
    await settings(bot, callback_query.message)
