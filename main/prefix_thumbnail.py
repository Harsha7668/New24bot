from pyrogram import Client, filters
from helper.database import db

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
    buttons = [
        [InlineKeyboardButton("✅ Upload as Document", callback_data="set_upload_document" if user_upload_type != "document" else "selected")],
        [InlineKeyboardButton("✅ Upload as Video", callback_data="set_upload_video" if user_upload_type != "video" else "selected")]
    ]
    
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
        
    elif query.data == "selected":
        await query.answer("Already selected.", show_alert=True)
    
    # Update message with the new button state
    user_upload_type = await db.get_user_upload_type(user_id)
    buttons = [
        [InlineKeyboardButton("✅ Upload as Document", callback_data="set_upload_document" if user_upload_type != "document" else "selected")],
        [InlineKeyboardButton("✅ Upload as Video", callback_data="set_upload_video" if user_upload_type != "video" else "selected")]
    ]
    await query.message.edit_text(
        "Select your upload type:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
