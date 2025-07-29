# main_window.py
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QMenuBar, QMenu, QAction, QTextEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
import traceback
from custom_dialog import SingleInputDialog, ConfirmationDialog
from anki_utils import create_s_deck, create_v_deck
from source_to_txt_utils import extract_text_from_pdf, extract_text_from_image
from ai_utils import clean_tokenized_text, extract_verbs, extract_except_verbs
from settings_screen import SettingsScreen
from styles import APP_STYLE
from main_screen import MainScreen, ProgressBarDialog
import os


# --- Worker Class Definition ---
class TextProcessingWorker(QObject):
    """
    Worker object that performs the text processing in a background thread.
    Emits signals to communicate progress, results, errors, and completion.
    """
    progress = pyqtSignal(int, str)  # Signal to update progress: (stage_number, status_text)
    result_ready = pyqtSignal(str, str)  # Signal when processing is done: (verbs_text, except_verbs_text)
    error_occurred = pyqtSignal(str)  # Signal if an error happens: (error_message)
    finished = pyqtSignal()  # Signal when the worker has finished its run

    def __init__(self, file_paths):
        super().__init__()
        self.file_paths = file_paths
        self._is_running = True  # Flag to potentially allow cancellation (optional)

    @pyqtSlot()
    def run(self):
        """The main processing logic, run in the worker thread."""
        try:
            # --- Stage 1: Extract Text ---
            if not self._is_running:
                return
            self.progress.emit(1, "Extracting text from files...")
            text = ""
            for path in self.file_paths:
                if not self._is_running:
                    return  # Check flag periodically
                if ".pdf" in path:
                    text += extract_text_from_pdf(path)
                else:
                    text += extract_text_from_image(path)

            # --- Stage 2: Clean Text ---
            if not self._is_running:
                return
            self.progress.emit(2, "Cleaning and tokenizing text...")
            cleaned_text = clean_tokenized_text(text)

            # --- Stage 3: Extract Verbs ---
            if not self._is_running:
                return
            self.progress.emit(3, "Extracting verbs...")
            verbs_text = extract_verbs(cleaned_text)

            # --- Stage 4: Extract Other Words ---
            if not self._is_running:
                return
            self.progress.emit(4, "Extracting other words and phrases...")
            except_verbs_text = extract_except_verbs(cleaned_text)

            # --- Stage 5: Signal Completion ---
            if not self._is_running:
                return
            self.progress.emit(5, "Finalizing...")
            # Emit the results
            self.result_ready.emit(verbs_text, except_verbs_text)
        except Exception as e:
            # If an error occurs, emit the error signal
            error_message = f"Error during processing: {str(e)}\n{traceback.format_exc()}"
            self.error_occurred.emit(error_message)
        finally:
            # Always emit finished when the run method ends
            self.finished.emit()
            self._is_running = False  # Ensure flag is reset


# --- Worker Class for Deck Creation ---
class DeckCreationWorker(QObject):
    progress = pyqtSignal(int, str)  # (stage, status)
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, vtext, stext, label):
        super().__init__()
        self.vtext = vtext
        self.stext = stext
        self.label = label
        self._is_running = True

    @pyqtSlot()
    def run(self):
        try:
            base_path = "C:/Users/GANT-NB/Music/anki/sources/"

            if not self._is_running:
                return
            self.progress.emit(1, "Saving verbs.txt...")
            with open(f"{base_path}verbs {self.label}.txt", "w", encoding="utf-8") as f:
                f.write(self.vtext)

            if not self._is_running:
                return
            self.progress.emit(2, "Saving subs.txt...")
            with open(f"{base_path}subs {self.label}.txt", "w", encoding="utf-8") as f:
                f.write(self.stext)

            if not self._is_running:
                return
            self.progress.emit(3, "Creating verb deck...")
            create_v_deck(self.label)

            if not self._is_running:
                return
            self.progress.emit(4, "Creating noun/adjective deck...")
            create_s_deck(self.label)

            if not self._is_running:
                return
            self.progress.emit(5, "Finalizing...")
        except Exception as e:
            error_msg = f"Error creating decks: {str(e)}\n{traceback.format_exc()}"
            self.error_occurred.emit(error_msg)
        finally:
            self.finished.emit()

# --- MainWindow Class ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EN-DEU Deck Creator")
        self.setWindowIcon(QIcon("icons/app_icon.png"))
        self.resize(1000, 600)
        # list to hold text editors
        self.text_editors = []
        # qstacked widget to hold different screens
        self.stackedWidget = QStackedWidget(self)
        self.setCentralWidget(self.stackedWidget)
        # create screens
        self.main_screen = MainScreen(self)
        self.settings_screen = SettingsScreen(self)
        # add screens to the stacked widget
        self.stackedWidget.addWidget(self.main_screen)  # index 0
        self.stackedWidget.addWidget(self.settings_screen)  # index 1
        # menu bar
        self.create_menu_bar()
        # style the main window
        self.setStyleSheet(APP_STYLE)
        # --- For Threading ---
        self.progress_dialog = None  # Keep track of the dialog instance
        self.worker_thread = None  # Keep track of the worker thread
        self.worker = None  # Keep track of the worker object

    def create_menu_bar(self):
        self.menubar = QMenuBar(self)
        self.menuFile = QMenu("File", self.menubar)
        self.setMenuBar(self.menubar)
        self.menubar.addMenu(self.menuFile)
        self.actionOpen = QAction("Open", self)
        self.actionOpen.setShortcut("Ctrl+O")
        self.menuFile.addAction(self.actionOpen)
        self.actionCreateTxt = QAction("Create txt", self)
        self.actionCreateTxt.setShortcut("Ctrl+T")
        self.menuFile.addAction(self.actionCreateTxt)
        self.actionCreateDeck = QAction("Create deck", self)
        self.actionCreateDeck.setShortcut("Ctrl+D")
        self.menuFile.addAction(self.actionCreateDeck)
        self.actionSettings = QAction("Settings", self)
        self.actionSettings.setShortcut("Ctrl+N")
        self.menuFile.addAction(self.actionSettings)
        self.actionOpen.triggered.connect(self.main_screen.open_file_dialog)
        self.actionSettings.triggered.connect(lambda: self.stackedWidget.setCurrentWidget(self.settings_screen))
        self.actionCreateTxt.triggered.connect(self.create_text_editors)
        self.actionCreateDeck.triggered.connect(self.create_decks)

    def create_text_editors(self):
        """Starts the text editor creation process in a background thread."""
        self.text_editors = []
        pathes = MainScreen.get_current_file_paths(self.main_screen)
        if not pathes:  # More Pythonic check
            dialog = ConfirmationDialog(
                parent=self,
                title="Warning",
                message="No files were selected",
            )
            dialog.setWindowIcon(QIcon("icons/warning_icon.png"))
            dialog.exec_()
            return

        # --- Setup Progress Dialog ---
        if self.progress_dialog is None:  # Create only if not exists
            self.progress_dialog = ProgressBarDialog(chp_amount=5, parent=self.main_screen)
            self.progress_dialog.setStyleSheet(APP_STYLE)
            # Connect the dialog's finished signal (when user closes it) to clean up
            self.progress_dialog.finished.connect(self.on_progress_dialog_finished)
        else:
            # If dialog exists (e.g., from a previous run), reset it
            self.progress_dialog.setup_progress_bar()  # Reset progress state

        self.progress_dialog.show()
        self.progress_dialog.raise_()  # Bring to front
        self.progress_dialog.activateWindow()  # Give it focus if needed

        # --- Setup Worker Thread ---
        # Always create a new thread and worker
        self.worker_thread = QThread()
        self.worker = TextProcessingWorker(pathes)
        # Move the worker to the thread
        self.worker.moveToThread(self.worker_thread)

        # Connect signals and slots
        # Start worker when thread starts
        self.worker_thread.started.connect(self.worker.run)
        # Update progress bar on progress signal
        self.worker.progress.connect(self.update_progress_from_worker)
        # Handle results when ready
        self.worker.result_ready.connect(self.handle_worker_results)
        # Handle errors
        self.worker.error_occurred.connect(self.handle_worker_error)
        # Cleanup when worker finishes
        self.worker.finished.connect(self.worker_thread.quit)  # Quit thread
        self.worker.finished.connect(self.worker.deleteLater)  # Schedule worker deletion
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)  # Schedule thread deletion

        # Start the thread (which will start the worker)
        self.worker_thread.start()

    @pyqtSlot(int, str)
    def update_progress_from_worker(self, stage, status_text):
        """Slot to update the progress dialog from the worker thread."""
        # This runs in the main thread, so it's safe to interact with GUI
        if self.progress_dialog:
            # Complete previous checkpoint if not the first stage
            if stage > 1:
                self.progress_dialog.complete_checkpoint()
            # Update status text for the current stage
            self.progress_dialog.update_status(status_text)
            # If it's the last stage, complete the final checkpoint to finish
            if stage == 5:
                self.progress_dialog.complete_checkpoint()

    @pyqtSlot(str, str)
    def handle_worker_results(self, verbs_text, except_verbs_text):
        """Slot to handle the results from the worker thread."""
        # This runs in the main thread, safe to create UI elements
        print("Worker finished successfully, creating text editors...")
        # Create first text editor window
        text_window1 = self.create_text_editor("verbs.txt")
        text_edit1 = QTextEdit(text_window1)
        text_edit1.setPlainText(verbs_text)
        text_window1.setCentralWidget(text_edit1)
        self.text_editors.append(text_edit1)
        text_window1.show()
        # Create second text editor window
        text_window2 = self.create_text_editor("subs.txt")
        text_edit2 = QTextEdit(text_window2)
        text_edit2.setPlainText(except_verbs_text)
        text_window2.setCentralWidget(text_edit2)
        self.text_editors.append(text_edit2)
        text_window2.show()

    @pyqtSlot(str)
    def handle_worker_error(self, error_message):
        """Slot to handle errors from the worker thread."""
        # This runs in the main thread, safe to show dialogs
        print(f"[ERROR] {error_message}")  # Log to console
        # Show error dialog
        error_dialog = ConfirmationDialog(
            parent=self,
            title="Processing Error",
            message=error_message,  # Or a user-friendly part of the message
        )
        error_dialog.setWindowIcon(QIcon("icons/error_icon.png"))
        error_dialog.exec_()
        # Ensure progress dialog is closed on error
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        # Cleanup worker and thread references
        if self.worker:
            try:
                self.worker.deleteLater()
            except RuntimeError:
                pass  # Object already deleted
            self.worker = None
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread.deleteLater()
            self.worker_thread = None

    @pyqtSlot()
    def on_progress_dialog_finished(self):
        """Slot called when the progress dialog is closed (e.g., by user)."""
        print("Progress dialog closed.")
        # Optionally request the worker to stop if it's still running
        if self.worker and hasattr(self.worker, '_is_running'):
            self.worker._is_running = False
        # Cleanup dialog reference
        self.progress_dialog = None
        # Cleanup worker and thread references
        if self.worker:
            try:
                self.worker.deleteLater()
            except RuntimeError:
                pass  # Object already deleted
            self.worker = None
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread.deleteLater()
            self.worker_thread = None

    def create_text_editor(self, title="", xsize=1000, ysize=600):
        text_window = QMainWindow(self)
        text_window.setWindowTitle(title)
        text_window.resize(xsize, ysize)
        return text_window

    def create_decks(self):
        if len(self.text_editors) < 2:
            dialog = ConfirmationDialog(
                parent=self,
                title="Warning",
                message="No text editors available to extract content from.",
            )
            dialog.setWindowIcon(QIcon("icons/warning_icon.png"))
            dialog.exec_()
            return

        vtext = self.text_editors[0].toPlainText().strip()
        stext = self.text_editors[1].toPlainText().strip()

        if not vtext and not stext:
            dialog = ConfirmationDialog(
                parent=self,
                title="Warning",
                message="No text available to create decks from.",
            )
            dialog.exec_()
            return

        # Ask for label
        label = ""
        while label.strip() == "":
            dialog = SingleInputDialog(
                parent=self,
                title="Deck Name",
                initial_text="Enter deck name:"
            )
            dialog.setWindowIcon(QIcon("icons/create_key.png"))
            if dialog.exec_() != 1:
                return  # User canceled
            label = dialog.get_data().strip()

        # --- Setup Progress Dialog ---
        if self.progress_dialog is None:
            self.progress_dialog = ProgressBarDialog(chp_amount=5, parent=self)
            self.progress_dialog.setStyleSheet(APP_STYLE)
            self.progress_dialog.finished.connect(self.on_progress_dialog_finished)
        else:
            self.progress_dialog.setup_progress_bar()

        self.progress_dialog.setWindowTitle("Creating Decks...")
        self.progress_dialog.update_status("Starting...")
        self.progress_dialog.show()
        self.progress_dialog.raise_()
        self.progress_dialog.activateWindow()

        # --- Setup Worker Thread ---
        self.worker_thread = QThread()
        self.worker = DeckCreationWorker(vtext, stext, label)
        self.worker.moveToThread(self.worker_thread)

        # Connect signals
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.update_progress_from_worker)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker.error_occurred.connect(self.handle_worker_error)

        # On success
        self.worker.finished.connect(lambda: self.on_deck_creation_finished(label))

        # Start thread
        self.worker_thread.start()

    @pyqtSlot()
    def on_deck_creation_finished(self, label):
        """Called when deck creation is successfully completed."""
        if self.progress_dialog:
            self.progress_dialog.complete_checkpoint()  # Finalize progress
            self.progress_dialog.close()
            self.progress_dialog = None

        success_dialog = ConfirmationDialog(
            parent=self,
            title="Success",
            message=f"Decks '{label}' have been created successfully!",
        )
        success_dialog.yes_btn.setStyleSheet("""
            QPushButton#yes_button {
                background-color: #4CAF50;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton#yes_button:hover {
                background-color: #66bb6a;
            }
        """)

        success_dialog.setWindowIcon(QIcon("icons/confirm_icon.png"))
        success_dialog.exec_()

    def on_process_finished(self):  # This might be called from other places if needed
        """ Called when all processes are completed, e.g., from worker's finished signal."""
        print("All processes completed!")
        # Ensure dialog reference is cleared
        self.progress_dialog = None