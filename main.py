import dropbox

from PyQt5.QtWidgets import QDialog, QMessageBox, QApplication
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
        self.progress_value = 0

    def download(self) -> None:
        """Checks if all the fields are filled out. If so, all the listed files are downloaded"""
        if not self.valid_input():
            message = QMessageBox()
            message.setText("You must enter at least one file to download.")
            message.exec_()
            return None

        # Get the list of files and turn to a list based on row breaks
        to_download = self.file_list.toPlainText().split('\n')

        # Get local savepoint
        savepoint = "."
        if self.local_savepoint.toPlainText() != '':
            savepoint = self.local_savepoint.toPlainText()

        path_to_file = f'{self.dropbox_dir.toPlainText()}'

        # Set progress bar max to reflect download progress
        self.progress_bar.setMaximum(len(to_download))

        # Connect to Dropbox and download files
        dbx = dropbox.Dropbox(self.token.toPlainText())

        # Start thread
        self.thread = QThread()
        self.worker = Worker(dbx, to_download, savepoint, path_to_file)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)

        # Connect signal for progress bar
        self.worker.report_progress.connect(self.set_progress_val)

        # Start and stop thread properly
        self.thread.start()
        self.thread.quit()

    def set_progress_val(self, val) -> None:
        """ Set the value of the progress bar to indicate percentage of files downloaded. """
        self.progress_bar.setValue(val)

    def valid_input(self) -> bool:
        """Check if the download list has at least one entry"""
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
