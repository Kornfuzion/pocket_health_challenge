import os
import uuid

from dicom_to_png import convert_dcm_to_png
from flask import current_app
from typing import Optional, Set


class FileStorageService:
	"""
	Abstract away details regarding file paths, ID generation, I/O.

	Currently this uses the local file system, but it could be
	later augmented to make a request to an external distributed file system.
	"""
	DCM_EXTENSION: str = "dcm"
	PNG_EXTENSION: str = "png"
	ALLOWED_EXTENSIONS: Set[str] = {DCM_EXTENSION}

	@classmethod
	def get_unique_storage_handle(cls) -> str:
		"""
		Generate randomized/"unique" storage handles for a few reasons:

		1. Avoid collisions on common user-provided file names
		2. Avoid messy input validation on user-provided file names
		3. Our local file system is acting as a CDN; handles should not be guessable
		   to prevent scraping/ DDOS across all files in storage.

		This collision avoidance strategy is very much best effort, but probably suffices:
		"Only after generating 1 billion UUIDs every second for the next 100 years, 
		the probability of creating just one duplicate would be about 50%."

		TODO:

		1. Ideally, our file system detects collisions on write/
		   makes use of a specialized ID-generation service. Data loss is unacceptable.
		2. Access control on files to protect sensitive data
		"""
		return str(uuid.uuid4()).replace("-", "")

	@classmethod
	def get_png_storage_handle(cls, storage_handle: str) -> str:
		return f"{storage_handle}.{cls.PNG_EXTENSION}"

	@classmethod
	def get_dcm_storage_handle(cls, storage_handle: str) -> str:
		return f"{storage_handle}.{cls.DCM_EXTENSION}"

	@classmethod
	def get_dcm_storage_path(cls, storage_handle: str) -> str:
		return os.path.join(
			current_app.config["DICOM_FOLDER"],
			cls.get_dcm_storage_handle(storage_handle),
		)

	@classmethod
	def get_png_storage_path(cls, storage_handle: str) -> str:
		return os.path.join(
			current_app.config["IMAGE_FOLDER"],
			cls.get_png_storage_handle(storage_handle),
		)

	@classmethod
	def upload_file(cls, file: "FileStorage") -> str:
		storage_handle = cls.get_unique_storage_handle()
		storage_path = cls.get_dcm_storage_path(storage_handle)
		image_path = cls.get_png_storage_path(storage_handle)

		file.save(storage_path)
		image = convert_dcm_to_png(
			storage_path,
		)
		image.save(image_path)

		return storage_handle

	@classmethod
	def validate_file(cls, file: Optional["FileStorage"]) -> bool:
		return (
			file and 
			'.' in file.filename and
			file.filename.rsplit('.', 1)[1].lower() in cls.ALLOWED_EXTENSIONS
		)
