from os import listdir
from stone.backends.python_rsrc.stone_validators import ValidationError

import dropbox
from dropbox.exceptions import ApiError
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal


class Worker(QObject):

    # Signal reporting number of files downloaded/handled
    report_progress = pyqtSignal(int)

    def __init__(self, dbx_object: dropbox.Dropbox,
                 to_download: list,
                 savepoint: str,
                 loadpoint: str):
        super(Worker, self).__init__()
        self.dbx = dbx_object
        self.to_download = to_download
        self.savepoint = savepoint
        self.loadpoint = loadpoint

        self.progress = 0

    def run(self) -> None:
        """ Downloads the provided list of files from Dropbox """
        for file in self.to_download:
            try:
                self.download_file(file)
            except FileNotFoundError:
                '''If the directory to save to does not exist'''
                message = QMessageBox()
                message.setText(f"Save directory does not exist for file: {file}")
                message.exec_()
            except ValidationError:
                '''If the Dropbox directory requested does note exist'''
                message = QMessageBox()
                message.setText(f"Dropbox directory does not exist for file: {file}")
                message.exec_()
            finally:
                self.progress += 1
                self.report_progress.emit(self.progress)

    def download_file(self, filename: str) -> None:
        """Downloads a given file from the specified Dropbox directory"""

        # Do not download if file by the same name is already in directory
        files_in_dir = listdir(self.savepoint)
        if filename in files_in_dir:
            print(f"File {filename} already in directory. Skipping")
            return None

        file_to_load = f'{self.loadpoint}/{filename}'
        file_to_save = f'{self.savepoint}/{filename}'

        # Try to download
        try:
            metadata, file = self.dbx.files_download(file_to_load)
            with open(file_to_save, 'wb') as a:
                a.write(file.content)
            print(f"{filename} downloaded successfully.")
        except ApiError:
            print(f"File '{filename}' not found. Skipping.")
