import os
import logging
import boto3
from dlow._dlow_core import ResourceDownloader


class S3FolderDownloader(ResourceDownloader):
    """Downloads a folder from an S3 bucket, reproducing its structure within a local filesystem folder.
       Performs parallel post-download processing when post_download_processes are provided."""
    def __init__(self, s3_bucket_name, s3_top_level_source_folder):
        self._s3_bucket_name = s3_bucket_name
        self._s3_top_level_source_folder = s3_top_level_source_folder
        self._s3_client = boto3.client('s3')
        self._s3_resource = boto3.resource('s3')

        # Make sure the folder name ends with a slash.
        if not self._s3_top_level_source_folder.endswith('/'):
            self._s3_top_level_source_folder += '/'
        # Make sure the folder path doesn't start with a slash.
        self._s3_top_level_source_folder = self._s3_top_level_source_folder.lstrip('/')

    def _download_s3_dir(self, dest_dir, logger, recursive=True, s3_current_source_folder=None):
        """Downloads all objects in the given S3 bucket and source folder into the given local destination folder.
           If recursive=True, the folder structure of s3_top_level_source_folder will be recreated inside local_dest_folder with copying performed recursively."""

        s3_current_source_folder = self._s3_top_level_source_folder if s3_current_source_folder is None else s3_current_source_folder
        paginator = self._s3_client.get_paginator('list_objects')
        for s3_objects_list in paginator.paginate(Bucket=self._s3_bucket_name, Delimiter='/', Prefix=s3_current_source_folder):
            if recursive:
                s3_folders = s3_objects_list.get('CommonPrefixes')
                if s3_folders is not None:
                    for subfolder in s3_folders:
                        # Recurse. Use yield to pop yielded results back up the recursion stack.
                        for downloaded_file_path in self._download_s3_dir(dest_dir, logger, recursive=True, s3_current_source_folder=subfolder.get('Prefix')):
                            yield downloaded_file_path

            # Folders have a key ending with a slash so we filter them out.
            s3_file_objects = [obj for obj in s3_objects_list.get('Contents') or [] if not obj['Key'].endswith('/')]
            for s3_file_object in s3_file_objects:
                s3_object_key = s3_file_object['Key']
                # Here we chop off the path segments of the top level source directory for the destination path.
                # This has the effect of copying only the folder structure from that point inward, rather than the whole bucket folder structure from the top.
                dest_path_of_file = os.path.realpath(os.path.join(dest_dir, s3_object_key[len(self._s3_top_level_source_folder):]))
                dest_folder_of_file = os.path.dirname(dest_path_of_file)
                if not os.path.exists(dest_folder_of_file):
                    logger.info('Creating local directory %s' % (dest_folder_of_file,))
                    os.makedirs(dest_folder_of_file)
                logger.info('Starting download of object %s from bucket %s to local directory %s' % (
                    s3_object_key, self._s3_bucket_name, dest_path_of_file))
                self._s3_resource.meta.client.download_file(self._s3_bucket_name, s3_object_key, dest_path_of_file)
                logger.info('Finished download of object %s from bucket %s to local directory %s' % (s3_object_key, self._s3_bucket_name, dest_path_of_file))

                yield dest_path_of_file

    def iter_downloaded_files(self, dest_dir, logger=logging.getLogger(), recursive=True):
        for downloaded_file_path in self._download_s3_dir(dest_dir, logger, recursive):
            yield downloaded_file_path