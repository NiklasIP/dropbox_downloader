from datetime import datetime

import dropbox

from PyQt5.QtWidgets import QDialog, QMessageBox, QApplication, QFileDialog, QButtonGroup
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal
from Thread import Worker

class GUI(QDialog):
    def __init__(self):
        super(GUI, self).__init__()
        uic.loadUi("layout.ui", self)
        self.show()

        self.download_button.clicked.connect(self.download)
        self.quit_button.clicked.connect(self.quit)
        self.abort_button.clicked.connect(self.quit)
        self.folder_button.clicked.connect(self.set_download_folder)
        self.clear_files_button.clicked.connect(self.clear_files)

        self.button_group = QButtonGroup()
        self.button_group.addButton(self.goholm_button)
        self.button_group.addButton(self.ottenby_button)
        self.button_group.addButton(self.other_button)

        self.goholm_button.toggled.connect(self.set_locale)
        self.ottenby_button.toggled.connect(self.set_locale)
        self.other_button.toggled.connect(self.set_locale)

        self.selected_year.setPlainText(datetime.now().strftime("%Y")) # Set current year as default
        self.progress_value = 0
        self.locale = ''

    def download(self) -> None:
        """Checks if all the fields are filled out. If so, all the listed files are downloaded"""
        if not self.valid_input():
            message = QMessageBox()
            message.setText("You must enter at least one file to download.")
            message.exec_()
            return None

        # Get the list of files and turn to a list based on row breaks
        self.to_download = self.file_list.toPlainText().split('\n')

        # Get local savepoint
        savepoint = "."
        if self.local_savepoint.toPlainText() != '':
            savepoint = self.local_savepoint.toPlainText()


        # Construct the correct directory path in dropbox
        if self.locale == "Other":
            path_to_file = f'{self.other_locale.toPlainText()}'
        else:
            path_to_file = f'{self.locale}/{self.selected_year.toPlainText()}'

        # Set progress bar max to reflect download progress
        self.progress_bar.setMaximum(len(self.to_download))

        # Connect to Dropbox and download files
        dbx = dropbox.Dropbox(self.token.toPlainText())

        # Start thread
        self.thread = QThread()
        self.worker = Worker(dbx, self.to_download, savepoint, path_to_file)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)

        # Connect signal for progress bar
        self.worker.report_progress.connect(self.set_progress_val)

        # Connect signal for errors
        self.worker.thread_error.connect(self.display_error_message)

        # Connect to signal to get list of failed downloads
        self.worker.files_not_downloaded.connect(self.get_failed_downloads)

        # Start and stop thread properly
        self.thread.start()
        self.thread.quit()




    def set_download_folder(self) -> None:
        """ Gets the download folder from a dialog box and updates the download path in the GUI"""
        # open the QFileDialog to select the download folder
        download_folder = QFileDialog.getExistingDirectory()
        # update local_savepoint box with the download folder
        self.local_savepoint.setPlainText(download_folder)


    def set_progress_val(self, val) -> None:
        """ Set the value of the progress bar to indicate percentage of files downloaded. """
        self.progress_value = val
        self.progress_bar.setValue(self.progress_value)


    def get_failed_downloads(self, failed_downloads) -> None:
        """Open a dialog box with failed downloads if any"""
        if len(failed_downloads) > 0:
            message_box = QMessageBox()
            #use chr(10) for new row as backslashes not allowed in fstrings
            message = f"Failed to download the following files:\n {chr(10).join(str(x) for x in failed_downloads)}"
            message_box.setText(message)
            message_box.exec_()
    def display_error_message(self, error_code) -> None:
        error_messages = {1: "Save directory does not exist.",
                          2: "Dropbox directory does not exist.",
                          3: "The authentication token you are using has expired.",
                          4: "The authentication token you have entered is malformed",
                          5: """You have encountered an unknown error. That is quite impressive.
                          Please submit a detailed description of what you did to get here."""}

        message = QMessageBox()
        message.setText(error_messages[error_code])
        message.exec_()


    def valid_input(self) -> bool:
        """Check if the download list has at least one entry"""
        if self.file_list.toPlainText() == '':
            return False
        else:
            return True

    def clear_files(self) -> None:
        self.file_list.setPlainText('')

    def set_locale(self)-> None:
        radioBtn = self.sender()
        if radioBtn.isChecked():
            self.locale = radioBtn.text()

            if self.locale == "Other":
                self.other_locale.setEnabled(True)
            else:
                self.other_locale.setEnabled(False)
    def quit(self) -> None:
        self.close()


def main():
    app = QApplication([])
    window = GUI()
    app.exec_()


if __name__ == "__main__":
    main()
