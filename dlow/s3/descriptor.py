import json

class S3FolderResourceDescriptor(object):
    """Describes an S3 folder resource and its contents."""

    def __init__(self, s3_bucket_name, s3_folder):
        self._s3_bucket_name = s3_bucket_name
        self._s3_folder = s3_folder

    def __str__(self):
        return json.dumps({'s3': {'bucket': self._s3_bucket_name, 'folder': self._s3_folder}})