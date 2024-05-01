import json
import utils


class JSON:
    def __init__(self):
        self.json_path = utils.resource_path('db.json')

    def does_exists(self, key):
        '''
        Check if the give value exists in the JSON file
        '''

        return key in self.read_json()

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
