# dlow
A library for downloading an S3 folder recursively and unzipping its contents. Extensible to other sources and post-processes.

## Installation
This library is available via pip from PyPI

```bash
pip install dlow
```

## Example use
```python
import logging
from dlow import ResourceDownloadOrchestrator
from dlow.s3 import S3FolderDownloader, S3FolderResourceDescriptor
from dlow.post_processing import FileUnzipper

s3_bucket_name = 'SOME_BUCKET_NAME'
s3_folder = '/some_folder'

download_orchestrator = ResourceDownloadOrchestrator(dest_dir='/resources',
                                                        resource_downloader=S3FolderDownloader(s3_bucket_name, s3_folder),
                                                        resource_descriptor=S3FolderResourceDescriptor(s3_bucket_name, s3_folder),
                                                        semaphore_pid_filepath='/tmp/app.pid',
                                                        post_download_processors=[FileUnzipper(delete_archive=True)],
                                                        logger=logging.getLogger('someLoggerName'),
                                                        clear_dest_dir=True)
download_orchestrator.ensure_resources_ready()
```

## AWS authentication for S3
This library uses the boto3 library to access S3. This reads the same configuration files on your host filesystem as the AWS CLI.
See http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html