import os
import sys
import time
import subprocess
from urllib3.exceptions import InsecureRequestWarning
import requests
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class Notices:
    def __init__(self):
        self.is_result_downloaded = False
        self.url = 'https://fohss.tu.edu.np/notices'
        self.downloads_path = os.path.join(os.environ['USERPROFILE'], 'Downloads')

    def is_pdf_downloaded(self, pdf_name):
        """
        Check if a PDF file is downloaded.

        Args:
            - pdf_name (str): The name of the PDF file.

        Returns:
            - bool: True if the PDF file is downloaded, False otherwise.
        """

        return pdf_name in os.listdir(self.downloads_path)

    def download_pdf(self, event, download_link):
        """
        Download a PDF file.

        Args:
            - event: The event triggering the download.
            - download_link (str): The URL to download the PDF file from.
        """

        pdf_name = os.path.basename(download_link)
        pdf_path = os.path.join(self.downloads_path, pdf_name)

        with open(pdf_path, 'wb') as f:
            content = self.session.get(download_link, verify=False, stream=True)
            contents = content.content
            f.write(contents)

    def reveal_in_explorer(self, event, pdf_name):
        """
        Open the file explorer and reveal the downloaded PDF.

        Args:
            - event: The event triggering the reveal action.
            - pdf_name (str): The name of the downloaded PDF file.
        """

        FILE_BROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
        pdf_location = os.path.join(self.downloads_path, pdf_name)

        subprocess.run([FILE_BROWSER_PATH, '/select,', pdf_location])

    def is_internet(self):
        """
        Check if there is an active internet connection.

        Returns:
        - bool: True if there is an active internet connection, False otherwise.
        """

        try:
            requests.get('http://google.com')
            return True

        except requests.ConnectionError:
            return False

    def resource_path(self, file_name):
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

        return os.path.join(base_path, 'assets', file_name)

    def get_notices(self):
        """
        Get notices related to BCA results.

        Returns:
            - list: A list of dictionaries containing information about the notices.
        """

        notices = []
        self.session = requests.Session()
        self.session.verify = False

        request = self.session.get(self.url).content
        soup = BeautifulSoup(request, "html.parser")

        all_divs = soup.find_all('div', attrs={'class': 'recent-post-wrapper'})

        for div in all_divs:
            date = div.find('h4').text
            curr_date = time.strftime('%Y-%m-%d')

            notice = div.find('div', attrs={'class', 'detail'})

            result_link = notice.find('a')['href']
            result_page_content = self.session.get(result_link).content

            notice = notice.find('h5').text
            lower_notice = notice.lower()

            result_page_soup = BeautifulSoup(result_page_content, "html.parser")
            pdf_page_link = result_page_soup.find('td', {'class': 'text-center'})
            pdf_link = pdf_page_link.find('a')['href']
            self.pdf_link = pdf_page_link.find('a')['href']

            self.pdf_name = self.pdf_link.split('/')[-1]
            pdf_name = self.pdf_link.split('/')[-1]

            if curr_date != date and 'result' in lower_notice and 'bca' in lower_notice:
                notices.append(
                    {
                        'notice_name': pdf_name,
                        'download_link': pdf_link,
                        'is_pdf_downloaded': self.is_pdf_downloaded(pdf_name)
                    }
                )

        return notices
