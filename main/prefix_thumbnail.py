from pyrofork import Client, filters

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
