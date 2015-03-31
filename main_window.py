# -*- coding: utf-8 -*-
__author__ = 'konnov@simicon.com'

from PyQt4 import QtCore, QtGui, QtWebKit
import urllib

from presets_widget import PresetsWidget
from fiorita_trikotaj_parser import FioritaTrikotajParser
from love_bunny_parser import LoveBunnyParser


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super().__init__(None)

        self._web_view = QtWebKit.QWebView(self)

        self._url_edit = QtGui.QLineEdit(self)
        self._url_edit.returnPressed.connect(
            lambda: self._web_view.setUrl(
                QtCore.QUrl.fromUserInput(self._url_edit.text())
            )
        )

        self._web_view.loadStarted.connect(self._on_page_load_started)
        self._web_view.loadFinished.connect(self._on_page_load_finished)

        self._presets_widget = PresetsWidget(self)
        self._presets_widget.setSizePolicy(
            QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum
        )
        self._presets_widget.activated.connect(
            lambda url: self._web_view.setUrl(
                QtCore.QUrl(url)
            )
        )

        self._load_progress = QtGui.QProgressBar()
        self._load_progress.setVisible(False)
        self._load_progress.setRange(0, 100)
        self._web_view.loadProgress.connect(
            self._load_progress.setValue
        )

        self._text_view = QtGui.QPlainTextEdit(self)
        self._text_view.setMaximumWidth(200)

        self._image = QtGui.QLabel(self)

        left_layout = QtGui.QVBoxLayout()
        left_layout.addWidget(self._text_view)
        left_layout.addWidget(self._image)

        right_layout = QtGui.QVBoxLayout()
        right_layout.addWidget(self._url_edit)
        right_layout.addWidget(self._presets_widget)
        right_layout.addWidget(self._web_view)
        right_layout.addWidget(self._load_progress)

        layout = QtGui.QHBoxLayout()
        layout.addLayout(left_layout)
        layout.addLayout(right_layout)

        central_widget = QtGui.QWidget(self)
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

        love_bunny = None

    def _on_page_load_started(self):
        self._url_edit.setText(self._web_view.url().toString())
        self._url_edit.setEnabled(False)
        self._load_progress.setVisible(True)

    def _on_page_load_finished(self):
        self._url_edit.setEnabled(True)
        self._load_progress.setVisible(False)

        self.work(self._web_view.url().toString())

    def work(self, url: str):
        if "fiorita-trikotaj.ru" in url:
            self._work_fiorita()

        if "optom.love-bunny.ru" in url:
            self._work_love_bunny()

    def _work_fiorita(self):
        page_parser = FioritaTrikotajParser()
        page_parser.set_page_source(
            self._web_view.page().mainFrame().toHtml()
        )
        self._text_view.clear()
        self._text_view.appendPlainText(
            self._web_view.url().toString()
        )
        self._text_view.appendPlainText(page_parser.extract_name())
        self._text_view.appendPlainText("Состав: "
                                        + page_parser.extract_description())

        color_string = ", ".join(page_parser.extract_colors())
        self._text_view.appendPlainText("Цвет: " + color_string)

        sizes_string = ", ".join(page_parser.extract_sizes())
        self._text_view.appendPlainText("Размер: " + sizes_string)

        self._text_view.appendPlainText("Цена: "
                                        + page_parser.extract_price()
                                        + "р.")
        QtGui.QApplication.clipboard().setText(self._text_view.toPlainText())

    def _work_love_bunny(self):
        love_bunny = LoveBunnyParser()
        love_bunny.set_page_source(self._web_view.page().mainFrame().toHtml())

        self._text_view.clear()
        self._text_view.appendPlainText(love_bunny.extract_name())
        print(love_bunny.extract_sizes())
        sizes_string = ", ".join(love_bunny.extract_sizes())
        self._text_view.appendPlainText("Размер: " + sizes_string)

        self._text_view.appendPlainText("Цена: "
                                        + love_bunny.extract_price()
                                        + "р.")
        QtGui.QApplication.clipboard().setText(self._text_view.toPlainText())

        with urllib.request.urlopen(love_bunny.extract_image_url()) as f:
            image_data = f.read()
            if image_data:
                image = QtGui.QImage()
                image.loadFromData(image_data, "JPG")
                QtGui.QApplication.clipboard().setImage(image)
                image = image.scaledToHeight(100,
                                             QtCore.Qt.SmoothTransformation)
                self._image.setPixmap(QtGui.QPixmap.fromImage(image))
