import os
import subprocess
from tkinter import *
from tkinter.font import Font
from tkinter import messagebox
from PIL import Image, ImageTk
from notices import Notices
from audio import Audio
from writer import JSON
from error import Error
import utils


class BCA_Notice_Downloader:
    def __init__(self):
        self.JSON = JSON()
        self.Audio = Audio()
        self.Notices = Notices()

        self.all_notices = []
        self.update_notice_timer = None

    def show_in_folder(self, event, pdf_name):
        """
        Open the file explorer and reveal the downloaded PDF.

        Args:
            - event: The event triggering the reveal action.
            - pdf_name (str): The path of the pdf_name to be revealed in the explorer
        """

        FILE_BROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
        pdf_location = os.path.join(self.Notices.downloads_path, pdf_name)

        subprocess.run([FILE_BROWSER_PATH, '/select,', pdf_location])

    def show_in_browser(self, event, pdf_path):
        """
        Open the downloaded pdf in default browser.

        Args:
            - event: The event triggering the reveal action.
            - pdf_path (str): The path of the pdf to be opened in the browser
        """

        full_pdf_path = os.path.join(self.Notices.downloads_path, pdf_path)
        os.startfile(full_pdf_path)

    def download_pdf(self, event, download_link):
        """
        Downloads the PDF file from the specified link and updates the GUI accordingly

        Args:
            - event: The event triggering the function call (not used)
            - download_link (str): The URL to download the PDF file from.
        """

        pdf_name = os.path.basename(download_link)
        pdf_path = os.path.join(self.Notices.downloads_path, pdf_name)

        with open(pdf_path, 'wb') as f:  # Saving pdf to the download path
            content = self.Notices.session.get(download_link, stream=True)
            contents = content.content
            f.write(contents)

        buttons_frame = event.widget.master  # Getting frame where buttons reside

        for widget in buttons_frame.winfo_children():  # Removing all widgets from buttons_frame
            widget.destroy()

        binding_function = lambda event=Event, location=pdf_name: self.show_in_folder(event, location)

        self.place_buttons(True, buttons_frame, pdf_name, self.show_in_directory_image, binding_function)

    def delete_pdf(self, event, pdf_name):
        '''
        Remove the downloaded pdf from the device
        '''

        try:
            pdf_path = os.path.join(self.Notices.downloads_path, pdf_name)
            os.remove(pdf_path)

            event.widget.master.master.destroy()

            for notice in self.all_notices:
                if notice['notice_name'] == pdf_name:
                    self.all_notices.remove(notice)

            self.JSON.write_json(pdf_name)

            self.create_widgets(scrape=False)

        except:
            messagebox.showerror('ERR', "Error: Unable to delete the file. The file either does not exist or is located in a directory that requires administrator privileges for deletion")

    def resize_image(self, image_name, size=(20, 20)):
        """
        Resize the given image to the specified size using Lanczos resampling

        Args:
            - image_name (str): The image to be resized
            - size (tuple): A tuple representing the new size of the image. Default is (40, 40)

        Returns:
            - PIL.Image.Image: The resized image.
        """

        image_path = utils.resource_path(image_name)
        image = Image.open(image_path)

        image = image.resize(size, Image.Resampling.LANCZOS)
        image = ImageTk.PhotoImage(image)

        return image

    def create_widgets(self, scrape=True):
        '''
        Create widgets for displaying notices.

        It clears existing widgets, fetches notices from web scraping
        in every minute, and populates the GUI accordingly.

        If there's no internet connection, it displays an error
        message. If there are no notices available, it also displays
        an appropriate message.

        If notices are available, it displays them with options to view or download.

        Parameters:
            scrape (bool): If True, force scraping for new notices. Defaults to True.

        '''

        for children in self.window.winfo_children():
            children.destroy()

        if scrape:
            self.all_notices = self.Notices.get_notices()

        if utils.is_internet() is False:
            self.Error.error_text_var.set('Unable to connect to the internet')
            self.Error.show_error()

        elif not self.all_notices:
            self.Error.error_text_var.set('No notices have been published as of yet !!!')
            self.Error.show_error()

        else:
            mute_unmute_label = Label(self.window, text="Press <space> key to pause or resume audio", justify=CENTER, font=('Calibri', 12, 'bold'), background='white', foreground='red')
            mute_unmute_label.pack(ipady=5, fill=X, expand=True)

            notices_frame = Frame(self.window, background='white')
            notices_frame.pack(padx=10, pady=10)

            for index, notice in enumerate(self.all_notices):
                notice_name = notice['notice_name']
                is_notice_downloaded = notice['is_pdf_downloaded']

                inner_frame = Frame(notices_frame, background='white', highlightthickness=2, highlightbackground='grey', highlightcolor='grey')
                inner_frame.pack(pady=(10 if index > 0 else 0, 0), fill='x')

                if is_notice_downloaded:
                    image = self.show_in_directory_image
                    binding_function = lambda event=Event, location=notice_name: self.show_in_folder(event, location)

                else:
                    image = self.download_image
                    binding_function = lambda event=Event, pdf_link=notice['download_link']: self.download_pdf(event, pdf_link)

                notice_label = Label(inner_frame, text=notice_name.split('.')[0], font=Font(family='Calibri', size=15), height=3, background='#43766C', foreground='whitesmoke')
                notice_label.pack(side=LEFT, ipadx=5, fill='x', expand=True)

                buttons_frame = Frame(inner_frame, background='white')
                buttons_frame.pack(side=RIGHT, fill=BOTH, ipadx=10)

                self.place_buttons(is_notice_downloaded, buttons_frame, notice_name, image, binding_function)

            self.Audio.play_audio()

        if scrape:
            self.update_notice_timer = self.window.after(60000, self.create_widgets)

    def place_buttons(self, is_notice_downloaded, buttons_frame, notice_name, image, binding_function):
        '''
        Place the 'open_in_folder' and 'open_in_browser' buttons after
        the user downloads the PDF, or only place download buttons when
        the PDF has not been downloaded
        '''

        label_common_attributes = {'relief': FLAT, 'cursor': 'hand2', 'background': 'white'}

        if is_notice_downloaded:
            open_in_browser_button = Label(buttons_frame, image=self.open_in_browser_image, **label_common_attributes)
            open_in_browser_button.pack()
            open_in_browser_button.image = self.open_in_browser_image
            open_in_browser_button.bind('<Button-1>', lambda event=Event, pdf_path=notice_name: self.show_in_browser(event, pdf_path))

        download_or_open_in_explorer_button = Label(buttons_frame, image=image, **label_common_attributes)
        download_or_open_in_explorer_button.pack(fill=BOTH, expand=True)
        download_or_open_in_explorer_button.image = image
        download_or_open_in_explorer_button.bind('<Button-1>', binding_function)

        if is_notice_downloaded:
            delete_button = Label(buttons_frame, image=self.delete_image, **label_common_attributes)
            delete_button.pack()
            delete_button.image = self.delete_image
            delete_button.bind('<Button-1>', lambda event=Event, pdf_name=notice_name: self.delete_pdf(event, pdf_name))

    def center_window(self):
        '''
        Set the position of the window to the center of the screen upon program launch
        '''

        self.window.update()
        self.window.iconphoto(False, ImageTk.PhotoImage(Image.open(utils.resource_path('icon.jpg'))))

        width, height = self.window.winfo_width(), self.window.winfo_height()
        screenwidth, screenheight = self.window.winfo_screenwidth() // 2, self.window.winfo_screenheight() // 2
        self.window.geometry(f'+{screenwidth - width // 2}+{screenheight - height // 2}')

        self.window.resizable(0, 0)
        self.window.deiconify()

        self.window.resizable(False, False)

    def main(self):
        self.window = Tk()
        self.window.withdraw()

        self.window.config(background='white')
        self.window.title('BCA Notices')

        self.Error = Error(self.window, self.Audio)

        self.delete_image = self.resize_image('delete.png')
        self.download_image = self.resize_image('download_pdf.png')
        self.open_in_browser_image = self.resize_image('open_in_browser.png')
        self.show_in_directory_image = self.resize_image('show_in_directory.png')

        self.create_widgets()

        self.window.after(250, self.center_window)
        self.window.bind('<space>', self.Audio.pause_unpause_audio)

        self.window.mainloop()


if __name__ == '__main__':
    win = BCA_Notice_Downloader()
    win.main()
