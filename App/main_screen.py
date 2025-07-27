# main_screen.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QProgressBar
import math


class ProgressBar(QProgressBar):
    def __init__(self, parent=None, chp_amount=1):
        super().__init__(parent)

        self.chp_amount = max(1, chp_amount)  # минимум 1 чекпоинт
        self.current_checkpoint = 0

        self.setRange(0, 100)
        self.setValue(0)
        self.setTextVisible(True)
        self.setFormat("%p%")

        # Цель - первый чекпоинт
        self.target_value = 100 / self.chp_amount

        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start()

    def update_progress(self):
        current_value = self.value()

        if current_value < self.target_value:
            # Вычисляем расстояние до цели
            distance_to_target = self.target_value - current_value

            # Используем экспоненциальное замедление
            # Чем ближе к цели, тем меньше шаг
            step = max(0.1, distance_to_target * 0.05)  # 5% от оставшегося расстояния

            new_value = current_value + step

            # Проверяем, достигли ли цели
            if new_value >= self.target_value:
                new_value = self.target_value
                self.setValue(new_value)
                self.timer.stop()  # останавливаемся точно у цели
            else:
                self.setValue(new_value)

    def complete_checkpoint(self):
        """Завершить текущий чекпоинт"""
        if self.current_checkpoint < self.chp_amount - 1:
            self.current_checkpoint += 1
            self.target_value = (self.current_checkpoint + 1) * (100 / self.chp_amount)

            # Возобновляем движение если остановлены
            if not self.timer.isActive():
                self.timer.start()
        else:
            # Последний этап - устанавливаем 100%
            self.setValue(100)
            self.timer.stop()

    def reset_progress(self):
        """Сбросить прогресс"""
        self.timer.stop()
        self.setValue(0)
        self.current_checkpoint = 0
        self.target_value = 100 / self.chp_amount if self.chp_amount > 0 else 100
        self.timer.start()

    def is_at_checkpoint(self):
        """Проверить, достигнут ли чекпоинт"""
        return not self.timer.isActive() and self.value() == self.target_value


class MainScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_file_paths = []
        self.progress_bar = None
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

        # Кнопка выбора файлов
        select_btn = QPushButton("Select Files")
        select_btn.setFixedWidth(200)
        select_btn.clicked.connect(self.open_file_dialog)
        layout.addWidget(select_btn)

        # Кнопки для создания текста и словаря
        self.create_text_btn = QPushButton("Create Text")
        self.create_text_btn.setFixedWidth(200)
        self.create_text_btn.clicked.connect(self.create_text)
        layout.addWidget(self.create_text_btn)

        self.create_dict_btn = QPushButton("Create Dictionary")
        self.create_dict_btn.setFixedWidth(200)
        self.create_dict_btn.clicked.connect(self.create_dict)
        layout.addWidget(self.create_dict_btn)

        # Прогресс-бар (изначально скрыт)
        self.progress_bar = ProgressBar(chp_amount=4)  # 4 этапа
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

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

    def create_text(self):
        """Функция создания текста с прогресс-баром"""
        if not self.current_file_paths:
            print("No files selected!")
            return

        print("Starting text creation...")

        # Показываем прогресс-бар
        self.progress_bar.setVisible(True)
        self.progress_bar.reset_progress()

        # Блокируем кнопки во время процесса
        self.create_text_btn.setEnabled(False)
        self.create_dict_btn.setEnabled(False)

        # Здесь будет ваша логика создания текста
        # После каждого этапа вызывайте:
        # self.progress_bar.complete_checkpoint()

        # Пример симуляции процесса (в реальном коде замените на вашу логику)
        QTimer.singleShot(2000, lambda: self.on_stage_completed(1))  # Этап 1

    def create_dict(self):
        """Функция создания словаря с прогресс-баром"""
        if not self.current_file_paths:
            print("No files selected!")
            return

        print("Starting dictionary creation...")

        # Показываем прогресс-бар
        self.progress_bar.setVisible(True)
        self.progress_bar.reset_progress()

        # Блокируем кнопки во время процесса
        self.create_text_btn.setEnabled(False)
        self.create_dict_btn.setEnabled(False)

        # Здесь будет ваша логика создания словаря
        # После каждого этапа вызывайте:
        # self.progress_bar.complete_checkpoint()

        # Пример симуляции процесса
        QTimer.singleShot(2000, lambda: self.on_stage_completed(1))  # Этап 1

    def on_stage_completed(self, stage):
        """Обработчик завершения этапа"""
        if self.progress_bar:
            self.progress_bar.complete_checkpoint()
            print(f"Stage {stage} completed")

            # Проверяем, все ли этапы завершены
            if stage < 4:  # Всего 4 этапа
                # Запускаем следующий этап
                QTimer.singleShot(2000, lambda: self.on_stage_completed(stage + 1))
            else:
                # Все этапы завершены
                print("Process completed!")
                self.create_text_btn.setEnabled(True)
                self.create_dict_btn.setEnabled(True)
                # Можно скрыть прогресс-бар через некоторое время
                QTimer.singleShot(3000, lambda: self.progress_bar.setVisible(False))