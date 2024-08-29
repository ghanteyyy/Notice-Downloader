from tkinter import *
from tkinter.font import Font


class Error:
    def __init__(self, root, previous_frame, error_title, animate_prefix):
        self.root = root
        self.error_title = error_title
        self.previous_frame = previous_frame
        self.animate_prefix = animate_prefix

        self.dot_counter = 0
        self.is_being_animated = None
        self.label_attributes = {"justify": CENTER, "height": 3, "foreground": 'grey'}

    def start_error_animation(self):
        '''
        Display error messages
        '''

        self.error_frame = Frame(self.previous_frame)
        self.error_frame.pack(padx=10, pady=10, fill='x')

        self.error_title_label = Label(self.error_frame, text=self.error_title, font=Font(size=20, weight='bold'), **self.label_attributes)
        self.error_title_label.pack(padx=10, pady=10)

        self.reconnecting_frame = Frame(self.error_frame)
        self.reconnecting_frame.pack(padx=10, pady=10)

        self.dot_label_var = StringVar(value=self.animate_prefix)

        self.reconnecting_label = Label(self.reconnecting_frame, text=self.animate_prefix, font=Font(size=15), **self.label_attributes)
        self.reconnecting_label.pack(side=LEFT, padx=(20, 0))
        self.dot_label = Label(self.reconnecting_frame, textvariable=self.dot_label_var, font=Font(size=15), **self.label_attributes, width=5, anchor='w')
        self.dot_label.pack(side=LEFT)

        self.animate()

    def animate(self):
        '''
        Animate '●' in classic loading fashion
        '''

        if self.dot_counter == 4:
            self.dot_counter = 1

        value = ' ●' * self.dot_counter
        self.dot_label_var.set(value)

        self.dot_counter += 1
        self.is_being_animated = self.root.after(1000, self.animate)

    def stop_error_animation(self):
        '''
        Stop showing error message
        '''

        self.error_frame.destroy()
        self.root.after_cancel(self.is_being_animated)