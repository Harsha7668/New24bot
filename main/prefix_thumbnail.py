from pyrogram import Client, filters
from helper.database import db
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MessageNotModified
from config import *
from pyrogram.types import Message

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

"""
@Client.on_message(filters.command("uploaddestinations") & filters.private)
async def upload_destinations(bot, msg):
    user_id = msg.from_user.id
    # Fetch current destination
    user_destination = await db.get_user_upload_destination(user_id)
    
    # Define buttons based on current preference
    telegram_button = InlineKeyboardButton(
        "Telegram ✅" if user_destination == "telegram" else "Telegram ❌",
        callback_data="set_destination_telegram"
    )
    gdrive_button = InlineKeyboardButton(
        "Google Drive ✅" if user_destination == "gdrive" else "Google Drive ❌",
        callback_data="set_destination_gdrive"
    )
    gofile_button = InlineKeyboardButton(
        "GoFile ✅" if user_destination == "gofile" else "GoFile ❌",
        callback_data="set_destination_gofile"
    )
    
    buttons = [[telegram_button], [gdrive_button], [gofile_button]]
    
    await msg.reply_text(
        "Select your upload destination:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query()
async def handle_upload_destinations_callback(bot, query):
    user_id = query.from_user.id
    
    if query.data == "set_destination_telegram":
        await db.set_user_upload_destination(user_id, "telegram")
        await query.answer("Upload destination set to Telegram.", show_alert=True)
        
    elif query.data == "set_destination_gdrive":
        await db.set_user_upload_destination(user_id, "gdrive")
        await query.answer("Upload destination set to Google Drive.", show_alert=True)

    elif query.data == "set_destination_gofile":
        await db.set_user_upload_destination(user_id, "gofile")
        await query.answer("Upload destination set to GoFile.", show_alert=True)
    
    # Update message with the new button state
    user_destination = await db.get_user_upload_destination(user_id)
    telegram_button = InlineKeyboardButton(
        "Telegram ✅" if user_destination == "telegram" else "Telegram ❌",
        callback_data="set_destination_telegram"
    )
    gdrive_button = InlineKeyboardButton(
        "Google Drive ✅" if user_destination == "gdrive" else "Google Drive ❌",
        callback_data="set_destination_gdrive"
    )
    gofile_button = InlineKeyboardButton(
        "GoFile ✅" if user_destination == "gofile" else "GoFile ❌",
        callback_data="set_destination_gofile"
    )
    
    buttons = [[telegram_button], [gdrive_button], [gofile_button]]
    
    # Only edit the message if there is a change
    current_text = query.message.text
    new_text = "Select your upload destination:"
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

"""
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MessageNotModified

@Client.on_message(filters.command("settings") & filters.private)
async def settings(bot, msg):
    user_id = msg.from_user.id

    # Retrieve user settings from the database
    thumbnail = await db.get_thumbnail(user_id)
    metadata = await db.get_metadata_titles(user_id)
    gofile_api_key = await db.get_gofile_api_key(user_id)
    prefix = await db.get_user_prefix(user_id)
    caption = await db.get_user_caption(user_id)

    # Create buttons for each setting
    view_thumbnail_button = InlineKeyboardButton(
        "View Thumbnail" if thumbnail else "Thumbnail ❌",
        callback_data="view_thumbnail"
    )
    view_metadata_button = InlineKeyboardButton(
        "View Metadata" if metadata else "Metadata ❌",
        callback_data="view_metadata"
    )
    view_gofile_api_key_button = InlineKeyboardButton(
        "View GoFile API Key" if gofile_api_key else "GoFile API Key ❌",
        callback_data="view_gofile_api_key"
    )
    view_prefix_button = InlineKeyboardButton(
        "View Prefix" if prefix else "Prefix ❌",
        callback_data="view_prefix"
    )
    view_caption_button = InlineKeyboardButton(
        "View Caption" if caption else "Caption ❌",
        callback_data="view_caption"
    )

    # Arrange buttons in a grid
    buttons = [
        [view_thumbnail_button],
        [view_metadata_button],
        [view_gofile_api_key_button],
        [view_prefix_button],
        [view_caption_button],
    ]

    await msg.reply_text(
        "Your Settings:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query()
async def handle_settings_callback(bot, query):
    user_id = query.from_user.id

    if query.data == "view_thumbnail":
        thumbnail = await db.get_thumbnail(user_id)
        if thumbnail:
            await bot.send_photo(query.message.chat.id, photo=thumbnail, caption="Here is your current thumbnail.")
        else:
            await query.answer("No thumbnail set.", show_alert=True)

    elif query.data == "view_metadata":
        metadata = await db.get_metadata_titles(user_id)
        if metadata:
            video_title, audio_title, subtitle_title = metadata
            metadata_text = f"**Video Title:** {titles.get('video_title', '')}\n**Audio Title:** {titles.get('audio_title', '')}\n**Subtitle Title:** {titles.get('subtitle_title', '')}"
            await query.message.edit_text(metadata_text)
        else:
            await query.answer("No metadata set.", show_alert=True)

    elif query.data == "view_gofile_api_key":
        gofile_api_key = await db.get_gofile_api_key(user_id)
        if gofile_api_key:
            await query.message.edit_text(f"**GoFile API Key:** {gofile_api_key}")
        else:
            await query.answer("No GoFile API key set.", show_alert=True)

    elif query.data == "view_prefix":
        prefix = await db.get_user_prefix(user_id)
        if prefix:
            await query.message.edit_text(f"**Prefix:** {prefix}")
        else:
            await query.answer("No prefix set.", show_alert=True)

    elif query.data == "view_caption":
        caption = await db.get_user_caption(user_id)
        if caption:
            await query.message.edit_text(f"**Caption Template:**\n{caption}")
        else:
            await query.answer("No caption template set.", show_alert=True)

    # Ensure buttons are updated after any action
    await update_settings_buttons(query)

async def update_settings_buttons(query):
    user_id = query.from_user.id

    # Re-fetch the settings to ensure buttons are updated correctly
    thumbnail = await db.get_thumbnail(user_id)
    metadata = await db.get_metadata_titles(user_id)
    gofile_api_key = await db.get_gofile_api_key(user_id)
    prefix = await db.get_user_prefix(user_id)
    caption = await db.get_user_caption(user_id)

    # Create buttons for each setting
    view_thumbnail_button = InlineKeyboardButton(
        "View Thumbnail" if thumbnail else "Thumbnail ❌",
        callback_data="view_thumbnail"
    )
    view_metadata_button = InlineKeyboardButton(
        "View Metadata" if metadata else "Metadata ❌",
        callback_data="view_metadata"
    )
    view_gofile_api_key_button = InlineKeyboardButton(
        "View GoFile API Key" if gofile_api_key else "GoFile API Key ❌",
        callback_data="view_gofile_api_key"
    )
    view_prefix_button = InlineKeyboardButton(
        "View Prefix" if prefix else "Prefix ❌",
        callback_data="view_prefix"
    )
    view_caption_button = InlineKeyboardButton(
        "View Caption" if caption else "Caption ❌",
        callback_data="view_caption"
    )

    buttons = [
        [view_thumbnail_button],
        [view_metadata_button],
        [view_gofile_api_key_button],
        [view_prefix_button],
        [view_caption_button],
    ]

    try:
        await query.message.edit_reply_markup(InlineKeyboardMarkup(buttons))
    except MessageNotModified:
        pass



@Client.on_message(filters.command("clear") & filters.user(ADMIN))
async def clear_database_handler(client: Client, msg: Message):
    try:
        await db.clear_database()
        await msg.reply_text("Database has been cleared✅.")
    except Exception as e:
        await msg.reply_text(f"An error occurred: {e}")


"""
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MessageNotModified

@Client.on_message(filters.command("settings") & filters.private)
async def settings(bot, msg):
    user_id = msg.from_user.id

    # Retrieve user settings from the database
    thumbnail = await db.get_thumbnail(user_id)
    metadata = await db.get_metadata_titles(user_id)
    gofile_api_key = await db.get_gofile_api_key(user_id)
    prefix = await db.get_user_prefix(user_id)
    caption = await db.get_user_caption(user_id)
    upload_type = await db.get_user_upload_type(user_id)
    upload_destination = await db.get_user_upload_destination(user_id)

    # Create buttons for each setting
    buttons = create_settings_buttons(thumbnail, metadata, gofile_api_key, prefix, caption, upload_type, upload_destination)
    
    await msg.reply_text(
        "Your Settings:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query()
async def handle_settings_callback(bot, query):
    user_id = query.from_user.id
    data = query.data

    if data == "view_thumbnail":
        thumbnail = await db.get_thumbnail(user_id)
        if thumbnail:
            await bot.send_photo(query.message.chat.id, photo=thumbnail, caption="Here is your current thumbnail.")
        else:
            await query.answer("No thumbnail set.", show_alert=True)
        await show_main_settings(query)

    elif data == "view_metadata":
        metadata = await db.get_metadata_titles(user_id)
        if metadata:
            video_title, audio_title, subtitle_title = metadata
            metadata_text = f"**Video Title:** {video_title}\n**Audio Title:** {audio_title}\n**Subtitle Title:** {subtitle_title}"
            await query.message.edit_text(
                metadata_text,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back_to_settings")]])
            )
        else:
            await query.answer("No metadata set.", show_alert=True)

    elif data == "view_gofile_api_key":
        gofile_api_key = await db.get_gofile_api_key(user_id)
        if gofile_api_key:
            await query.message.edit_text(
                f"**GoFile API Key:** {gofile_api_key}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back_to_settings")]])
            )
        else:
            await query.answer("No GoFile API key set.", show_alert=True)

    elif data == "view_prefix":
        prefix = await db.get_user_prefix(user_id)
        if prefix:
            await query.message.edit_text(
                f"**Prefix:** {prefix}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back_to_settings")]])
            )
        else:
            await query.answer("No prefix set.", show_alert=True)

    elif data == "view_caption":
        caption = await db.get_user_caption(user_id)
        if caption:
            await query.message.edit_text(
                f"**Caption Template:**\n{caption}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back_to_settings")]])
            )
        else:
            await query.answer("No caption template set.", show_alert=True)

    elif data == "view_upload_type":
        await query.message.edit_text(
            "Choose Upload Type:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Document", callback_data="set_upload_type_document")],
                [InlineKeyboardButton("Video", callback_data="set_upload_type_video")],
                [InlineKeyboardButton("Back", callback_data="back_to_settings")]
            ])
        )

    elif data == "view_upload_destination":
        await query.message.edit_text(
            "Choose Upload Destination:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Telegram", callback_data="set_upload_destination_telegram")],
                [InlineKeyboardButton("Google Drive", callback_data="set_upload_destination_gdrive")],
                [InlineKeyboardButton("GoFile", callback_data="set_upload_destination_gofile")],
                [InlineKeyboardButton("Back", callback_data="back_to_settings")]
            ])
        )

    elif data.startswith("set_upload_type_"):
        upload_type = data.split("_")[-1].capitalize()
        if upload_type in ["Document", "Video"]:
            await db.set_user_upload_type(user_id, upload_type)
            await query.answer(f"Upload Type set to {upload_type}.")
        else:
            await query.answer("Invalid upload type selected.", show_alert=True)
        await show_main_settings(query)

    elif data.startswith("set_upload_destination_"):
        upload_destination = data.split("_")[-1].lower()  # Changed to lowercase
        valid_destinations = ['telegram', 'gdrive', 'gofile']
        if upload_destination in valid_destinations:
            await db.set_user_upload_destination(user_id, upload_destination)
            await query.answer(f"Upload Destination set to {upload_destination.replace('_', ' ').title()}.")
        else:
            await query.answer("Invalid upload destination.", show_alert=True)
        await show_main_settings(query)

    elif data == "back_to_settings":
        await show_main_settings(query)

async def show_main_settings(query):
    user_id = query.from_user.id

    # Re-fetch the settings to ensure buttons are updated correctly
    thumbnail = await db.get_thumbnail(user_id)
    metadata = await db.get_metadata_titles(user_id)
    gofile_api_key = await db.get_gofile_api_key(user_id)
    prefix = await db.get_user_prefix(user_id)
    caption = await db.get_user_caption(user_id)
    upload_type = await db.get_user_upload_type(user_id)
    upload_destination = await db.get_user_upload_destination(user_id)

    # Create buttons for each setting
    buttons = create_settings_buttons(thumbnail, metadata, gofile_api_key, prefix, caption, upload_type, upload_destination)

    try:
        await query.message.edit_text(
            "Your Settings:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except MessageNotModified:
        # Content hasn't changed; no need to update the message
        pass

def create_settings_buttons(thumbnail, metadata, gofile_api_key, prefix, caption, upload_type, upload_destination):
    # Create buttons for each setting with ticks for selected options
    view_thumbnail_button = InlineKeyboardButton(
        "View Thumbnail" if thumbnail else "Thumbnail ❌",
        callback_data="view_thumbnail"
    )
    view_metadata_button = InlineKeyboardButton(
        "View Metadata" if metadata else "Metadata ❌",
        callback_data="view_metadata"
    )
    view_gofile_api_key_button = InlineKeyboardButton(
        "View GoFile API Key" if gofile_api_key else "GoFile API Key ❌",
        callback_data="view_gofile_api_key"
    )
    view_prefix_button = InlineKeyboardButton(
        "View Prefix" if prefix else "Prefix ❌",
        callback_data="view_prefix"
    )
    view_caption_button = InlineKeyboardButton(
        "View Caption" if caption else "Caption ❌",
        callback_data="view_caption"
    )
    view_upload_type_button = InlineKeyboardButton(
        f"Upload Type: {'Document' if upload_type == 'Document' else 'Video'} {'✅' if upload_type else ''}",
        callback_data="view_upload_type"
    )
    view_upload_destination_button = InlineKeyboardButton(
        f"Upload Destination: {upload_destination.replace('_', ' ').title() if upload_destination in ['telegram', 'gdrive', 'gofile'] else 'Not Set'} {'✅' if upload_destination else ''}",
        callback_data="view_upload_destination"
    )

    buttons = [
        [view_thumbnail_button],
        [view_metadata_button],
        [view_gofile_api_key_button],
        [view_prefix_button],
        [view_caption_button],
        [view_upload_type_button],
        [view_upload_destination_button],
    ]

    return buttons
"""
