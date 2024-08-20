import time
import threading
from tkinter import *
import tkinter.ttk as ttk
from tkinter.font import Font
from Functions import notices, utils, images, writer
from GUI import error


class BCA_Notice_Downloader:
    def __init__(self):
        self.is_error_showing = False
        self.Notices = notices.Notices()
        self.JSON_Writer = writer.JSON()
        self.Notices.start_fetching_notices()

        self.window = Tk()
        self.window.withdraw()
        self.window.resizable(0, 0)
        self.window.title('BCA notice downloader')
        self.window.iconphoto(False, images.Images().icon_image)

        self.root_frame = Frame(self.window)
        self.root_frame.pack(pady=5)

        self.error_thread = threading.Thread(target=self.check_for_any_errors, daemon=True)
        self.error_thread.start()

        self.window.after(1500, self.window.deiconify)
        self.window.protocol('WM_DELETE_WINDOW', self.quit)
        self.window.bind('<Control-d>', self.JSON_Writer.clear_json)
        self.window.mainloop()

    def check_for_any_errors(self):
        '''
        Periodically checks for errors every 5 seconds
        '''

        while True:
            notices = self.Notices.data

            if utils.is_internet() is False and self.is_error_showing is False:
                self.Notices.data = []
                self.is_error_showing = True
                self.Error = error.Error(self.window, 'Unable to connect to the internet ', 'Reconnecting')
                self.Error.start_error_animation()

            elif not notices and self.is_error_showing is False:
                self.is_error_showing = True
                self.Error = error.Error(self.window, 'No notices have been published as of yet !!!', 'Fetching')
                self.Error.start_error_animation()

            else:
                if self.is_error_showing and notices:
                    self.populate_notices()

            time.sleep(5)

    def populate_notices(self):
        """
        Displays a list of fetched notices, allowing users to view and
        interact with each notice's details and available actions.
        """

        self.is_error_showing = False
        self.Error.stop_error_animation()

        for notice in self.Notices.data:
            notice_frame = Frame(self.root_frame, background='#43766C')
            notice_frame.pack(padx=5, pady=(8, 0), ipady=15, fill='both')

            date_label = Label(notice_frame, text=notice['date'], anchor='c', background='#43766C', foreground='whitesmoke', font=Font(family='Calibri', size=15))
            date_label.pack(side=LEFT, ipadx=5)

            date_separator = ttk.Separator(notice_frame, orient=VERTICAL)
            date_separator.pack(side=LEFT, fill='y')

            notice_label = Label(notice_frame, text=notice['notice_name'].strip('.pdf'), anchor='w', background='#43766C', foreground='whitesmoke', font=Font(family='Calibri', size=15))
            notice_label.pack(side=LEFT, padx=5, ipadx=10, expand=True, fill='x')

            buttons_frame = Frame(notice_frame, background='#e6e6e6', highlightbackground="#cfcfcf", highlightthickness=3)
            buttons_frame.pack(side=LEFT, fill='y')

            # If True: The notice has been successfully downloaded. Display three buttons:
            # - "Open PDF in Browser": Opens the downloaded PDF in the default web browser.
            # - "Open PDF in Explorer": Opens the folder containing the PDF in the file explorer.
            # - "Delete": Deletes the downloaded PDF.
            #
            # If False: The notice has not been downloaded. Display a "Download" button to initiate the download.
            #
            # 'image': Refers to the graphical icon or image associated with each button.
            # 'command': Refers to the function or action triggered when the corresponding button is clicked.
            buttons_lists = {
                True: {
                    'open_in_browser': {
                        'image': images.Images().open_in_browser_image,
                        'command': lambda event=Event, pdf_name=notice['notice_name']: self.Notices.show_notice_in_browser(event, pdf_name)
                    },

                    'open_in_explorer': {
                        'image': images.Images().show_in_directory_image,
                        'command': lambda event=Event, pdf_name=notice['notice_name']: self.Notices.show_notice_location_in_explorer(event, pdf_name)
                    },

                    'delete': {
                        'image': images.Images().delete_image,
                        'command': lambda event=Event, notice_frame=notice_frame, pdf_name=notice['notice_name']: self.delete_notice(event, notice_frame, pdf_name)
                    }
                },
                False: {
                    'download': {
                        'command': None,
                        'image': images.Images().download_pdf_image
                    }
                }
            }

            # Attach the download command to the "Download" button if the notice has not been downloaded.
            # This command is added here instead of earlier because the 'buttons_list' needs to be fully populated
            # before being passed to the attach_buttons method, which is responsible for packing the necessary buttons.
            buttons_lists[False]['download']['command'] = lambda event=Event, pdf_link=notice['download_link'], button_frame=buttons_frame, buttons=buttons_lists[True]: self.download_notice(event, pdf_link, button_frame, buttons)
            buttons = buttons_lists[notice['is_notice_downloaded']]

            self.attach_buttons(buttons_frame, buttons)

    def attach_buttons(self, button_frame, buttons):
        '''
        Attaches and displays the specified buttons onto the provided button_frame for user interaction
        '''

        for _, img in buttons.items():
            button = Label(button_frame, image=img['image'], anchor='c', cursor='hand2', background='#e6e6e6')
            button.pack(expand=True, fill='y', padx=(5, 0))
            button.image = img

            button.bind('<Button-1>', img['command'])

    def download_notice(self, event, pdf_link, buttons_frame, buttons):
        """
        Handles the download process triggered by the user's click,
        retrieves the PDF from pdf_link, saves it, and replaces the
        download button with options to open the PDF in a browser,
        view it in Explorer, or delete it.
        """


        for child in buttons_frame.winfo_children():
            child.destroy()

        self.attach_buttons(buttons_frame, buttons)

        self.Notices.download_notice(event, pdf_link)

    def delete_notice(self, event, notice_frame, pdf_name):
        self.JSON_Writer.write_json(pdf_name)

        notice_frame.destroy()
        self.Notices.delete_notice(pdf_name)

    def quit(self):
        """
        Terminates the data fetching process and closes the application window
        """

        self.Notices.continue_fetch_data = False
        self.window.destroy()


if __name__ == "__main__":
    BCA_Notice_Downloader()