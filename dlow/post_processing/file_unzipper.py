import os
import logging
import zipfile
from dlow._dlow_core import PostDownloadFileProcessor

class FileUnzipper(PostDownloadFileProcessor):
    """Unzips .zip files into the same directory, deleting the zip archive immediately afterward."""

    def __init__(self, delete_archive=False):
        self._delete_archive = delete_archive

    def process(self, filepath, logger=logging.getLogger()):
        if filepath.endswith('.zip'):
            logger.info('Unzipping %s' % (filepath,))
            with zipfile.ZipFile(filepath, 'r') as archive:
                archive.extractall(os.path.dirname(filepath))
            logger.info('Finished unzipping %s.' % (filepath,))
            if self._delete_archive:
                logger.info('Deleting archive file %s.' % (filepath,))
                os.remove(filepath)
                logger.info('Deleted archive file %s.' % (filepath,))