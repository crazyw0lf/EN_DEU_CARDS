# styles.py

APP_STYLE = """
    QMainWindow, QWidget {
        background-color: #1e1e1e;
        color: white;
    }
    QMenuBar {
        background-color: #2e2e2e;
        color: white;
    }
    QMenu {
        background-color: #2e2e2e;
        color: white;
    }
    QMenu::item:selected {
        background-color: #3d3d3d;
    }
    QStatusBar {
        background-color: #2e2e2e;
        color: white;
    }
    QMenuBar::item:selected {
        background-color: #3d3d3d;
    }

    /* Стили для QTableWidget */
    QTableWidget {
        background-color: #292929;  /* Цвет фона таблицы */
        color: white;              /* Цвет текста */
        selection-background-color: #444444;  /* Цвет выделения строки */
        selection-color: white;    /* Цвет текста при выделении */
        gridline-color: #555555;   /* Цвет разделителей между ячейками */
    }
    QHeaderView::section {
        background-color: #2e2e2e;  /* Цвет заголовков столбцов */
        color: white;               /* Цвет текста заголовков */
        border: none;               /* Убираем границы вокруг заголовков */
        padding: 5px;              /* Поля вокруг текста в заголовках */
    }
    QTableWidget::item {
        padding: 5px;              /* Поля внутри ячеек */
    }
"""

SETTINGS_PANEL_STYLE = "background-color: #292929;"
SETTINGS_BUTTON_STYLE = """
    QPushButton {
        background-color: transparent;
        color: white;
        padding: 10px;
        font-size: 14px;
        text-align: left;
        border: none;
    }
    QPushButton:checked {
        background-color: #3d3d3d;
    }
    QPushButton:hover {
        background-color: #444444;
    }
"""
SETTINGS_BUTTON_EXIT_STYLE = SETTINGS_BUTTON_STYLE + """
    QPushButton:hover {
        background-color: #d32f2f;
    }
"""

ABOUT_PAGE_STYLE = """
    QLabel#aboutTitle {
        font-size: 32px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 10px;
    }
    QLabel#aboutText {
        font-size: 20px;
        color: #cccccc;
        margin: 8px 0;
    }
    QLabel#versionLabel {
        font-size: 18px;
        color: #999999;
        font-style: italic;
    }
    QLabel#authorLabel {
        font-size: 20px;
        color: #66bb6a;
        font-weight: bold;
    }
    QPushButton#aboutLink {
        background-color: transparent;
        color: white;
        padding: 10px;
        font-size: 20px;
        text-align: left;
        border: none;
    }
    QPushButton#aboutLink:checked {
        background-color: #3d3d3d;
    }
    QPushButton#aboutLink:hover {
        background-color: #444444;
    }
"""