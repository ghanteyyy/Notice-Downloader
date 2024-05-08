import os
from urllib3.exceptions import InsecureRequestWarning
import requests
from bs4 import BeautifulSoup
from writer import JSON


requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class Notices:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False

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

    def get_notices(self):
        """
        Get notices related to BCA.

        Returns:
            - list: A list of dictionaries containing information about the notices.
        """

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
            pdf_page_link = notice_page_soup.find('td', {'class': 'text-center'})

            if pdf_page_link:
                pdf_link = pdf_page_link.find('a')['href']
                self.pdf_link = pdf_page_link.find('a')['href']

                self.pdf_name = self.pdf_link.split('/')[-1]
                pdf_name = self.pdf_link.split('/')[-1]

                is_it_valid_notice = all(map(lambda _notice: _notice in notice.lower(), ('bca',)))
                is_notice_deleted_by_user_previously = JSON().does_exists(pdf_name)

                if is_it_valid_notice and is_notice_deleted_by_user_previously is False:
                    date = div.find('span', {'id': 'nep_month'}).text

                    notices.append(
                        {
                            'date': date,
                            'notice_name': pdf_name,
                            'download_link': pdf_link,
                            'is_pdf_downloaded': self.is_pdf_downloaded(pdf_name)
                        }
                    )

        return notices
