from distutils.file_util import write_file

from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QMenuBar, QMenu, QAction, QTextEdit
from PyQt5.QtGui import QIcon
from custom_dialog import SingleInputDialog, ConfirmationDialog
from anki_utils import create_s_deck, create_v_deck
from source_to_txt_utils import extract_text_from_pdf, extract_text_from_image
from ai_utils import clean_tokenized_text, extract_verbs, extract_except_verbs
from settings_screen import SettingsScreen
from styles import APP_STYLE
from main_screen import MainScreen
import os

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
        # Очищаем список текстовых редакторов перед созданием новых
        self.text_editors = []
        pathes = MainScreen.get_current_file_paths(self.main_screen)
        if pathes == []:
            dialog = ConfirmationDialog(
                parent=self,
                title="Warning",
                message="No files were selected",
            )
            dialog.setWindowIcon(QIcon("icons/warning_icon.png"))
            dialog.exec_()
            return
        text = ""
        for path in pathes:
            if ".pdf" in path:
                text += extract_text_from_pdf(path)
            else:
                text += extract_text_from_image(path)

        cleaned_text = clean_tokenized_text(text)


        verbs_text = extract_verbs(cleaned_text)
        except_verbs_text = extract_except_verbs(cleaned_text)

        # Create first text editor window
        text_window1 = self.create_text_editor("verbs.txt")
        text_edit1 = QTextEdit(text_window1)
        text_edit1.setPlainText(verbs_text)
        text_window1.setCentralWidget(text_edit1)
        self.text_editors.append(text_edit1)  # Сохраняем ссылку
        text_window1.show()

        # Create second text editor window
        text_window2 = self.create_text_editor("subs.txt")
        text_edit2 = QTextEdit(text_window2)
        text_edit2.setPlainText(except_verbs_text)
        text_window2.setCentralWidget(text_edit2)
        self.text_editors.append(text_edit2)  # Сохраняем ссылку
        text_window2.show()

    def create_text_editor(self,title = "",xsize = 1000,ysize = 600):
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
            dialog = SingleInputDialog(parent=None,title="Filename" ,initial_text="Filename:")
            dialog.setWindowIcon(QIcon("icons/create_key.png"))

            if dialog.exec_() == 1:
                label =  dialog.get_data()

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