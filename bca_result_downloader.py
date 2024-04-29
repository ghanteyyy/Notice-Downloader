import os
import subprocess
from tkinter import *
from tkinter.font import Font
from PIL import ImageTk, Image
import utils
from audio import Audio
from notices import Notices


class BCA_Result_Downloader:
    def __init__(self):
        self.Audio = Audio()
        self.Notices = Notices()
        self.icon_image = Image.open(utils.resource_path('icon.jpg'))

    def resize_image(self, image, size=(20, 20)):
        """
        Resize the given image to the specified size using Lanczos resampling

        Args:
            - image (PIL.Image.Image): The image to be resized
            - size (tuple): A tuple representing the new size of the image. Default is (40, 40)

        Returns:
            - PIL.Image.Image: The resized image.
        """

        image = image.resize(size, Image.Resampling.LANCZOS)
        image = ImageTk.PhotoImage(image)

        return image

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

        img = self.resize_image(self.show_in_directory_image)
        binding_function = lambda event=Event, location=pdf_name: self.show_in_folder(event, location)

        self.place_buttons(True, buttons_frame, pdf_name, img, binding_function)

    def center_window(self):
        '''
        Set position of the window to the center of the screen when user open the program
        '''

        self.window.update()
        self.window.iconphoto(False, ImageTk.PhotoImage(self.icon_image))

        width, height = self.window.winfo_width(), self.window.winfo_height()
        screenwidth, screenheight = self.window.winfo_screenwidth() // 2, self.window.winfo_screenheight() // 2
        self.window.geometry(f'+{screenwidth - width // 2}+{screenheight - height // 2}')

        self.window.resizable(0, 0)
        self.window.deiconify()

        self.window.resizable(False, False)

    def update_notices(self):
        '''
        Fetch and update notices in every minute
        '''

        play_audio = False

        for widget in self.window.winfo_children(): # Deleting all notice widgets
            widget.destroy()

        if utils.is_internet() is False:
            self.error_text.set('Unable to connect to the internet')
            self.when_any_error()
            return

        retrieved_notices = self.Notices.get_notices()

        if retrieved_notices:
            mute_unmute_label = Label(self.window, text="Press <space> key to pause or resume audio", justify=CENTER, font=('Calibri', 12, 'bold'), background='white', foreground='red')
            mute_unmute_label.pack(ipady=5, fill=X)

            notices_frame = Frame(self.window, background='white')
            notices_frame.pack(padx=10, pady=10)

            for index, notice in enumerate(retrieved_notices):
                notice_name = notice['notice_name']
                is_notice_downloaded = notice['is_pdf_downloaded']

                if is_notice_downloaded:
                    image = self.show_in_directory_image
                    binding_function = lambda event=Event, location=notice_name: self.show_in_folder(event, location)

                else:
                    play_audio = True
                    image = self.download_image
                    binding_function = lambda event=Event, pdf_link=notice['download_link']: self.download_pdf(event, pdf_link)

                image = self.resize_image(image)

                inner_frame = Frame(notices_frame, background='#43766C')
                inner_frame.pack(pady=(5 if index > 0 else 0, 0), fill='x')

                self.notice_label = Label(inner_frame, text=notice_name, font=Font(family='Calibri', size=15), justify=CENTER, height=3, background='#43766C', foreground='whitesmoke')
                self.notice_label.pack(side=LEFT, ipadx=5, fill='x')

                buttons_frame = Frame(inner_frame, background='white')
                buttons_frame.pack(side=RIGHT, fill=BOTH, ipadx=10)

                self.place_buttons(is_notice_downloaded, buttons_frame, notice_name, image, binding_function)

            if play_audio or self.Audio.is_audio_paused is False:
                self.Audio.play_audio()

        else:
            self.error_text.set('No results have been published as of yet !!!')
            self.when_any_error()

        self.window.after(60000, self.update_notices)

    def place_buttons(self, is_notice_downloaded, buttons_frame, notice_name, image, binding_function):
        '''
        Place the 'open_in_folder' and 'open_in_browser' buttons after
        the user downloads the PDF, or only place download buttons when
        the PDF has not been downloaded
        '''

        side = RIGHT

        if is_notice_downloaded:
            open_in_browser_image = self.resize_image(self.open_in_browser_image)

            open_in_browser_button = Label(buttons_frame, image=open_in_browser_image, relief=FLAT, cursor='hand2', background='white')
            open_in_browser_button.pack(side=TOP)
            open_in_browser_button.image = open_in_browser_image

            open_in_browser_button.bind('<Button-1>', lambda event=Event, pdf_path=notice_name: self.show_in_browser(event, pdf_path))

            side = BOTTOM

        download_button = Label(buttons_frame, image=image, relief=FLAT, cursor='hand2', background='white')
        download_button.pack(side=side)
        download_button.image = image

        download_button.bind('<Button-1>', binding_function)

    def when_any_error(self):
        '''
        Show error messages:
            1. When there is no internet connection
            2. When no result is published
        '''

        inner_frame = Frame(self.window, background='whitesmoke')
        inner_frame.pack()

        no_notice_label = Label(inner_frame, textvariable=self.error_text, font=Font(family='Calibri', size=20), justify=CENTER, height=3, background='whitesmoke', foreground='#FF204E')
        no_notice_label.pack(ipadx=10, fill=BOTH)

        re_checking_frame = Frame(inner_frame, background='whitesmoke')
        re_checking_frame.pack()

        dot_string_text = StringVar()
        re_checking_info_label = Label(re_checking_frame, text='Continuously trying every minute', font=Font(family='Calibri', size=12), justify=CENTER, height=3, background='whitesmoke', foreground='grey')
        re_checking_info_label.pack(side=LEFT, ipadx=10)

        dot_label = Label(re_checking_frame, textvariable=dot_string_text, width=3, font=Font(family='Calibri', size=15), justify=CENTER, height=3, background='whitesmoke', foreground='grey')
        dot_label.pack(side=RIGHT, ipadx=10)

        self.animate_dot(dot_string_text)

    def animate_dot(self, string_var):
        '''
        Animate '•' in classic loading fashion
        '''

        dot_symbol = '•'
        number_of_dots = string_var.get().count(dot_symbol)

        dot_numbering = number_of_dots + 1 if number_of_dots < 3 else 1
        update_dots = dot_symbol * dot_numbering

        string_var.set(update_dots)
        self.window.after(1000, lambda: self.animate_dot(string_var))

    def main(self):
        """
        Displays the GUI window containing notices and download options for PDF files
        """

        self.window = Tk()
        self.window.withdraw()
        self.window.title('BCA Results')

        self.error_text = StringVar()

        self.download_image = Image.open(utils.resource_path('download_pdf.png'))
        self.open_in_browser_image = Image.open(utils.resource_path('open_in_browser.png'))
        self.show_in_directory_image = Image.open(utils.resource_path('show_in_directory.png'))

        self.frame = Frame(self.window, background='white')
        self.frame.pack(ipadx=5, padx=(10, 0), pady=5)

        self.update_notices()

        self.window.config(background='whitesmoke')
        self.window.after(250, self.center_window)
        self.window.bind('<space>', self.Audio.pause_unpause_audio)

        self.window.config(background='white')
        self.window.mainloop()


if __name__ == '__main__':
    win = BCA_Result_Downloader()
    win.main()
