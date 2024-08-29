import time
import threading
from tkinter import *
import tkinter.ttk as ttk
from tkinter.font import Font
from GUI.scrollable_frame import ScrollableFrame
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

        self.root_frame = ScrollableFrame(self.window)
        self.root_frame.pack(pady=5, fill=BOTH, expand=True)

        self.error_thread = threading.Thread(target=self.check_for_any_errors, daemon=True)
        self.error_thread.start()

        self.window.after(2000, self.initial_position)
        self.window.protocol('WM_DELETE_WINDOW', self.quit)
        self.window.bind('<Control-d>', self.JSON_Writer.clear_json)
        self.window.mainloop()

    def initial_position(self):
        '''
        Sets the initial position of the window when it is
        placed on the screen for the first time
        '''

        self.window.update_idletasks()

        window_width = self.window.winfo_reqwidth()
        window_height = self.window.winfo_reqheight()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        winfo_x = screen_width // 2 - window_width // 2
        winfo_y = screen_height // 2 - window_height // 2

        self.window.geometry(f'+{winfo_x}+{winfo_y}')
        self.window.deiconify()

    def check_for_any_errors(self):
        '''
        Periodically checks for errors every 5 seconds
        '''

        while True:
            notices = self.Notices.data

            if utils.is_internet() is False and self.is_error_showing is False:
                self.Notices.data = []
                self.is_error_showing = True
                self.Error = error.Error(self.window, self.root_frame.scrollable_frame, 'Unable to connect to the internet ', 'Reconnecting')
                self.Error.start_error_animation()

            elif not notices and self.is_error_showing is False:
                self.is_error_showing = True
                self.Error = error.Error(self.window, self.root_frame.scrollable_frame, 'Please wait, the notices are currently being fetched.\nThis process may take a moment', 'Fetching')
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

        label_attributes = {'background': '#43766C', 'foreground': 'whitesmoke', 'font': Font(family='Calibri Light', size=15)}

        for widget in self.root_frame.scrollable_frame.winfo_children():
            widget.destroy()

        for notice in self.Notices.data:
            notice_frame = Frame(self.root_frame.scrollable_frame, background='#43766C')
            notice_frame.pack(padx=5, pady=(8, 0), ipady=15, fill='both')

            date_label = Label(notice_frame, text=notice['date'], anchor='c', **label_attributes)
            date_label.pack(side=LEFT, ipadx=5)

            date_separator = ttk.Separator(notice_frame, orient=VERTICAL)
            date_separator.pack(side=LEFT, fill='y')

            notice_label = Label(notice_frame, text=notice['notice_name'].strip('.pdf'), justify='left', wraplength=500, anchor='w', **label_attributes)
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
        """
        Deletes a notice from the view and records the name of the deleted PDF.
        This ensures that the PDF will not be re-added when fetching notices in the future.
        """

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