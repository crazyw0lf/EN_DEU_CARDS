# main_screen.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

class MainScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_file_paths = []  # Теперь это список!
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)

        # Заголовок
        title_label = QLabel("DeuCards")
        title_label.setStyleSheet("font-size: 48px; font-weight: bold; color: white;")
        layout.addWidget(title_label)

        # Подзаголовок
        subtitle_label = QLabel("Create smart German Anki decks automatically")
        subtitle_label.setStyleSheet("font-size: 28px; color: #aaaaaa;")
        layout.addWidget(subtitle_label)

        # Отображение выбранного файла
        self.path_label = QLabel("No file selected")
        self.path_label.setStyleSheet("font-size: 24px; color: #999999;")
        self.path_label.setWordWrap(True)
        layout.addWidget(self.path_label)

        # Кнопка для тестирования (опционально)
        # test_btn = QPushButton("Select File")
        # test_btn.setFixedWidth(200)
        # test_btn.clicked.connect(self.open_file_dialog)
        # layout.addWidget(test_btn)

        self.setLayout(layout)

    def update_path_display(self):
        """Обновляет метку с информацией о выбранных файлах"""
        count = len(self.current_file_paths)
        if count == 0:
            self.path_label.setText("No files selected")
            self.path_label.setToolTip("")
        elif count == 1:
            path = self.current_file_paths[0]
            filename = path.split("/")[-1]  # Имя файла
            self.path_label.setText(f"Selected:\n{filename}")
            self.path_label.setToolTip(path)
        else:
            self.path_label.setText(f"Selected {count} files")
            # Показываем все пути в подсказке
            tooltip_text = "\n".join([p.split("/")[-1] for p in self.current_file_paths])
            self.path_label.setToolTip(f"Files:\n{tooltip_text}")


    def open_file_dialog(self):
        """Открывает диалог выбора нескольких файлов и сохраняет их пути"""
        from PyQt5.QtWidgets import QFileDialog

        # Фильтры для поддерживаемых форматов
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files (PDF, Images)",  # Заголовок окна
            "",  # Начальная директория (пусто — последняя)
            "Supported Files (*.pdf *.png *.jpg *.jpeg);;"
            "PDF Files (*.pdf);;"
            "Image Files (*.png *.jpg *.jpeg);;"
            "All Files (*)"
        )

        if file_paths:
            self.current_file_paths = file_paths  # Сохраняем список путей
            self.update_path_display()
            print(f"[DEBUG] Selected files: {self.current_file_paths}")

    def get_current_file_paths(self):
        """Возвращает список путей к выбранным файлам"""
        return self.current_file_paths.copy()