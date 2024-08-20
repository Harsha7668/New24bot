
from pymongo import ReturnDocument
from config import DATABASE_NAME, DATABASE_URI
import motor.motor_asyncio

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.users_col = self.db["users"]
        self.photos_col = self.db['photos']
        self.upload_destinations_col = self.db['uploaddestinations']
        self.gofile_col = self.db['gofile']
        self.gdrive_col = self.db['gdrive']

    async def get_user_upload_destination(self, user_id):
        # Fetch user settings from the database
        user_settings = await self.upload_destinations_col.find_one({"user_id": user_id})
        if user_settings:
            return user_settings.get("upload_destination", "telegram")  # Default to "telegram" if not set
        return "telegram"  # Default to "telegram" if user settings not found

    async def set_user_upload_destination(self, user_id, destination):
        # Validate the destination value
        if destination not in ["telegram", "gdrive", "gofile"]:
            raise ValueError("Invalid upload destination")

        # Update user settings in the database
        result = await self.upload_destinations_col.update_one(
            {"user_id": user_id},
            {"$set": {"upload_destination": destination}},
            upsert=True  # Create a new document if none exists
        )
        return result.modified_count > 0 or result.upserted_id is not None


    async def set_gofile_api_key(self, user_id, api_key):
        """Store the Gofile API key for a user."""
        await self.gofile_col.update_one(
            {"user_id": user_id},
            {"$set": {"api_key": api_key}},
            upsert=True
        )

    async def get_gofile_api_key(self, user_id):
        """Retrieve the Gofile API key for a user."""
        doc = await self.gofile_col.find_one({"user_id": user_id})
        return doc.get("api_key") if doc else None
            
        
    async def set_gdrive_folder_id(self, user_id, folder_id):
        """Store the Google Drive folder ID for a user."""
        await self.gdrive_col.update_one(
            {"user_id": user_id},
            {"$set": {"folder_id": folder_id}},
            upsert=True
        )

    
    async def get_gdrive_folder_id(self, user_id):
        """Retrieve the Google Drive folder ID for a user."""
        doc = await self.gdrive_col.find_one({"user_id": user_id})
        return doc.get("folder_id") if doc else None
        
    async def set_user_upload_type(self, user_id, upload_type):
        await self.users_col.update_one(
            {"user_id": user_id},
            {"$set": {"upload_type": upload_type}},
            upsert=True
        )

    async def get_user_upload_type(self, user_id):
        user = await self.users_col.find_one({"user_id": user_id})
        return user.get("upload_type", "document")  # Default to "document"

    
    async def save_metadata_titles(self, user_id, video_title, audio_title, subtitle_title):
        """Saves metadata titles for video, audio, and subtitles."""
        result = await self.users_col.find_one_and_update(
            {'_id': user_id},
            {'$set': {
                'video_title': video_title,
                'audio_title': audio_title,
                'subtitle_title': subtitle_title
            }},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        return result

    async def get_metadata_titles(self, user_id):
        """Retrieves metadata titles for video, audio, and subtitles."""
        user_data = await self.users_col.find_one({'_id': user_id})
        if user_data:
            return {
                'video_title': user_data.get('video_title', ''),
                'audio_title': user_data.get('audio_title', ''),
                'subtitle_title': user_data.get('subtitle_title', '')
            }




    async def set_user_prefix(self, user_id, prefix):
        """Sets the prefix for a user."""
        result = await self.users_col.find_one_and_update(
            {'_id': user_id},
            {'$set': {'prefix': prefix}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        return result

    async def get_user_prefix(self, user_id):
        """Gets the prefix for a user."""
        user = await self.users_col.find_one({'_id': user_id})
        return user.get('prefix', '') if user else ''

    async def set_user_caption(self, user_id, caption):
        """Sets the caption template for a user."""
        result = await self.users_col.find_one_and_update(
            {'_id': user_id},
            {'$set': {'caption': caption}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        return result

    async def get_user_caption(self, user_id):
        """Gets the caption template for a user."""
        user = await self.users_col.find_one({'_id': user_id})
        return user.get('caption', '') if user else ''

    async def set_thumbnail(self, user_id, thumbnail_file_id):
        """Sets the thumbnail file ID for a user."""
        result = await self.users_col.find_one_and_update(
            {'_id': user_id},
            {'$set': {'thumbnail': thumbnail_file_id}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        return result

    async def get_thumbnail(self, user_id):
        """Gets the thumbnail file ID for a user."""
        user = await self.users_col.find_one({'_id': user_id})
        return user.get('thumbnail', '') if user else ''

    async def clear_database(self):
        # Drop all collections
        await self.users_col.drop()
        await self.photos_col.drop()
        await self.upload_destinations_col.drop()
        await self.gofile_col.drop()
        await self.gdrive_col.drop()
              
# Initialize the database instance
db = Database(DATABASE_URI, DATABASE_NAME)    
