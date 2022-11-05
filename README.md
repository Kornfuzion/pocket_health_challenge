# PocketHealth Backend Coding Challenge: File Server
A simple proof-of-concept microservice to upload DCM files, read DCM/PNG files, fetch DCM attributes by tag

## Problem Statement
[Backend_Programming_Challenge.pdf](https://github.com/Kornfuzion/pocket_health_challenge/files/9941528/Backend_Programming_Challenge.pdf)

## Design Considerations
1. **File names can cause a few issues**
   1. File names can easily collide across uploads, causing data loss.
   2. User-provided file names requires heavy input validation (check for obscure characters/ensure reasonable length/ensure file path does not cause file to be stored in unintended places in the file system)
   3. Accessing files directly from web (using file name as query param) means file names are guessable, which can make our service more susceptible to scraping/DDOS.
  - **decision: Generate 'unique' file name using UUID to minimize collision, avoid input validation, anonymize and randomize file names**

2. **DICOM metadata tags come in a few forms: tuple (0008,0005), hex 0x00080005, base10 int 524293**
   1. Tuples are not JSON serializable, which makes serialization and deserialization messy (requires dumping the entire tuple to str)
   2. base10 int is less readable, the information about the tag group + element is lost in this representation, which could make debugging difficult
  - **decision: Use hex representation for tag query to simplify key as a single int/str value while maintaining readability**

## APIs
1. 'upload_file()'
2. 'download_dicom_file()'
3. 'download_image_file()'
4. 'get_header_attributes()'

## Setup
<pre>
# 1. Clone repo
<b>git clone https://github.com/Kornfuzion/pocket_health_challenge</b>

# 2. Setup python virtual environment
<b>python3 -m venv env</b>
<b>source env/bin/activate</b>
<b>pip install -r requirements.txt</b>
</pre>

## Running locally
<pre>
# Navigate to application folder
<b>cd application</b>

# Debug Mode
<b>flask --app app --debug run</b>

# Production Mode
<b>flask --app app run</b>
</pre>
<img width="1001" alt="Screen Shot 2022-11-04 at 1 11 00 PM" src="https://user-images.githubusercontent.com/7553119/200039900-bbac7bc9-9bc4-4a10-8955-aff064215bb6.png">

## Running tests
The integration tests exercise all major functionality and error cases of our microservice. Files are actually being uploaded to our test server to a test directory and are subsequently deleted after tests finish running (via test.sh).
<pre>
# 1. Navigate to tests folder
<b>cd application/tests</b>

# 2. Run all tests
<b>./test.sh</b>
</pre>
<img width="999" alt="Screen Shot 2022-11-04 at 1 10 19 PM" src="https://user-images.githubusercontent.com/7553119/200039884-2c5e9a51-27b5-45d6-99a2-1639708b7580.png">
Test dicom files can be added or removed, as long as they adhere to the naming scheme of example{0}.dcm -> example{n}.dcm. Tests are configured to automatically run across all test files in the test_data directory.

## Limitations/ Future Improvements
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
5. Add unit tests + better integration test mocking to avoid actual file upload/download on the server
