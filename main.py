from os import listdir
from stone.backends.python_rsrc.stone_validators import ValidationError

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
        self.abort_button.clicked.connect(self.quit)


    def download_file(self, filename: str, dbx: dropbox.Dropbox) -> None:
        '''Downloads a given file from the specified Dropbox directory'''

        savepoint = "."
        if self.local_savepoint.toPlainText() != '':
            savepoint = self.local_savepoint.toPlainText()

        path_to_file = f'{self.dropbox_dir.toPlainText()}/{filename}'
        save_path = f'{savepoint}/{filename}'

        # Do not download if file by the same name is already in directory
        files_in_dir = listdir(savepoint)
        if filename in files_in_dir:
            print(f"File {filename} already in directory. Skipping")

        # Try to download
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
            message.setText("You must enter at least one file to download.")
            message.exec_()
            return None

        #Get the list of files and turn to a list based on breakrows
        to_download = self.file_list.toPlainText().split('\n')

        #Connect to Dropbox and download files
        dbx = dropbox.Dropbox(self.token.toPlainText())

        for file in to_download:
            try:
                self.download_file(file, dbx)
            except FileNotFoundError:
                '''If the directory to save to does not exist'''
                message = QMessageBox()
                message.setText(f"Save directory does not exist for file: {file}")
                message.exec_()
                return None
            except ValidationError:
                '''If the Dropbox directory requested does note exist'''
                message = QMessageBox()
                message.setText(f"Dropbox directory does not exist for file: {file}")
                message.exec_()
                return None
            else:
                print(f"{file} downloaded successfully.")



    def valid_input(self) -> bool:
        '''Check if the download list has at least one entry'''
        if self.file_list.toPlainText() == '':
            return False
        else:
            return True

    def quit(self) -> None:
        self.close()


def main():
    app = QApplication([])
    window = GUI()
    app.exec_()


if __name__ == "__main__":
    main()
