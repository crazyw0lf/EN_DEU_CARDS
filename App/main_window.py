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
    result_ready = pyqtSignal(str, str) # Signal when processing is done: (verbs_text, except_verbs_text)
    error_occurred = pyqtSignal(str) # Signal if an error happens: (error_message)
    finished = pyqtSignal() # Signal when the worker has finished its run

    def __init__(self, file_paths):
        super().__init__()
        self.file_paths = file_paths
        self._is_running = True # Flag to potentially allow cancellation (optional)

    @pyqtSlot()
    def run(self):
        """The main processing logic, run in the worker thread."""
        try:
            # --- Stage 1: Extract Text ---
            if not self._is_running: return
            self.progress.emit(1, "Extracting text from files...")
            text = ""
            for path in self.file_paths:
                if not self._is_running: return # Check flag periodically
                if ".pdf" in path:
                    text += extract_text_from_pdf(path)
                else:
                    text += extract_text_from_image(path)

            # --- Stage 2: Clean Text ---
            if not self._is_running: return
            self.progress.emit(2, "Cleaning and tokenizing text...")
            cleaned_text = clean_tokenized_text(text)

            # --- Stage 3: Extract Verbs ---
            if not self._is_running: return
            self.progress.emit(3, "Extracting verbs...")
            verbs_text = extract_verbs(cleaned_text)

            # --- Stage 4: Extract Other Words ---
            if not self._is_running: return
            self.progress.emit(4, "Extracting other words and phrases...")
            except_verbs_text = extract_except_verbs(cleaned_text)

            # --- Stage 5: Signal Completion ---
            if not self._is_running: return
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
            self._is_running = False # Ensure flag is reset

# --- MainWindow Class ---

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("API Key Manager")
        self.setWindowIcon(QIcon("icons/app_icon.png"))
        self.resize(1000, 600)

        # Список для хранения ссылок на текстовые редакторы
        self.text_editors = []

        # === QStackedWidget для переключения между экранами ===
        self.stackedWidget = QStackedWidget(self)
        self.setCentralWidget(self.stackedWidget)

        # === Создаем экраны ===
        self.main_screen = MainScreen(self)
        self.settings_screen = SettingsScreen(self)

        # Добавляем в стек
        self.stackedWidget.addWidget(self.main_screen)  # index 0
        self.stackedWidget.addWidget(self.settings_screen)  # index 1

        # === Менюбар ===
        self.create_menu_bar()

        # === Стиль ===
        self.setStyleSheet(APP_STYLE)

        # --- For Threading ---
        self.progress_dialog = None # Keep track of the dialog instance
        self.worker_thread = None # Keep track of the worker thread
        self.worker = None # Keep track of the worker object

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
        # Очищаем список текстовых редакторов перед созданием новых
        self.text_editors = []
        pathes = MainScreen.get_current_file_paths(self.main_screen)
        if not pathes: # More Pythonic check
            dialog = ConfirmationDialog(
                parent=self,
                title="Warning",
                message="No files were selected",
            )
            dialog.setWindowIcon(QIcon("icons/warning_icon.png"))
            dialog.exec_()
            return

        # --- Setup Progress Dialog ---
        if self.progress_dialog is None: # Create only if not exists
            self.progress_dialog = ProgressBarDialog(chp_amount=5, parent=self.main_screen)
            self.progress_dialog.setStyleSheet(APP_STYLE)
            # Connect the dialog's finished signal (when user closes it) to cleanup
            self.progress_dialog.finished.connect(self.on_progress_dialog_finished)
        else:
            # If dialog exists (e.g., from a previous run), reset it
            self.progress_dialog.setup_progress_bar() # Reset progress state

        self.progress_dialog.show()
        self.progress_dialog.raise_() # Bring to front
        self.progress_dialog.activateWindow() # Give it focus if needed

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
        self.worker.finished.connect(self.worker_thread.quit) # Quit thread
        self.worker.finished.connect(self.worker.deleteLater) # Schedule worker deletion
        self.worker_thread.finished.connect(self.worker_thread.deleteLater) # Schedule thread deletion

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
        print(f"[ERROR] {error_message}") # Log to console
        # Show error dialog
        error_dialog = ConfirmationDialog(
            parent=self,
            title="Processing Error",
            message=error_message, # Or a user-friendly part of the message
        )
        error_dialog.setWindowIcon(QIcon("icons/error_icon.png"))
        error_dialog.exec_()

        # Ensure progress dialog is closed on error
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None

        # Cleanup worker and thread references
        if self.worker:
            self.worker.deleteLater()
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
            self.worker.deleteLater()
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
        if self.text_editors == []:
            return
        vtext = self.text_editors[0].toPlainText()
        stext = self.text_editors[1].toPlainText()

        label = ""
        while label == "":
            dialog = SingleInputDialog(parent=None, title="Filename", initial_text="Filename:")
            dialog.setWindowIcon(QIcon("icons/create_key.png"))

            if dialog.exec_() == 1:
                label = dialog.get_data()

        self.write_file(vtext, f"verbs {label}")
        self.write_file(stext, f"subs {label}")

        create_v_deck(label)
        create_s_deck(label)

    def write_file(self, text, filename):
        path = f"C:/Users/GANT-NB/Music/anki/sources/{filename}.txt"
        if os.path.exists(path):
            os.remove(path)

        file = open(path, "w")
        file.write(text)
        file.close()

    def on_process_finished(self): # This might be called from other places if needed
        """Обработчик завершения всего процесса"""
        print("All processes completed!")
        # Ensure dialog reference is cleared
        self.progress_dialog = None