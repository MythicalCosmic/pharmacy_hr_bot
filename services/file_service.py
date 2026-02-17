
import os
import uuid
import aiofiles
from aiogram import Bot
from aiogram.types import PhotoSize

PHOTOS_DIR = "media/photos"
os.makedirs(PHOTOS_DIR, exist_ok=True)


class FileService:

    @staticmethod
    async def download_photo(bot: Bot, photo: PhotoSize, user_id: int) -> str | None:
        try:
            file = await bot.get_file(photo.file_id)
            ext = file.file_path.rsplit(".", 1)[-1] if "." in file.file_path else "jpg"
            filename = f"{user_id}_{uuid.uuid4().hex}.{ext}"
            filepath = os.path.join(PHOTOS_DIR, filename)

            file_bytes = await bot.download_file(file.file_path)

            async with aiofiles.open(filepath, "wb") as f:
                await f.write(file_bytes.read())

            return filepath

        except Exception as e:
            print(f"[FileService] download_photo failed: {e}")
            return None

    @staticmethod
    def delete_file(filepath: str) -> None:
        try:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"[FileService] delete_file failed: {e}")