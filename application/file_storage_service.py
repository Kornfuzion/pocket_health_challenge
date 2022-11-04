import os
import uuid
from pydicom.errors import InvalidDicomError
from dicom_to_png import convert_dcm_to_png
from flask import current_app
from typing import Optional, Set
import pydicom
import io


class FileStorageService:
	"""
	Abstract away details regarding file paths, ID generation, I/O.

	Currently this uses the local file system, but it could be
	later augmented to make a request to an external distributed file system.
	"""
	DCM_EXTENSION: str = "dcm"
	PNG_EXTENSION: str = "png"

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
	def upload_dicom_file(
		cls, 
		storage_handle: str,
		file: Optional["werkzeug.FileStorage"], 
	) -> Optional[str]:
		dicom_path = cls.get_dcm_storage_path(storage_handle)
		file.save(dicom_path)

	@classmethod
	def upload_image_file(
		cls, 
		storage_handle: str,
		dicom_file: "pydicom.dataset.FileDataset",
	) -> Optional[str]:
		image_path = cls.get_png_storage_path(storage_handle)
		image = convert_dcm_to_png(
			dicom_file,
		)
		image.save(image_path)

	@classmethod
	def validate_dicom_file(
		cls, 
		file: Optional["werkzeug.FileStorage"]
	) -> Optional["pydicom.dataset.FileDataset"]:
		if not file:
			return None

		file_bytes = io.BytesIO(file.read())
		# File.read() advances the file cursor to the end of the file
		# Reset the cursor so this file can be saved to disk later
		file.seek(0)

		# We can't rely on the file extension, so load the file as DCM to validate
		try:
			return pydicom.dcmread(file_bytes)
		except InvalidDicomError:
			return None
