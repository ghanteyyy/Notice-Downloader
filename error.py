from tkinter import *
from tkinter.font import Font


class Error:
    def __init__(self, window, audio):
        self.Audio = audio
        self.window = window

        self.error_text_var = StringVar()
        self.is_error_message_shown = False

    def show_error(self):
        '''
        Display error messages under the following conditions:
            1. No internet connection detected
            2. No results published
        '''

        if self.is_error_message_shown is False:
            self.Audio.stop_audio()
            self.is_error_message_shown = True

            inner_frame = Frame(self.window, background='whitesmoke')
            inner_frame.pack()

            no_notice_label = Label(inner_frame, textvariable=self.error_text_var, font=Font(family='Calibri', size=20), justify=CENTER, height=3, background='whitesmoke', foreground='#FF204E')
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

        if self.is_error_message_shown:
            dot_symbol = '•'
            number_of_dots = string_var.get().count(dot_symbol)

            dot_numbering = number_of_dots + 1 if number_of_dots < 3 else 1
            update_dots = dot_symbol * dot_numbering

            string_var.set(update_dots)
            self.animate_dot_timer = self.window.after(1000, lambda: self.animate_dot(string_var))
