import os
import time
import requests
import threading
import subprocess
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from Functions import writer

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class Notices:
    def __init__(self):
        self.data = []
        self.json = writer.JSON()
        self.continue_fetch_data = True
        self.notice_download_path = os.path.join(os.environ['USERPROFILE'], 'Notice Downloader')

        self.session = requests.Session()
        self.session.verify = False

        self.url = 'https://fohss.tu.edu.np/notices'

        if os.path.exists(self.notice_download_path) is False:
            os.makedirs(self.notice_download_path)

    def is_notice_downloaded(self, pdf_name):
        """
        Check if a PDF file is already downloaded.
        """

        return pdf_name in os.listdir(self.notice_download_path)

    def download_notice(self, event, pdf_link, pdf_name):
        """
        Downloads the PDF file from the specified link and updates the GUI accordingly
        """

        pdf_path = os.path.join(self.notice_download_path, pdf_name + '.pdf')

        with open(pdf_path, 'wb') as f:  # Saving pdf to the download path
            content = self.session.get(pdf_link, stream=True)
            contents = content.content
            f.write(contents)

    def delete_notice(self, event, pdf_name):
        pdf_path = os.path.join(self.notice_download_path, pdf_name)

        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    def show_notice_in_browser(self, event, pdf_name):
        """
        Open the downloaded pdf in default browser
        """

        pdf_path = os.path.join(self.notice_download_path, pdf_name + '.pdf')
        os.startfile(pdf_path)

    def show_notice_location_in_explorer(self, event, pdf_name):
        """
        Open the file explorer and reveal the downloaded PDF
        """

        pdf_path = os.path.join(self.notice_download_path, pdf_name + '.pdf')
        FILE_BROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')

        subprocess.run([FILE_BROWSER_PATH, '/select,', pdf_path])

    def delete_notice(self, pdf_name):
        """
        Deletes the specified PDF file from the notice download path
        """

        pdf_path = os.path.join(self.notice_download_path, pdf_name)

        os.remove(pdf_path)

    def fetch_notices(self):
        """
        Fetches notices from the specified URL
        """

        while self.continue_fetch_data:
            notices = []

            request = self.session.get(self.url).content
            soup = BeautifulSoup(request, "html.parser")

            root_divs = soup.find_all('div', attrs={'class': 'recent-post-wrapper'})

            for divs in root_divs:
                date = divs.find('span', attrs={'id': 'nep_month'}).text

                root_notice_url = divs.find('div', attrs={'class': 'detail'}).find('a')['href']

                notice_page_content = self.session.get(root_notice_url).content
                notice_page_soup = BeautifulSoup(notice_page_content, "html.parser")

                table_divs = notice_page_soup.find('table')

                if table_divs:
                    table_rows = table_divs.find('tbody').find_all('tr')

                    for table_row in table_rows:
                        title = table_row.find('td').text
                        download_link = table_row.find('td', attrs={'class': 'text-center'}).find('a')['href']

                        notices.append(
                            {
                                'date': date,
                                'notice_name': title,
                                'download_link': download_link,
                                'is_notice_downloaded': self.is_notice_downloaded(title + '.pdf')
                            }
                        )

            self.data = notices
            time.sleep(60)

    def start_fetching_notices(self):
        """
        Initiates a background thread to asynchronously fetch notices using the `fetch_notices` method
        """

        thread = threading.Thread(target=self.fetch_notices, daemon=True)
        thread.start()
