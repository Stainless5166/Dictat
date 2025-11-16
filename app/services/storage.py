"""
File storage service for audio files using Docker volumes
"""

import os
import hashlib
import secrets
from datetime import datetime
from pathlib import Path
from typing import BinaryIO, AsyncGenerator, Optional
import aiofiles
import magic

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import FileUploadError

logger = get_logger(__name__)


class StorageService:
    """
    Service for managing audio file storage on Docker volumes

    Features:
    - Secure file upload with validation
    - Streaming with HTTP 206 range support
    - File integrity verification (SHA-256)
    - MIME type detection with magic bytes
    - Secure file deletion
    """

    def __init__(self):
        self.base_path = Path(settings.AUDIO_STORAGE_PATH)
        self.max_size = settings.MAX_UPLOAD_SIZE
        self.allowed_formats = settings.ALLOWED_AUDIO_FORMATS
        self.chunk_size = settings.CHUNK_SIZE

        # Ensure storage directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save_audio_file(
        self,
        file: BinaryIO,
        filename: str,
        user_id: int,
    ) -> dict:
        """
        Save uploaded audio file to Docker volume

        Args:
            file: File object to save
            filename: Original filename
            user_id: ID of user uploading file

        Returns:
            Dictionary with file metadata:
            - file_path: Relative path to file
            - file_name: Generated filename
            - file_size: Size in bytes
            - mime_type: Detected MIME type
            - file_hash: SHA-256 hash

        Raises:
            FileUploadError: If upload fails or validation fails
        """
        try:
            # Validate file format using magic bytes
            mime_type = self._validate_file_format(file)

            # Generate secure filename
            secure_filename = self._generate_secure_filename(filename, user_id)

            # Create user directory if not exists
            user_dir = self.base_path / str(user_id)
            user_dir.mkdir(parents=True, exist_ok=True)

            # Full file path
            file_path = user_dir / secure_filename
            relative_path = f"{user_id}/{secure_filename}"

            # Stream file to disk in chunks
            file_size = 0
            hasher = hashlib.sha256()

            async with aiofiles.open(file_path, "wb") as f:
                while True:
                    chunk = file.read(self.chunk_size)
                    if not chunk:
                        break

                    file_size += len(chunk)

                    # Check size limit
                    if file_size > self.max_size:
                        # Delete partial file
                        await aiofiles.os.remove(file_path)
                        raise FileUploadError(
                            f"File size exceeds maximum allowed size of "
                            f"{self.max_size / 1024 / 1024:.1f}MB"
                        )

                    await f.write(chunk)
                    hasher.update(chunk)

            file_hash = hasher.hexdigest()

            logger.info(
                f"File uploaded: user={user_id}, path={relative_path}, "
                f"size={file_size}, hash={file_hash[:16]}..."
            )

            return {
                "file_path": relative_path,
                "file_name": secure_filename,
                "file_size": file_size,
                "mime_type": mime_type,
                "file_hash": file_hash,
            }

        except FileUploadError:
            raise
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise FileUploadError(f"Failed to upload file: {str(e)}")

    async def stream_audio_file(
        self,
        file_path: str,
        start_byte: Optional[int] = None,
        end_byte: Optional[int] = None,
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream audio file with optional range support (HTTP 206)

        Args:
            file_path: Path to file relative to storage base
            start_byte: Optional start byte for range request
            end_byte: Optional end byte for range request

        Yields:
            Chunks of file data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If invalid range
        """
        full_path = self.base_path / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size = full_path.stat().st_size

        # Validate range parameters
        if start_byte is None:
            start_byte = 0
        if end_byte is None:
            end_byte = file_size - 1

        if start_byte < 0 or end_byte >= file_size or start_byte > end_byte:
            raise ValueError(f"Invalid byte range: {start_byte}-{end_byte}")

        bytes_to_read = end_byte - start_byte + 1

        logger.info(
            f"Streaming file: path={file_path}, range={start_byte}-{end_byte}, "
            f"size={bytes_to_read}"
        )

        # Stream file in chunks
        async with aiofiles.open(full_path, "rb") as f:
            await f.seek(start_byte)
            bytes_read = 0

            while bytes_read < bytes_to_read:
                chunk_size = min(self.chunk_size, bytes_to_read - bytes_read)
                chunk = await f.read(chunk_size)

                if not chunk:
                    break

                bytes_read += len(chunk)
                yield chunk

    async def delete_audio_file(self, file_path: str) -> None:
        """
        Delete audio file from storage

        Args:
            file_path: Path to file relative to storage base

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        full_path = self.base_path / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            # Delete file
            await aiofiles.os.remove(full_path)

            logger.info(f"File deleted: path={file_path}")

            # Try to remove empty user directory
            user_dir = full_path.parent
            try:
                user_dir.rmdir()  # Only removes if empty
            except OSError:
                pass  # Directory not empty, ignore

        except Exception as e:
            logger.error(f"File deletion failed: {e}")
            raise

    async def get_file_info(self, file_path: str) -> dict:
        """
        Get metadata about stored file

        Args:
            file_path: Path to file relative to storage base

        Returns:
            Dictionary with file info:
            - size: File size in bytes
            - mime_type: MIME type
            - last_modified: Last modification timestamp

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        full_path = self.base_path / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        stat = full_path.stat()

        # Detect MIME type
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(str(full_path))

        return {
            "size": stat.st_size,
            "mime_type": mime_type,
            "last_modified": datetime.fromtimestamp(stat.st_mtime),
        }

    def _generate_secure_filename(self, original_filename: str, user_id: int) -> str:
        """
        Generate secure, unique filename

        Args:
            original_filename: Original uploaded filename
            user_id: ID of user

        Returns:
            Secure filename

        Format: <timestamp>_<random>_<user_id>.<ext>
        """
        # Extract extension safely
        ext = Path(original_filename).suffix.lower()

        # Validate extension
        if ext.lstrip(".") not in self.allowed_formats:
            raise FileUploadError(
                f"File format not allowed. Allowed: {', '.join(self.allowed_formats)}"
            )

        # Generate secure filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        random_part = secrets.token_hex(8)
        secure_name = f"{timestamp}_{random_part}_u{user_id}{ext}"

        return secure_name

    def _validate_file_format(self, file: BinaryIO) -> str:
        """
        Validate file format using magic bytes (not file extension)

        Args:
            file: File object to validate

        Returns:
            Detected MIME type

        Raises:
            FileUploadError: If format not allowed
        """
        # Read first 2048 bytes for magic detection
        file.seek(0)
        header = file.read(2048)
        file.seek(0)  # Reset for actual reading

        # Detect MIME type using magic bytes
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(header)

        # Map MIME types to extensions
        mime_to_ext = {
            "audio/mpeg": "mp3",
            "audio/mp3": "mp3",
            "audio/wav": "wav",
            "audio/x-wav": "wav",
            "audio/wave": "wav",
            "audio/mp4": "m4a",
            "audio/x-m4a": "m4a",
            "audio/ogg": "ogg",
            "audio/x-ogg": "ogg",
            "audio/flac": "flac",
            "audio/x-flac": "flac",
        }

        detected_ext = mime_to_ext.get(mime_type)

        if detected_ext not in self.allowed_formats:
            raise FileUploadError(
                f"Invalid audio format detected: {mime_type}. "
                f"Allowed formats: {', '.join(self.allowed_formats)}"
            )

        logger.debug(f"File validated: mime_type={mime_type}, extension={detected_ext}")

        return mime_type


# Singleton storage service instance
storage_service = StorageService()
