# PocketHealth Backend Coding Challenge: File Server
A simple proof-of-concept microservice to upload DCM files, read DCM/PNG files, fetch DCM attributes by tag. Given the constraints of this project, we omit a few features necessary for productionization, described in **Limitations/ Future Improvements** below.

For simplicity, this implementation avoids the concept of users and user authentication/authorization.

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
**Upload File**
<pre>
@app.route("<b>/upload_file</b>", methods=["GET", "POST"])
def <b>upload_file()</b> -> Response:
</pre>

| Request| | |
|:---| :--- | :-- |
| |Path| /upload_file|
| |POST| Expects file using name="file", ContentType=multipart/form-data|

|Response        | | |
|:---| :--- | :-- |
| |Status code                                                    | 201 CREATED|
| |Response   | {"storage_handle": <storage_handle>}|
| |Description|<storage_handle> is a UUID containing alphanumerical characters|
| |Example    | {"storage_handle": "ef9b58755f8d4288bfcde5c2365e5ebd"}|

|Errors|Reason|Error Code|
|:---| :--- | :-- |
| |GET request in non-debug mode|404 Invalid path.|
| |Bad file/ wrong file type|400 Invalid file.|
 

**Download DICOM File**
<pre>
@app.route("<b>/uploads/dicom/&lt;storage_handle&gt;</b>", methods=["GET"])
def <b>download_dicom_file(storage_handle: str)</b> -> Response:
</pre>

| Request| | |
|:---| :--- | :-- |
| |Path| /uploads/dicom/&lt;storage_handle&gt;|
| |GET| storage_handle str = UUID returned from upload_file()|

|Response        | | |
|:---| :--- | :-- |
| |Status code                                                    | 200 SUCCESS|
| |Response   | DICOM file |

|Errors|Reason|Error Code|
|:---| :--- | :-- |
| |GET request in non-debug mode|404 Invalid path.|
| |Bad storage_handle|404 File not found.|
           
**Download PNG File**
<pre>
@app.route("<b>/uploads/image/&lt;storage_handle&gt;</b>", methods=["GET"])
def <b>download_image_file(storage_handle: str)</b> -> Response:
</pre>

| Request| | |
|:---| :--- | :-- |
| |Path| /uploads/dicom/&lt;storage_handle&gt;|
| |GET| storage_handle str = UUID returned from upload_file()|

|Response        | | |
|:---| :--- | :-- |
| |Status code                                                    | 200 SUCCESS|
| |Response   | PNG file |

|Errors|Reason|Error Code|
|:---| :--- | :-- |
| |GET request in non-debug mode|404 Invalid path.|
| |Bad storage_handle|404 File not found.|
       
**Get Header Attributes**
<pre>
@app.route("<b>/header_attributes/&lt;storage_handle&gt;</b>", methods=["GET"])
def <b>get_header_attributes(storage_handle: str)</b> -> Response:
</pre>

| Request| | |
|:---| :--- | :-- |
| |Path| /header_attributes/&lt;storage_handle&gt;|
| |GET| storage_handle str = UUID returned from upload_file()|
| | | tags: List[str] = List of tags in hex representation |
| |Example| [0x00080005]|
| |Note|request with no tags included returns all tags on the DICOM file |

|Response        | | |
|:---| :--- | :-- |
| |Status code                                                    | 200 SUCCESS|
| |Response   | JSON Dict[str, Dict[str, str]] mapping tag->info |

|Errors|Reason|Error Code|
|:---| :--- | :-- |
| |Invalid tags  |400 Invalid tags.|
| |Bad storage_handle|404 File not found.|

<pre>
# Request
{"tags": [0x00080005]}

# Response
{
   "0x00080005": {
      "VR": "CS",
      "name": "Specific Character Set",
      "value": "ISO_IR 100",
   }
}
</pre>

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
1. **Files are stored in the server's local file system**
   1. This means our servers are stateful and we'd need some kind of routing scheme to figure out which users should hit which servers to find their data. Ideally we leverage a distributed file store that can scale and also support additional features such as access control.

2. **UUID storage handle can still collide** 
   1. UUID minimizes the probability of collision, but can still cause unexpected data loss if storage_handle collides. In a production system with user_id provided, we could create an even safer file name. For example, something like:
   <pre>
   # It's unlikely for a user to upload twice in the same millisecond/microsecond AND experience UUID collision
   <b>storage_handle = f"{user_id}{uuid()}{current_timestamp()}"</b>
   </pre>

3. **Lack of user->file association**
   1. Since file names/folders contain valuable information (e.g. sequence number for slices of the same scan) we would need a way to associate users->files. We could create a simple relational database which maps (user_id, file_name) -> storage_handle. This would allow users to query for all of their uploads by file name and prevent collisions (on a per-user, per-file_name basis) by using a uniqueness constraint on (user_id, file_name).
   
4. **Lack of security/authorization measures**
   1. Set up TLS certificates to serve requests over HTTPS
   2. Implement authorization via OAuth2
   
5. **Currently only configured to run locally** 
   1. requires virtual env setup and package installation. Ideally this can be condensed into a container/Docker config for easy deployment on a production web server.

6. **DICOM + PNG file uploads cannot be bundled into an atomic operation** 
   1. Not robust to partial failure + retry. In production, this would lead to duplicate/orphaned DICOM files (first request fails after DICOM upload, retried and second request succeeds in reuploading DICOM + PNG). One possible solution could look like:

      a. Upload the DICOM with TTL or store some additional information in a "pending uploads" DB containing (storage_handle, upload_time)
      
      b. Use a message/task queue (could use topic=user_id for load balancing. upload ordering doesn't really matter), enqueue a message containing the storage_handle
      
      c. Message queue calls to task to perform DICOM->PNG or other image processing, upload the PNG file, remove TTL on DICOM file/ delete the entry from the "pending uploads" DB.
      
      d. If a partial failure occurs between the DICOM upload and message enqueue, either the file will eventually be deleted due to TTL or deleted up by a daily async job when the file is older than N days (N=14->30 to provide buffer for issues in production which may increase processing delay)
      
7. **Improve tests**
   1. Add unit tests + better integration test mocking to avoid flakiness from actual file upload/download on the server
