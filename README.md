# PocketHealth Coding Challenge
A simple microservice to upload DCM files, read DCM/PNG files, fetch DCM attributes by tag

## Problem Statement
[Backend_Programming_Challenge.pdf](https://github.com/Kornfuzion/pocket_health_challenge/files/9941528/Backend_Programming_Challenge.pdf)

## Setup
'''
git clone https://github.com/Kornfuzion/pocket_health_challenge

python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
'''

## APIs
1. 'upload_file()'
2. 'download_dicom_file()'
3. 'download_image_file()'
4. 'get_header_attributes()'

## Running locally
'''
# Debug Mode
flask --app app --debug run
# Production Mode
flask --app app run
'''
<img width="1001" alt="Screen Shot 2022-11-04 at 1 11 00 PM" src="https://user-images.githubusercontent.com/7553119/200039900-bbac7bc9-9bc4-4a10-8955-aff064215bb6.png">

## Running tests
<img width="999" alt="Screen Shot 2022-11-04 at 1 10 19 PM" src="https://user-images.githubusercontent.com/7553119/200039884-2c5e9a51-27b5-45d6-99a2-1639708b7580.png">

## Limitations/Notes
