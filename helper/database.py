import motor.motor_asyncio
from pymongo import ReturnDocument
from config import DATABASE_NAME, DATABASE_URI

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.settings_col = self.db["settings"]  # Dedicated collection for user settings

    # User upload type
    async def set_user_upload_type(self, user_id, upload_type):
        await self.settings_col.update_one(
            {"user_id": user_id},
            {"$set": {"upload_type": upload_type}},
            upsert=True
        )
        
    async def get_user_upload_type(self, user_id):
        user_settings = await self.settings_col.find_one({"user_id": user_id})
        return user_settings.get("upload_type", "document") if user_settings else "document"

    # Thumbnail management
    async def set_thumbnail(self, user_id, thumbnail_file_id):
        await self.settings_col.update_one(
            {"user_id": user_id},
            {"$set": {"thumbnail": thumbnail_file_id}},
            upsert=True
        )
        
    async def get_thumbnail(self, user_id):
        user_settings = await self.settings_col.find_one({"user_id": user_id})
        return user_settings.get("thumbnail", None) if user_settings else None

    # Prefix management
    async def set_user_prefix(self, user_id, prefix):
        await self.settings_col.update_one(
            {"user_id": user_id},
            {"$set": {"prefix": prefix}},
            upsert=True
        )

    async def get_user_prefix(self, user_id):
        user_settings = await self.settings_col.find_one({"user_id": user_id})
        return user_settings.get("prefix", "") if user_settings else ""

    # Sample video status
    async def set_sample_video_status(self, user_id, status):
        await self.settings_col.update_one(
            {"user_id": user_id},
            {"$set": {"sample_video": status}},
            upsert=True
        )
        
    async def get_sample_video_status(self, user_id):
        user_settings = await self.settings_col.find_one({"user_id": user_id})
        return user_settings.get("sample_video", False) if user_settings else False

    # Screenshot status
    async def set_screenshot_status(self, user_id, status):
        await self.settings_col.update_one(
            {"user_id": user_id},
            {"$set": {"screenshot": status}},
            upsert=True
        )
        
    async def get_screenshot_status(self, user_id):
        user_settings = await self.settings_col.find_one({"user_id": user_id})
        return user_settings.get("screenshot", False) if user_settings else False

    # Caption management
    async def set_user_caption(self, user_id, caption):
        await self.settings_col.update_one(
            {"user_id": user_id},
            {"$set": {"caption": caption}},
            upsert=True
        )

    async def get_user_caption(self, user_id):
        user_settings = await self.settings_col.find_one({"user_id": user_id})
        return user_settings.get("caption", "") if user_settings else ""

# Initialize the database instance
db = Database(DATABASE_URI, DATABASE_NAME)
