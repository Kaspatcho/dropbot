import requests
from json import dumps
import re
from credentials import API_KEY

class DropBoxUpload:
    def __init__(self, dropbox_path : str, local_file_path : str):
        self.session_id = None
        self.dropbox_path = dropbox_path
        self.local_file_path = local_file_path
        self.offset = 0
        self.offset_diff = 0


    def open_session(self) -> dict:
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Dropbox-API-Arg': '{"close": false}',
            'Content-Type': 'application/octet-stream',
        }

        response = requests.post('https://content.dropboxapi.com/2/files/upload_session/start', headers=headers)
        self.session_id = response.json().get('session_id')

        return response.ok


    def append(self, data):
        args = {
            "cursor": {
                "session_id": self.session_id,
                "offset": self.offset
            },
            "close": False
        }

        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Dropbox-API-Arg': dumps(args),
            'Content-Type': 'application/octet-stream',
        }

        response = requests.post('https://content.dropboxapi.com/2/files/upload_session/append_v2', headers=headers, data=data)

        if correct_offset := self._get_correct_offset(response.text):
            self.offset = correct_offset
            return self.append(data)

        self.offset += self.offset_diff

        return response.json()


    def finish_session(self):

        args = {
            "cursor": {
                "session_id": self.session_id,
                "offset": self.offset
            },
            "commit": {
                "path": self.dropbox_path,
                "mode": "add",
                "autorename": True,
                "mute": False,
                "strict_conflict": False
            }
        }

        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Dropbox-API-Arg': dumps(args),
            'Content-Type': 'application/octet-stream',
        }

        response = requests.post('https://content.dropboxapi.com/2/files/upload_session/finish', headers=headers)

        if correct_offset := self._get_correct_offset(response.text):
            self.offset = correct_offset
            return self.finish_session()

        return response.json()


    def _get_correct_offset(self, data):
        if data is None: return False
        matches = re.search(r"(?<=\"correct_offset\"\:\s)\d+", data)
        if matches is None: return False
        correct_offset = int(matches.group(0))
        self.offset_diff = correct_offset - self.offset
        return correct_offset


    def __enter__(self):
        self.open_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish_session()
