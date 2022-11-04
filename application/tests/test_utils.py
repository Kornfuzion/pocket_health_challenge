from __init__ import test_client, TEST_FILE_PATH
from flask import url_for
from io import BytesIO


def upload_test_file(test_client: "FlaskClient", file_name: str = "example.dcm") -> None:
    with open(TEST_FILE_PATH, "rb") as fh:
        data = {"file": (BytesIO(fh.read()), file_name)}
    return test_client.post(
        url_for('upload_file'), 
        data=data, 
        follow_redirects=True,
        content_type='multipart/form-data',
    )
