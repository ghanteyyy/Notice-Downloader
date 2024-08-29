from tkinter import *


class ScrollableFrame(Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.canvas = Canvas(self)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.scrollbar = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollable_frame = Frame(self.canvas)

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.scrollable_frame.bind("<Configure>", self.configure)

    def _on_mousewheel(self, event):
        '''
        When user changes mousewheel inside the scrollable frame
        '''

        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    def set_maximum_inner_frame_width(self):
        '''
        Set the canvas width to the maximum size of the inner frame
        '''

        max_width = 0

        for children in self.scrollable_frame.winfo_children():
            if children:
                width = children.winfo_width()

                if width and width > max_width:
                    max_width = width

                    self.canvas.config(width=max_width)

    def configure(self, event):
        '''
        Adjust the scrollable region of the canvas to encompass all content within it
        '''

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.set_maximum_inner_frame_width()
