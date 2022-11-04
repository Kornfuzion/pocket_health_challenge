#!/usr/bin/env bash

# CREATE TEST UPLOAD DIRECTORIES
mkdir -p test_uploads/DCM/
mkdir -p test_uploads/PNG/

python3 -m pytest

# DELETE TEST DATA POST-TEARDOWN
rm -rf test_uploads
