import sys
import os
import pyperclip
from PyQt5.QtWidgets import QApplication, QRubberBand, QMainWindow
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QGuiApplication, QPixmap, QPainter, QScreen, QCursor
from pynput import keyboard
import pytesseract
from PIL import Image
# import logging
# from functools import wraps


# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
#
# def log_method(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         logger.info(f"Calling method {func.__name__} with args: {args}, kwargs: {kwargs}")
#         result = func(*args, **kwargs)
#         logger.info(f"Method {func.__name__} returned: {result}")
#         return result
#     return wrapper
#
#
# def log_all_methods(cls):
#     for attr_name, attr_value in cls.__dict__.items():
#         if callable(attr_value) and not attr_name.startswith("__"):
#             setattr(cls, attr_name, log_method(attr_value))
#     return cls


#  @log_all_methods
class ScreenshotTool(QMainWindow):
    def __init__(self, screen):
        super().__init__()

        # Получаем скриншот экрана, на котором произошел вызов
        self.full_screenshot = screen.grabWindow(0)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowState(Qt.WindowFullScreen)
        self.rubber_band = None
        self.start_pos = None

        self.setStyleSheet("background: none;")
        self.pixmap = QPixmap(self.full_screenshot.size())
        self.pixmap.fill(Qt.transparent)
        painter = QPainter(self.pixmap)
        painter.drawPixmap(0, 0, self.full_screenshot)
        painter.end()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
            self.rubber_band.setGeometry(QRect(self.start_pos, QSize()))
            self.rubber_band.show()

    def mouseMoveEvent(self, event):
        if self.rubber_band:
            self.rubber_band.setGeometry(QRect(self.start_pos, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.rubber_band:
            rect = self.rubber_band.geometry()
            self.capture_screenshot(rect)
            self.rubber_band.hide()
            self.rubber_band = None
            self.close()

    def capture_screenshot(self, rect):
        cropped_pixmap = self.full_screenshot.copy(rect)
        cropped_pixmap.save("screenshot.png", "png")
        print("Screenshot сохранен: screenshot.png")

        # Используем pytesseract для извлечения текста с изображения
        self.extract_text_from_image(cropped_pixmap)

    def extract_text_from_image(self, pixmap):
        image = pixmap.toImage()
        image.save("temp_image.png")

        pil_image = Image.open("temp_image.png")

        text = pytesseract.image_to_string(pil_image, lang='eng+rus')

        print("Распознанный текст:")
        print(text)
        pyperclip.copy(text)


def get_current_screen():
    # Определяем экран, на котором находится курсор или приложение
    screen = QGuiApplication.screenAt(QCursor.pos())
    if not screen:
        screen = QGuiApplication.primaryScreen()  # Если не удалось, используем основной экран
    return screen


def on_key_press(key):
    try:
        if key == keyboard.Key.insert:
            app = QApplication(sys.argv)
            screen = get_current_screen()
            screenshot_tool = ScreenshotTool(screen)
            screenshot_tool.show()
            app.exec_()
    except AttributeError:
        pass


if __name__ == "__main__":
    print("Чтобы извлечь текст с изображения, нужно нажать клавишу 'insert' и выделить область")
    pytesseract.pytesseract.tesseract_cmd = os.path.join(os.getcwd(), "tess", "tesseract.exe")
    with keyboard.Listener(on_press=on_key_press) as listener:
        listener.join()
