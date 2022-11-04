#!/usr/bin/env bash

# SETUP: CREATE TEST UPLOAD DIRECTORIES
mkdir -p test_uploads/DCM/
mkdir -p test_uploads/PNG/

python3 -m pytest -vv

# TEARDOWN: DELETE TEST DATA
rm -rf test_uploads
