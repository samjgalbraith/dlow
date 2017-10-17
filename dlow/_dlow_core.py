#!/usr/bin/env python
import os
import errno
import shutil
import threading
import logging


def mkdir_p(path):
    """Provides functionality analogous to linux `mkdir -P` which creates any necessary folders to satisfy the existence
       of the provided full filesystem directory path."""
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class DownloadStateFlagger(object):

    def __init__(self, ready_file_dir, download_resource_descriptor, logger=logging.getLogger(), ready_file_name='.ready'):
        self._logger = logger
        self._download_ready_file_path = os.path.realpath(os.path.join(ready_file_dir, ready_file_name))
        self._download_resource_descriptor = download_resource_descriptor

    def flag_as_ready(self):
        """Flags the folder as downloaded and ready to consume."""
        self._logger.info("Flagging the resource '%s' as ready for the service to consume." % (self._download_resource_descriptor.__str__(),))
        with open(self._download_ready_file_path, 'w') as ready_file:
            ready_file.write(self._download_resource_descriptor.__str__())

    def is_flagged_as_ready(self):
        """Returns True if the download folder is flagged as ready to consume."""
        if os.path.exists(self._download_ready_file_path):
            with open(self._download_ready_file_path, 'r') as ready_file:
                flag_file_contents = '\n'.join(ready_file.readlines())
                return flag_file_contents == self._download_resource_descriptor.__str__()
        return False


class ResourceDownloader(object):

    def iter_downloaded_files(self, dest_dir):
        """Returns an iterator which yields local file paths of files downloaded from the resource."""
        raise NotImplementedError('ResourceDownloader subclasses must implement iter_downloaded_files iterator.')


class PostDownloadFileProcessor(object):

    def process(self, filepath):
        """Performs some process against the file at the given path."""
        raise NotImplementedError('PostDownloadFileProcessor subclass must implement process.')


class ResourceDownloadOrchestrator:

    def __init__(self, dest_dir, resource_downloader, resource_descriptor, post_download_processors=[], error_on_nothing_downloaded=True, clear_dest_dir=False):
        self._dest_dir = dest_dir
        self._resource_downloader = resource_downloader
        self._resource_descriptor = resource_descriptor
        self._post_download_processors = post_download_processors
        self._error_on_nothing_downloaded = error_on_nothing_downloaded
        self._clear_dest_dir = clear_dest_dir

    def _post_process_downloaded_file(self, file_path, logger):
        for processor in self._post_download_processors:
            processor.process(file_path, logger=logger)

    def _clear_destination_dir(self):
        """Deletes all existing files and subdirectories in the destination directory."""
        for current_dir, subdirs, files in os.walk(self._dest_dir):
            if current_dir == self._dest_dir:
                for subdir in subdirs:
                    shutil.rmtree(os.path.join(current_dir, subdir))
                for f in files:
                    os.remove(os.path.join(current_dir, f))
                # We were only looking for the current directory so once we hit it we know we don't need to keep iterating.
                break

    def ensure_resources_ready(self, logger=logging.getLogger()):
        download_state_flagger = DownloadStateFlagger(self._dest_dir, self._resource_descriptor, logger=logger)
        if download_state_flagger.is_flagged_as_ready():
            return
        else:
            mkdir_p(self._dest_dir)
            if self._clear_dest_dir:
                self._clear_destination_dir()

            post_download_processing_threads = []
            num_files_downloaded = 0
            for downloaded_file_path in self._resource_downloader.iter_downloaded_files(self._dest_dir, logger=logger):
                num_files_downloaded += 1
                # Start a background thread to post-process the downloaded file.
                post_process_thread = threading.Thread(target=self._post_process_downloaded_file, args=(downloaded_file_path,logger))
                post_process_thread.start()
                post_download_processing_threads.append(post_process_thread)

            # Let all the post-processing threads finish.
            for thread in post_download_processing_threads:
                thread.join()

            if num_files_downloaded == 0:
                nothing_downloaded_message = 'Downloaded zero files. Check your configuration and that the source contains resources.'
                logger.warn(nothing_downloaded_message)
                if self._error_on_nothing_downloaded:
                    raise IOError(nothing_downloaded_message)

            download_state_flagger.flag_as_ready()
            logger.info('Flagged downloaded resources as ready.')
    
    def resources_are_ready(self):
        download_state_flagger = DownloadStateFlagger(self._dest_dir, self._resource_descriptor)
        return download_state_flagger.is_flagged_as_ready()
