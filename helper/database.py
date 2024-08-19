import motor.motor_asyncio
from pymongo import ReturnDocument



class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.users_col = self.db["users"]
        self.photos_col = self.db['photos']  # Assuming you want to keep this collection

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
