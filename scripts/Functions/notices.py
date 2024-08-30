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

    def is_notice_downloaded(self, pdf_name):
        """
        Check if a PDF file is already downloaded.
        """

        return pdf_name in os.listdir(self.notice_download_path)

    def download_notice(self, event, pdf_link):
        """
        Downloads the PDF file from the specified link and updates the GUI accordingly
        """

        if os.path.exists(self.notice_download_path) is False:
            os.makedirs(self.notice_download_path)

        pdf_name = os.path.basename(pdf_link)
        pdf_path = os.path.join(self.notice_download_path, pdf_name)

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

        pdf_path = os.path.join(self.notice_download_path, pdf_name)
        os.startfile(pdf_path)

    def show_notice_location_in_explorer(self, event, pdf_name):
        """
        Open the file explorer and reveal the downloaded PDF
        """

        pdf_path = os.path.join(self.notice_download_path, pdf_name)
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

            all_divs = soup.find_all('div', attrs={'class': 'recent-post-wrapper'})

            for div in all_divs:
                notice = div.find('div', attrs={'class', 'detail'})

                notice_link = notice.find('a')['href']
                notice_page_content = self.session.get(notice_link).content

                notice = notice.find('h5').text

                notice_page_soup = BeautifulSoup(notice_page_content, "html.parser")
                pdf_tables = notice_page_soup.find('div', attrs={'class', 'download-wrapper'}).find('table').find('tbody')

                if pdf_tables:
                    for table in pdf_tables.find_all('tr'):
                        all_pdf_links = table.find_all('a')

                        for pdf_link in all_pdf_links:
                            date = div.find('span', {'id': 'nep_month'}).text
                            pdf_download_link = pdf_link['href']
                            pdf_name = pdf_download_link.split('/')[-1]

                            if self.json.does_exists(pdf_name) is False:
                                notices.append(
                                    {
                                        'date': date,
                                        'notice_name': pdf_name,
                                        'download_link': pdf_download_link,
                                        'is_notice_downloaded': self.is_notice_downloaded(pdf_name)
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