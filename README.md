# PocketHealth Coding Challenge
A simple microservice to upload DCM files, read DCM/PNG files, fetch DCM attributes by tag

## Problem Statement
[Backend_Programming_Challenge.pdf](https://github.com/Kornfuzion/pocket_health_challenge/files/9941528/Backend_Programming_Challenge.pdf)

## Design Considerations
1. 

## APIs
1. 'upload_file()'
2. 'download_dicom_file()'
3. 'download_image_file()'
4. 'get_header_attributes()'

## Setup
```
git clone https://github.com/Kornfuzion/pocket_health_challenge

python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Running locally
<pre>
<b>cd application</b>

# Debug Mode
<b>flask --app app --debug run</b>

# Production Mode
<b>flask --app app run</b>
</pre>
<img width="1001" alt="Screen Shot 2022-11-04 at 1 11 00 PM" src="https://user-images.githubusercontent.com/7553119/200039900-bbac7bc9-9bc4-4a10-8955-aff064215bb6.png">

## Running tests
<pre>
<b>cd application/tests</b>
<b>./test.sh</b>
</pre>
<img width="999" alt="Screen Shot 2022-11-04 at 1 10 19 PM" src="https://user-images.githubusercontent.com/7553119/200039884-2c5e9a51-27b5-45d6-99a2-1639708b7580.png">

## Limitations/Future Improvements
1. Given the constraints of this challenge, we are using the server's local file system. This means our servers are stateful and we'd need some kind of routing scheme to figure out which users should hit which servers to find their data. Ideally we leverage a distributed file store that can scale and also support additional features such as access control.

2. File name generation uses UUID, which minimizes the probability of collision, but can still cause unexpected data loss if storage_handle collides. Given a production system with user/uploader id provided, we could create an even safer file name. For example, something like:
   <pre>
   # It's unlikely for a user to upload twice in the same millisecond/microsecond AND experience UUID collision
   <b>storage_handle = f"{user_id}{uuid()}{current_timestamp()}"</b>
   </pre>
   Since file names/folders contain valuable information (e.g. sequence number for slices of the same scan) we would need a way to associate users->files. We could create a database which maps (user_id, file_name) -> storage_handle. This would allow users to query for all of their uploads by name and prevent collisions via uniqueness constraint on (user_id, file_name).
   
3. Currently this is only configured to run locally, requiring some virtual env setup and package installation. Ideally this can be condensed into a container/Docker config for easy deployment on a production server.

4. DICOM + PNG file uploads cannot be bundled into an atomic operation and are not idempotent on partial failure + retry. In production, this would mean we could have duplicate/orphaned DICOM files (first request fails after DICOM upload, retried and second request succeeds in reuploading DICOM + PNG). Some ideas on how to improve on this given the time/resources:

   a. Upload the DICOM with TTL or upload the DICOM including some additional attribute finished_processing=False, upload_time=X
   
   b. Use a message/task queue (could use user_id as topic, but upload ordering doesn't exactly matter), enqueue a message containing the storage_handle
   
   
   c. Message queue calls to task to perform DICOM->PNG or other image processing, upload the PNG file, remove TTL on DICOM file/ set finished_processing=True on DICOM file
   
   d. If a partial failure occurs between the DICOM upload and message enqueue, either it will eventually be deleted due to TTL or cleaned up by an async job when the file is older than N days and finished_processing=False (which should be okay if N is significantly larger than the queue latency SLA, giving some buffer for issues in production)
