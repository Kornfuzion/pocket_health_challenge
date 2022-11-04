import pytest
from app import app
import os
from typing import Generator


TEST_FILE_PATH: str = os.path.abspath("./test_data/example.dcm")


@pytest.fixture(scope="module")
def test_client() -> Generator:
    app.config["TESTING"] = True
    # Avoid writing test data to prod
    app.config["DICOM_FOLDER"] = os.path.abspath("./test_uploads/DCM")
    app.config["IMAGE_FOLDER"] = os.path.abspath("./test_uploads/PNG")
    with app.test_client() as testing_client:
        app.app_context().push()
        app.test_request_context().push()
        print(type)
        yield testing_client
