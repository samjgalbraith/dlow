# dlow
A library for downloading an S3 folder recursively and unzipping its contents. Extensible to other sources and post-processes.

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
                                                        resource_descriptor=S3FolderResourceDescriptor(s3_folder, s3_bucket_name),
                                                        post_download_processors=[FileUnzipper(delete_archive=True)],
                                                        logger=logging.getLogger('someLoggerName'),
                                                        clear_dest_dir=True)
download_orchestrator.ensure_resources_ready()
```
