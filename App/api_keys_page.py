# api_keys_page.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from custom_dialog import ApiKeyDialog, ConfirmationDialog
from api_data import load_api_keys, save_api_keys
from PyQt5.QtGui import QIcon

class ApiKeysPage(QWidget):
    def __init__(self, settings_screen):
        super().__init__()
        self.settings_screen = settings_screen
        self.api_keys = []
        self.init_ui()
        self.load_keys()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Заголовок
        title = QLabel("API Keys")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Описание
        description = QLabel(
            "Manage your API keys. Remember to keep your API keys safe to prevent unauthorized access."
        )
        description.setStyleSheet("color: #aaaaaa;")
        layout.addWidget(description)

        # Кнопка Create
        create_btn = QPushButton("Create API Key")
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #333333;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        create_btn.clicked.connect(self.show_create_dialog)
        layout.addWidget(create_btn, alignment=Qt.AlignRight)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["NAME", "SECRET KEY", "", ""])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

    def load_keys(self):
        """Загружает ключи из файла и отображает в таблице"""
        self.api_keys = load_api_keys()
        self.table.setRowCount(0)

        for row, key_data in enumerate(self.api_keys):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(key_data["name"]))
            # Отображаем только первую и последнюю часть ключа
            masked_key = self.mask_key(key_data["key"])
            self.table.setItem(row, 1, QTableWidgetItem(masked_key))

            edit_btn = QPushButton("Edit")
            delete_btn = QPushButton("Delete")

            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #444444;
                    color: white;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #666666;
                }
            """)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #d32f2f;
                    color: white;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #ff5252;
                }
            """)

            edit_btn.clicked.connect(lambda _, r=row: self.show_edit_dialog(r))
            delete_btn.clicked.connect(lambda _, r=row: self.delete_key(r))

            self.table.setCellWidget(row, 2, edit_btn)
            self.table.setCellWidget(row, 3, delete_btn)

    def mask_key(self, key):
        """Маскирует ключ, оставляя только первые и последние 4 символа"""
        if len(key) <= 8:
            return key
        return f"{key[:4]}...{key[-4:]}"

    def show_create_dialog(self):
        dialog = ApiKeyDialog(self)
        dialog.setWindowTitle("Create API Key")
        dialog.setWindowIcon(QIcon("icons/create_key.png"))

        if dialog.exec_():
            name, key = dialog.get_data()
            if name and key:
                self.api_keys.append({"name": name, "key": key})
                save_api_keys(self.api_keys)
                self.load_keys()

    def show_edit_dialog(self, row):
        key_data = self.api_keys[row]
        dialog = ApiKeyDialog(self, key_data["name"],"")
        dialog.setWindowTitle("Edit API Key")
        dialog.setWindowIcon(QIcon("icons/edit_key.png"))
        if dialog.exec_():
            name, key = dialog.get_data()
            if name and key:
                self.api_keys[row]["name"] = name
                self.api_keys[row]["key"] = key
                save_api_keys(self.api_keys)
                self.load_keys()

    def delete_key(self, row):
        dialog = ConfirmationDialog(
            parent=self,
            title="Delete Key",
            message="Are you sure you want to delete this API key?",
        )
        dialog.setWindowIcon(QIcon("icons/delete_key.png"))  # Иконка окна

        if dialog.exec_():
            del self.api_keys[row]
            save_api_keys(self.api_keys)
            self.load_keys()