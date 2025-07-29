# main_screen.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QDialog
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import QProgressBar
import math


class ProgressBarDialog(QDialog):
    finished = pyqtSignal()  # signal to indicate processing is finished

    def __init__(self, chp_amount=1, parent=None):
        super().__init__(parent)
        self.chp_amount = max(1, chp_amount)
        self.current_checkpoint = 0
        self.setup_ui()
        self.setup_progress_bar()

    def setup_ui(self):
        self.setWindowTitle("Processing...")
        self.setModal(True)
        self.setFixedSize(400, 150)

        layout = QVBoxLayout()

        # title label
        self.status_label = QLabel("Processing files...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

        # Goal value for the progress bar
        self.target_value = 100 / self.chp_amount

        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_progress)

    def setup_progress_bar(self):
        self.progress_bar.setValue(0)
        self.current_checkpoint = 0
        self.target_value = 100 / self.chp_amount if self.chp_amount > 0 else 100

    def start_progress(self):
        # start the progress bar and timer
        self.setup_progress_bar()
        self.timer.start()
        self.show()

    def update_progress(self):
        current_value = self.progress_bar.value()

        if current_value < self.target_value:
            # calculate the distance to the target value
            distance_to_target = self.target_value - current_value

            # use exponential step size based on distance
            step = max(0.1, distance_to_target * 0.05)

            new_value = current_value + step

            if new_value >= self.target_value:
                new_value = self.target_value
                self.progress_bar.setValue(new_value)
                self.timer.stop()
            else:
                self.progress_bar.setValue(new_value)

    def complete_checkpoint(self):
        # complete the current checkpoint and move to the next one
        if self.current_checkpoint < self.chp_amount - 1:
            self.current_checkpoint += 1
            self.target_value = (self.current_checkpoint + 1) * (100 / self.chp_amount)

            if not self.timer.isActive():
                self.timer.start()
        else:
            self.progress_bar.setValue(100)
            self.timer.stop()
            self.finished.emit()  # emit signal that processing is finished
            self.close()

    def reset_progress(self):
        # reset the progress bar to the initial state
        self.timer.stop()
        self.setup_progress_bar()
        self.timer.start()

    def update_status(self, text):
        # update the status label with the given text
        self.status_label.setText(text)


class MainScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_file_paths = []
        self.progress_dialog = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)

        # title
        title_label = QLabel("DeuCards")
        title_label.setStyleSheet("font-size: 48px; font-weight: bold; color: white;")
        layout.addWidget(title_label)

        # subtitle
        subtitle_label = QLabel("Create smart German Anki decks automatically")
        subtitle_label.setStyleSheet("font-size: 28px; color: #aaaaaa;")
        layout.addWidget(subtitle_label)

        # display selected file paths
        self.path_label = QLabel("No file selected")
        self.path_label.setStyleSheet("font-size: 24px; color: #999999;")
        self.path_label.setWordWrap(True)
        layout.addWidget(self.path_label)

        self.setLayout(layout)

    def update_path_display(self):
        # updates the label to show the currently selected file paths
        count = len(self.current_file_paths)
        if count == 0:
            self.path_label.setText("No files selected")
            self.path_label.setToolTip("")
        elif count == 1:
            path = self.current_file_paths[0]
            filename = path.split("/")[-1]
            self.path_label.setText(f"Selected:\n{filename}")
            self.path_label.setToolTip(path)
        else:
            self.path_label.setText(f"Selected {count} files")
            tooltip_text = "\n".join([p.split("/")[-1] for p in self.current_file_paths])
            self.path_label.setToolTip(f"Files:\n{tooltip_text}")

    def open_file_dialog(self):
        # creates a file dialog to select multiple files
        from PyQt5.QtWidgets import QFileDialog

        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files (PDF, Images)",
            "",
            "Supported Files (*.pdf *.png *.jpg *.jpeg);;"
            "PDF Files (*.pdf);;"
            "Image Files (*.png *.jpg *.jpeg);;"
            "All Files (*)"
        )

        if file_paths:
            self.current_file_paths = file_paths
            self.update_path_display()
            print(f"[DEBUG] Selected files: {self.current_file_paths}")

    def get_current_file_paths(self):
        # returns a copy of the current file paths to avoid external modifications
        return self.current_file_paths.copy()