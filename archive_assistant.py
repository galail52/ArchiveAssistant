"""
Archive Assistant

Launcher

Author:
Trent + ChatGPT
"""

import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def load_stylesheet():

    return """
    QMainWindow {
        background-color: #2b2b2b;
    }

    QWidget {
        background-color: #2b2b2b;
        color: #eeeeee;
        font-size: 11pt;
    }

    QLabel {
        color: #eeeeee;
        background: transparent;
    }

    QMenuBar {
        background-color: #353535;
        color: white;
    }

    QMenuBar::item:selected {
        background-color: #4d8cff;
    }

    QMenu {
        background-color: #353535;
        color: white;
    }

    QMenu::item:selected {
        background-color: #4d8cff;
    }

    QProgressBar {

        border: 1px solid #555555;
        border-radius: 5px;

        text-align: center;

        background-color: #444444;

        height: 18px;
    }

    QProgressBar::chunk {

        background-color: #3daee9;

        border-radius: 5px;
    }

    QFrame {

        color: #666666;
    }

    """

def main():

    app = QApplication(sys.argv)

    app.setStyleSheet(load_stylesheet())

    window = MainWindow()

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()