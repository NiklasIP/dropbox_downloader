import sys

import dropbox
from dropbox.exceptions import ApiError
from PyQt5.QtWidgets import *
from PyQt5 import uic

class GUI(QDialog):
    def __init__(self):
        super(GUI, self).__init__()
        uic.loadUi("layout.ui", self)
        self.show()

        self.download_button.clicked.connect(self.download)
        self.quit_button.clicked.connect(self.quit)

    def download_file(self, filename: str, dbx: dropbox.Dropbox) -> None:
        '''Downloads a given file from the specified Dropbox directory'''
        path_to_file = f'{self.dropbox_dir.toPlainText()}/{filename}'
        save_path = f'{self.local_savepoint.toPlainText()}/{filename}'

        # TODO: Do not download if file is already in directory
        # TODO: Catch more kinds of errors
        try:
            metadata, file = dbx.files_download(path_to_file)
            with open(save_path, 'wb') as a:
                a.write(file.content)
        except ApiError as e:
            print(f"File '{filename}' not found. Skipping.")

    def download(self) -> None:
        '''Checks if all the fields are filled out. If so, all the listed files are downloaded'''
        if not self.valid_input():
            message = QMessageBox()
            message.setText("Only the Dropbox directory may be left empty.")
            message.exec_()
            return None

        # TODO: Check if save directory exists

        #Get the list of files and turn to a list based on breakrows
        to_download = self.file_list.toPlainText().split('\n')

        #Connect to Dropbox and download files
        dbx = dropbox.Dropbox(self.token.toPlainText())
        for file in to_download:
            self.download_file(file, dbx)

    def valid_input(self) -> bool:
        '''Check if all the text fields have been filled out'''
        if self.file_list.toPlainText() == '':
            return False
        elif self.token.toPlainText() == '':
            return False
        elif self.local_savepoint.toPlainText() == '':
            return False
        else:
            return True

    def quit(self):
        sys.exit()


def main():
    app = QApplication([])
    window = GUI()
    app.exec_()


if __name__ == "__main__":
    main()
