from os import listdir
from stone.backends.python_rsrc.stone_validators import ValidationError

import dropbox
from dropbox.exceptions import ApiError, AuthError, BadInputError
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal


class Worker(QObject):

    # Signal reporting number of files downloaded/handled
    report_progress = pyqtSignal(int)
    files_not_downloaded = pyqtSignal(list)
    thread_error = pyqtSignal(int)

    def __init__(self, dbx_object: dropbox.Dropbox,
                 to_download: list,
                 savepoint: str,
                 loadpoint: str):
        super(Worker, self).__init__()
        self.dbx = dbx_object
        self.to_download = to_download
        self.savepoint = savepoint
        self.loadpoint = loadpoint
        self.failed_dowloads = []

        self.progress = 0

    def run(self) -> None:
        """ Downloads the provided list of files from Dropbox """
        for file in self.to_download:
            try:
                self.download_file(file)

            except FileNotFoundError:
                '''If the directory to save to does not exist'''
                self.thread_error.emit(1)
                break

            except ValidationError:
                '''If the Dropbox directory requested does note exist'''
                self.thread_error.emit(2)
                break

            except AuthError:
                '''If the token is expired'''
                self.thread_error.emit(3)
                break

            except BadInputError:
                '''If the token is not the correct form.'''
                self.thread_error.emit(4)
                break

            except Exception:
                '''Unknown Error'''
                self.thread_error.emit(5)
                break


        else:
                self.progress += 1
                self.report_progress.emit(self.progress)

        self.files_not_downloaded.emit(self.failed_dowloads)

    def download_file(self, filename: str) -> None:
        """Downloads a given file from the specified Dropbox directory"""

        # Do not download if file by the same name is already in directory
        files_in_dir = listdir(self.savepoint)
        if filename in files_in_dir:
            print(f"File {filename} already in directory. Skipping")
            return None

        file_to_load = f'/{self.loadpoint}/{filename}'
        file_to_save = f'{self.savepoint}/{filename}'

        # Try to download
        try:
            metadata, file = self.dbx.files_download(file_to_load)
            with open(file_to_save, 'wb') as a:
                a.write(file.content)
            print(f"{filename} downloaded successfully.")
        except ApiError:
            print(f"File '{filename}' not found. Skipping.")
            self.failed_dowloads.append(filename)
