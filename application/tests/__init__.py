import pytest
from app import app
import os
from typing import Generator


# Stub to make tests + decorators cooperate
@pytest.fixture(scope="module")
def test_file_path():
    pass


@pytest.fixture(scope="module")
def test_client() -> Generator:
    app.config["TESTING"] = True
    # Avoid writing test data to prod
    app.config["DICOM_FOLDER"] = os.path.abspath("./test_uploads/DCM")
    app.config["IMAGE_FOLDER"] = os.path.abspath("./test_uploads/PNG")
    with app.test_client() as testing_client:
        app.app_context().push()
        app.test_request_context().push()
        yield testing_client
