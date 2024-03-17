import dropbox
from PyQt5.QtWidgets import QDialog, QMessageBox, QApplication
from PyQt5 import uic
from PyQt5.QtCore import QThread
from Thread import Worker


class GUI(QDialog):
    def __init__(self):
        super(GUI, self).__init__()
        uic.loadUi("layout.ui", self)
        self.show()

        self.download_button.clicked.connect(self.download)
        self.quit_button.clicked.connect(self.quit)
        self.abort_button.clicked.connect(self.quit)
        # TODO: Implement the functionality for the progressbar and abort button

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

        # Connect to Dropbox and download files
        try:
            dbx = dropbox.Dropbox(self.token.toPlainText())
        except dropbox.dropbox_client.BadInputException:
            message = QMessageBox()
            message.setText("The provided access token is valid")
            message.exec_()
            return None

        self.thread = QThread()
        self.worker = Worker(dbx, to_download, savepoint, path_to_file)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()
        self.thread.quit()

    def valid_input(self) -> bool:
        """Check if the download list has at least one entry"""
        if self.file_list.toPlainText() == '':
            return False
        else:
            return True

    def quit(self) -> None:
        """Close the GUI"""
        self.close()


def main():
    """Launch GUI"""
    app = QApplication([])
    window = GUI()
    app.exec_()


if __name__ == "__main__":
    main()
