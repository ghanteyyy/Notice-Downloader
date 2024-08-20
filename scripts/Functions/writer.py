import os
import json
from Functions import utils


class JSON:
    def __init__(self):
        self.json_path = utils.resource_path('downloaded_notices.json', 'JSON')
        self.notice_downloaded_path = os.path.join(os.environ['USERPROFILE'], 'Notice Downloader')

    def does_exists(self, pdf_name):
        '''
        Check if the given value exists in the JSON file
        '''

        return pdf_name in self.read_json()

    def clear_json(self, event=None):
        '''
        Empties json file
        '''

        with open(self.json_path, 'w'):
            pass

    def read_json(self):
        '''
        Read the contents of the JSON file
        '''

        try:
            with open(self.json_path, 'r') as f:
                return json.load(f)

        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def write_json(self, content):
        '''
        Write new content to the JSON file
        '''

        contents = self.read_json()
        contents.append(content)

        with open(self.json_path, 'w') as f:
            json.dump(contents, f, indent=4)
