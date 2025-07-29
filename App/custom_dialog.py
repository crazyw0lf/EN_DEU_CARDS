# custom_dialog.py

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton, QHBoxLayout

class ApiKeyDialog(QDialog):
    def __init__(self,parent = None, name="", key=""):
        super().__init__(parent)
        self.setModal(True)
        self.resize(300, 120)

        layout = QVBoxLayout(self)

        # Name
        self.name_input = QLineEdit(name)
        self.name_input.setPlaceholderText("Name")
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)

        # Key
        self.key_input = QLineEdit(key)
        self.key_input.setPlaceholderText("Secret Key")
        layout.addWidget(QLabel("Secret Key:"))
        layout.addWidget(self.key_input)

        # Buttons
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")

        # Button styles
        self.ok_btn.setObjectName("dialog_ok")
        self.cancel_btn.setObjectName("dialog_cancel")
        self.setStyleSheet("""
                    #dialog_ok {
                        background-color: #4CAF50;
                        color: white;
                        padding: 6px 12px;
                        border-radius: 4px;
                    }
                    #dialog_ok:hover {
                        background-color: #66bb6a;
                    }
                    #dialog_cancel {
                        background-color: #757575;
                        color: white;
                        padding: 6px 12px;
                        border-radius: 4px;
                    }
                    #dialog_cancel:hover {
                        background-color: #9e9e9e;
                    }
                """)

        self.ok_btn.setDefault(True)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def get_data(self):
        return self.name_input.text().strip(), self.key_input.text().strip()

class ConfirmationDialog(QDialog):
    def __init__(self, parent=None, title="Confirm", message="Are you sure?", icon_path=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(300, 120)

        layout = QVBoxLayout(self)

        self.message_label = QLabel(message)
        self.message_label.setWordWrap(True)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.message_label)
        layout.addLayout(top_layout)

        # Buttons
        btn_layout = QHBoxLayout()

        self.yes_btn = QPushButton("Yes")
        self.no_btn = QPushButton("No")

        self.yes_btn.setObjectName("yes_button")
        self.no_btn.setObjectName("no_button")

        self.yes_btn.clicked.connect(self.accept)   # cancel dialog and return QDialog.Accepted
        self.no_btn.clicked.connect(self.reject)   # cancel dialog and return QDialog.Rejected

        # Implementing styles
        self.yes_btn.setStyleSheet("""
            QPushButton#yes_button {
                background-color: #d32f2f;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                min-width: 70px;
            }
            QPushButton#yes_button:hover {
                background-color: #f44336;
            }
        """)
        self.no_btn.setStyleSheet("""
            QPushButton#no_button {
                background-color: #757575;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                min-width: 70px;
            }
            QPushButton#no_button:hover {
                background-color: #9e9e9e;
            }
        """)

        # add buttons to layout
        btn_layout.addStretch()
        btn_layout.addWidget(self.yes_btn)
        btn_layout.addWidget(self.no_btn)
        layout.addLayout(btn_layout)

class SingleInputDialog(QDialog):
    def __init__(self, parent=None,title = "", initial_text=""):
        super().__init__(parent)
        self.setModal(True)
        self.resize(250, 100)  # Smaller size than ApiKeyDialog

        layout = QVBoxLayout(self)

        # Input field
        self.setWindowTitle(title)
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter text")
        layout.addWidget(QLabel(initial_text))
        layout.addWidget(self.input_field)

        # Buttons
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")

        # Button styles
        self.ok_btn.setObjectName("dialog_ok")
        self.cancel_btn.setObjectName("dialog_cancel")
        self.setStyleSheet("""
            #dialog_ok {
                background-color: #4CAF50;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
            }
            #dialog_ok:hover {
                background-color: #66bb6a;
            }
            #dialog_cancel {
                background-color: #757575;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
            }
            #dialog_cancel:hover {
                background-color: #9e9e9e;
            }
        """)

        self.ok_btn.setDefault(True)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def get_data(self):
        return self.input_field.text().strip()