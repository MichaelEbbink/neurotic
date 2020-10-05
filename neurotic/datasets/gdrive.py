import os
import json
import pickle
import urllib
from functools import reduce

from googleapiclient.discovery import build
import googleapiclient.errors
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from tqdm.auto import tqdm

import logging
logger = logging.getLogger(__name__)


user_dir = os.path.join(os.path.expanduser('~'), '.neurotic')
credentials_file = os.path.join(user_dir, 'gdrive-credentials.json')


# TODO: keep this?
save_token = True
token_file = os.path.join(user_dir, 'gdrive-token.pickle')


def gdrive_download(gdrive_url, local_file, overwrite_existing=False, show_progress=True, bytes_per_chunk=1024*1024*5):
    """
    Download a file from Google Drive.
    TODO ... using gdrive:// scheme...
    """
    if not overwrite_existing and os.path.exists(local_file):
        logger.info(f'Skipping {os.path.basename(local_file)} (already exists)')
        return

    logger.info(f'Downloading {os.path.basename(local_file)}')
    try:
        _download_with_progress_bar(gdrive_url, local_file, show_progress=show_progress, bytes_per_chunk=bytes_per_chunk)

    except googleapiclient.errors.HttpError as e:

        error_code = json.loads(e.args[1]).get('error', {}).get('code', None)

        if error_code == 404:
            # not found
            logger.error(f'Skipping {os.path.basename(local_file)} (not found on server for account "{_get_user_email()}")')
            return

        else:
            logger.error(f'Skipping {os.path.basename(local_file)} ({e})')
            return

    except Exception as e:

        logger.error(f'Skipping {os.path.basename(local_file)} ({e})')
        return


def _download_with_progress_bar(gdrive_url, local_file, show_progress=True, bytes_per_chunk=1024*1024*5):
    """
    Download while showing a progress bar.
    """
    # TODO: bytes_per_chunk=1024*1024*100 (100 MiB) would match
    # MediaIoBaseDownload's default chunk size and seems to be significantly
    # faster than smaller values, suggesting chunk fetching incurs a large
    # overhead. Unfortunately, such a large chunk size would prevent the
    # progress bar from updating frequently. As a compromise, the chunk size
    # used by this function is just 5 MiB, which is a little larger than is
    # ideal for progress reporting and yet still noticeably slows downloads. Is
    # there a better solution?

    # create the containing directory if necessary
    if not os.path.exists(os.path.dirname(local_file)):
        os.makedirs(os.path.dirname(local_file))

    file_id = _get_file_id(gdrive_url)
    if file_id is None:
        raise ValueError(f'error locating file on server for account "{_get_user_email()}"')

    service = _get_service()
    file_size_in_bytes = int(service.files().get(
        fileId=file_id, supportsAllDrives=True,
        fields='size').execute().get('size', 0))

    request = service.files().get_media(fileId=file_id)
    with open(local_file, 'wb') as f:
        downloader = MediaIoBaseDownload(f, request, chunksize=bytes_per_chunk)
        with tqdm(total=file_size_in_bytes, unit='B', unit_scale=True) as pbar:
            done = False
            while done is False:
                status, done = downloader.next_chunk()

                # set progress to the exact number of bytes downloaded so far
                pbar.n = status.resumable_progress
                pbar.update()


def _get_file_id(gdrive_url):
    """
    TODO ...
    """
    drive_name = urllib.parse.urlparse(gdrive_url).netloc
    path = urllib.parse.urlparse(gdrive_url).path
    path = os.path.normpath(path).strip(os.sep).split(os.sep)

    if drive_name == 'My Drive':
        drive_id = 'root'
    else:
        service = _get_service()
        drives = service.drives().list().execute().get('drives', [])
        drives = [drive for drive in drives if drive['name']==drive_name]

        if len(drives)==0:
            raise ValueError(f'drive "{drive_name}" not found on server for account "{_get_user_email()}"')
        elif len(drives)>1:
            raise ValueError(f'ambigous path, multiple drives with name "{drive_name}" exist on server for account "{_get_user_email()}"')
        else:
            drive_id = drives[0]['id']

    file_id = reduce(_get_child_id, path, drive_id)
    return file_id


def _get_child_id(parent_id, child_name):
    """
    TODO ...
    """
    if parent_id is None:
        return None

    service = _get_service()
    results = service.files().list(
        supportsAllDrives=True, includeItemsFromAllDrives=True,
        q=f'name="{child_name}" and "{parent_id}" in parents and trashed=false',
        fields="nextPageToken, files(id)").execute()

    items = results.get('files', [])
    if len(items)==0:
        raise ValueError(f'file or folder "{child_name}" not found on server for account "{_get_user_email()}"')
    elif len(items)>1:
        raise ValueError(f'ambiguous path, multiple files or folders with the name "{child_name}" exist under their parent folder on server for account "{_get_user_email()}"')
    else:
        child_id = items[0]['id']

    return child_id


def _get_user_email():
    """
    TODO ...
    """
    service = _get_service()
    results = service.about().get(fields='user').execute()
    email = results.get('user', {}).get('emailAddress', 'unknown email')
    return email


def _get_service():
    """
    TODO ...
    """
    creds = _get_creds()
    service = build('drive', 'v3', credentials=creds)
    return service


def _get_creds():
    """
    TODO ...
    """
    if not os.path.exists(credentials_file):
        raise FileNotFoundError(f'missing Google Drive API credentials file "{credentials_file}"')

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if save_token and os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            scopes = ['https://www.googleapis.com/auth/drive.readonly']
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, scopes)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        if save_token:
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)

    return creds


if __name__ == '__main__':

    # TODO: remove

    import sys
    class StreamLoggingFormatter(logging.Formatter):
        """
        A custom formatter for stream logging
        """
        def format(self, record):
            if record.levelno == logging.INFO:
                # exclude the level name ("INFO") from common log records
                self._style._fmt = '[neurotic] %(message)s'
            else:
                self._style._fmt = '[neurotic] %(levelname)s: %(message)s'
            return super().format(record)
    logger.setLevel(logging.INFO)
    logger_streamhandler = logging.StreamHandler(stream=sys.stderr)
    logger_streamhandler.setFormatter(StreamLoggingFormatter())
    logger.addHandler(logger_streamhandler)


    remote_path = 'gdrive://LFI-neural-correlates/Mirror of GIN data repository/LFI-neural-correlates/README.md'
    # remote_path = 'gdrive://My Drive/Chiel Lab/neurotic-paper-figures.zip'
    # remote_path = 'gdrive://My Drive/Introduction to Python for Neuroscientists/Zoom recordings of Python lessons/Session-08--2020-09-13.mp4'

    local_file = os.path.join('temp', os.path.basename(remote_path))
    gdrive_download(remote_path, local_file, overwrite_existing=True)
