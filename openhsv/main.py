from openhsv import OpenHSV
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap
import qdarkstyle
import sys
import time

if __name__ == '__main__':
    app = QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    # Show splash screen for 2 seconds
    pix = QPixmap("openhsv/openhsv_splashscreen.jpg")
    splash = QSplashScreen(pix)
    splash.show()
    time.sleep(2)
    splash.close()

    # Show OpenHSV main window
    w = OpenHSV(app)
    w.showMaximized()
    w.updateRangeIndicator()

    sys.exit(app.exec_())