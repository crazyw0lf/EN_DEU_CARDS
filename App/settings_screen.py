# settings_screen.py

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QFrame
from api_keys_page import ApiKeysPage
from styles import SETTINGS_PANEL_STYLE, SETTINGS_BUTTON_STYLE, SETTINGS_BUTTON_EXIT_STYLE
from about_page import AboutPage

class SettingsScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # left panel
        self.left_panel = QFrame()
        self.left_panel.setFixedWidth(150)
        self.left_panel.setStyleSheet(SETTINGS_PANEL_STYLE)

        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # buttons
        self.exit_btn = QPushButton("Exit")
        self.api_keys_btn = QPushButton("API Keys")
        self.about_btn = QPushButton("About")

        # style buttons
        self.exit_btn.setStyleSheet(SETTINGS_BUTTON_EXIT_STYLE)
        self.api_keys_btn.setStyleSheet(SETTINGS_BUTTON_STYLE)
        self.about_btn.setStyleSheet(SETTINGS_BUTTON_STYLE)

        self.exit_btn.setCheckable(True)
        self.api_keys_btn.setCheckable(True)
        self.about_btn.setCheckable(True)
        self.api_keys_btn.setChecked(True)

        # events
        self.exit_btn.clicked.connect(self.exit)
        self.api_keys_btn.clicked.connect(lambda: self.switch_settings_page(0))
        self.about_btn.clicked.connect(lambda: self.switch_settings_page(1))

        # add buttons to left layout
        left_layout.addWidget(self.exit_btn)
        left_layout.addWidget(self.api_keys_btn)
        left_layout.addWidget(self.about_btn)
        left_layout.addStretch()
        self.left_panel.setLayout(left_layout)

        # right area for settings content
        self.settings_content = QStackedWidget()

        # add pages to settings content
        self.api_keys_page = ApiKeysPage(self)
        self.settings_content.addWidget(self.api_keys_page)

        self.about_page = AboutPage()
        self.settings_content.addWidget(self.about_page)

        # add settings content to the right area
        layout.addWidget(self.left_panel)
        layout.addWidget(self.settings_content)
        self.setLayout(layout)

    def exit(self):
        self.main_window.stackedWidget.setCurrentWidget(self.main_window.main_screen)
        self.exit_btn.setChecked(False)

    def switch_settings_page(self, index):
        self.settings_content.setCurrentIndex(index)
        for btn in [self.api_keys_btn, self.about_btn, self.exit_btn]:
            btn.setChecked(False)
        if index == 0:
            self.api_keys_btn.setChecked(True)
        elif index == 1:
            self.about_btn.setChecked(True)

