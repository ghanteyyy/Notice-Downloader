import os
from tkinter import *
from tkinter.font import Font
from PIL import ImageTk, Image
import pygame
from notices import Notices


class BCA_Result_Downloader:
    def __init__(self):
        self.is_paused = False
        self.Notices = Notices()
        self.icon_image = Image.open(self.Notices.resource_path('icon.jpg'))

    def play_audio(self):
        '''
        Play audio if any notice gets retrieved
        '''

        pygame.mixer.init()

        audio_file = self.Notices.resource_path('sound.mp3')
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play(loops=-1)

    def pause_unpause_audio(self, event):
        '''
        Pause or unpause audio when pressed space key
        '''

        if self.is_paused:
            pygame.mixer.music.unpause()

        else:
            pygame.mixer.music.pause()

        self.is_paused = not self.is_paused

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

    def show_in_folder(self, event, location):
        """
        Opens the folder containing the specified location

        Args:
            - event: The event triggering the function call (not used)
            - location (str): The path of the location to be revealed in the explorer
        """

        self.Notices.reveal_in_explorer(event, location)

    def download_pdf(self, event, pdf_link):
        """
        Downloads the PDF file from the specified link and updates the GUI accordingly

        Args:
            - event: The event triggering the function call (not used)
            - pdf_link (str): The URL or path of the PDF file to be downloaded
        """

        self.Notices.download_pdf(event, pdf_link)

        pdf_basename = os.path.basename(pdf_link)
        img = self.resize_image(self.show_in_directory_image)

        binding_function = lambda event=Event, location=pdf_basename: self.show_in_folder(event, location)
        event.widget.unbind('<Button-1>')
        event.widget.bind('<Button-1>', binding_function)

        event.widget.config(image=img)
        event.widget.image = img

    def center_window(self):
        '''
        Set position of the window to the center of the screen when user open the program
        '''

        self.window.update()
        self.window.iconphoto(False, ImageTk.PhotoImage(self.icon_image))

        width, height = self.window.winfo_width(), self.window.winfo_height()
        screenwidth, screenheight = self.window.winfo_screenwidth() // 2, self.window.winfo_screenheight() // 2
        self.window.geometry(f'{width}x{height}+{screenwidth - width // 2}+{screenheight - height // 2}')

        self.window.resizable(0, 0)
        self.window.deiconify()

        if self.retrieved_notices:
            self.play_audio()

        self.window.resizable(False, False)

    def main(self):
        """
        Displays the GUI window containing notices and download options for PDF files
        """

        self.retrieved_notices = self.Notices.get_notices()

        self.window = Tk()
        self.window.withdraw()
        self.window.title('BCA Results')

        self.download_image = Image.open(self.Notices.resource_path('download_pdf.png'))
        self.show_in_directory_image = Image.open(self.Notices.resource_path('show_in_directory.png'))

        self.mute_unmute_label = Label(self.window, text="Press <space> to pause and unpause audio", justify=CENTER, font=('Courier', 10))
        self.mute_unmute_label.pack(ipady=5)

        for notice in self.retrieved_notices:
            notice_name = notice['notice_name']

            if notice['is_pdf_downloaded']:
                image = self.show_in_directory_image
                binding_function = lambda event=Event, location=notice_name: self.show_in_folder(event, location)

            else:
                image = self.download_image
                binding_function = lambda event=Event, pdf_link=notice['download_link']: self.download_pdf(event, pdf_link)

            image = self.resize_image(image)

            self.frame = Frame(self.window)

            self.notice_label = Label(self.frame, text=notice_name, font=Font(family='Calibri', size=15), wraplength=500, justify=CENTER, height=3, background='#43766C', foreground='whitesmoke')
            self.notice_label.pack(side=LEFT, ipadx=5, fill=BOTH)

            self.download_button = Label(self.frame, image=image, relief=FLAT, cursor='hand2')
            self.download_button.pack(side=RIGHT, fill=Y, ipadx=10)
            self.download_button.bind('<Button-1>', binding_function)

            self.frame.pack(ipadx=5, ipady=5, padx=(10, 0), pady=10)


        self.window.config(background='whitesmoke')
        self.window.after(250, self.center_window)
        self.window.bind('<space>', self.pause_unpause_audio)

        self.window.mainloop()


if __name__ == '__main__':

    win = BCA_Result_Downloader()
    win.main()
