import os
import sys
import requests


def is_internet():
    '''
    Check if user is connected to internet
    '''

    try:
        requests.get('http://google.com')
        return True

    except requests.ConnectionError:
        return False


def resource_path(file_name, inner_directory):
    '''
    Get absolute path to resource from temporary directory

    In development:
        Gets path of files that are used in this script like icons, images or
        file of any extension from current directory

    After compiling to .exe with pyinstaller and using --add-data flag:
        Gets path of files that are used in this script like icons, images or
        file of any extension from temporary directory
    '''

    try:
        base_path = sys._MEIPASS  # PyInstaller creates a temporary directory and stores path of that directory in _MEIPASS

    except AttributeError:
        base_path = os.getcwd()
        base_path = os.path.split(base_path)[0]

    return os.path.join(base_path, 'assets', inner_directory, file_name)