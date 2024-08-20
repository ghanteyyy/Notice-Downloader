from PIL import Image, ImageTk
from Functions import utils

class Images:
    def __init__(self):
        self.icon_image = self.resize_image(utils.resource_path('icon.png', 'Images'), (0, 0))
        self.delete_image = self.resize_image(utils.resource_path('delete.png', 'Images'))
        self.download_pdf_image = self.resize_image(utils.resource_path('download_pdf.png', 'Images'))
        self.setting_image = self.resize_image(utils.resource_path('settings.png', 'Images'), (25, 25))
        self.go_to_back_image = self.resize_image(utils.resource_path('go_to_back.png', 'Images'), (30, 30))
        self.open_in_browser_image = self.resize_image(utils.resource_path('open_in_browser.png', 'Images'))
        self.show_in_directory_image = self.resize_image(utils.resource_path('show_in_directory.png', 'Images'))

    def resize_image(self, image_path, size=(20, 20)):
        """
        Resize the given image to the specified size using Lanczos resampling
        """

        image = Image.open(image_path)

        if size[0] != 0 and size[1] != 0:
            image = image.resize(size, Image.Resampling.LANCZOS)

        image = ImageTk.PhotoImage(image)

        return image
