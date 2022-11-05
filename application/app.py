import json
import os

from dicom_attribute_extractor import DicomAttributeExtractor
from flask import Flask, request, send_from_directory
from file_storage_service import FileStorageService
from werkzeug.wrappers import Response


app = Flask(__name__)
app.config["DICOM_FOLDER"] = os.path.abspath("../uploads/DCM")
app.config["IMAGE_FOLDER"] = os.path.abspath("../uploads/PNG")


@app.route("/upload_file", methods=["GET", "POST"])
def upload_file() -> Response:
    if request.method == "POST":
        file = request.files.get("file")
        dicom_file = FileStorageService.get_dicom_file(file)

        if not dicom_file:
            return "Invalid File.", 400

        storage_handle = FileStorageService.get_unique_storage_handle()
        # TODO: Make these atomic so that either both uploads succeed, 
        #       or partially uploaded files are deleted
        FileStorageService.upload_dicom_file(storage_handle, file)
        FileStorageService.upload_image_file(storage_handle, dicom_file)

        return {"storage_handle": storage_handle}, 201

    elif app.config["DEBUG"]:
        # GET form for debugging in TEST/DEBUG mode
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
        '''

    else:
        # GET not supported in prod
        return "Invalid path.", 404


@app.route("/uploads/dicom/<storage_handle>", methods=["GET"])
def download_dicom_file(storage_handle: str) -> Response:
    return send_from_directory(
        app.config["DICOM_FOLDER"], 
        FileStorageService.get_dcm_storage_handle(storage_handle),
    )


@app.route("/uploads/image/<storage_handle>", methods=["GET"])
def download_image_file(storage_handle: str) -> Response:
    return send_from_directory(
        app.config["IMAGE_FOLDER"], 
        FileStorageService.get_png_storage_handle(storage_handle),
    )


@app.route("/header_attributes/<storage_handle>", methods=["GET"])
def get_header_attributes(storage_handle: str) -> Response:
    try:
        tag_keys = set(json.loads(request.args.get("tags", "[]")))
    except (JSONDecodeError, TypeError):
        return "Invalid tags formatting.", 400
    if not DicomAttributeExtractor.validate_tag_keys(tag_keys):
        return f"Invalid tags: {tag_keys}.", 400

    try:
        return DicomAttributeExtractor.extract_dicom_attributes(
            FileStorageService.get_dcm_storage_path(storage_handle),
            tag_keys,
        )
    except FileNotFoundError:
        return "File not found.", 404
