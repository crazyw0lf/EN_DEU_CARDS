# about_page.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from styles import ABOUT_PAGE_STYLE

class AboutPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title_label = QLabel("About DeuCards")
        title_label.setObjectName("aboutTitle")
        title_label.setStyleSheet(ABOUT_PAGE_STYLE)
        layout.addWidget(title_label)

        # Icon
        icon_label = QLabel()
        pixmap = QPixmap("icons/app_icon.png")
        if not pixmap.isNull():
            icon_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            icon_label.setText("[App Icon]")
            icon_label.setStyleSheet("font-size: 16px; color: #777;")
        layout.addWidget(icon_label)

        # Version
        version_label = QLabel("Version 1.0.0")
        version_label.setObjectName("versionLabel")
        version_label.setStyleSheet(ABOUT_PAGE_STYLE)
        layout.addWidget(version_label)

        # Author
        author_label = QLabel("Created by Hryhorii Antoniuk")
        author_label.setObjectName("authorIntel")
        author_label.setStyleSheet(ABOUT_PAGE_STYLE)
        layout.addWidget(author_label)

        # Description
        desc_text = (
            "DeuCards is a smart and intuitive app designed to help you learn German "
            "effortlessly by generating custom Anki flashcard decks.\n\n"
            "It automatically creates bilingual English-German cards, "
            "complete with translations, grammar hints, and example sentences — "
            "all ready to import into your Anki library.\n\n"
            "Built with simplicity and language mastery in mind, "
            "DeuCards turns vocabulary learning into a seamless, automated experience."
        )
        description_label = QLabel(desc_text)
        description_label.setObjectName("aboutText")
        description_label.setWordWrap(True)
        description_label.setStyleSheet(ABOUT_PAGE_STYLE)
        layout.addWidget(description_label)

        # Github Link
        links_layout = QHBoxLayout()
        github_btn = QPushButton("GitHub Repository")
        github_btn.setObjectName("aboutLink")
        github_btn.setStyleSheet(ABOUT_PAGE_STYLE)
        github_btn.clicked.connect(lambda: self.open_link("https://github.com/crazyw0lf/EN_DEU_CARDS"))

        links_layout.addWidget(github_btn)
        layout.addLayout(links_layout)

        self.setLayout(layout)

    def open_link(self, url):
        import webbrowser
        webbrowser.open(url)