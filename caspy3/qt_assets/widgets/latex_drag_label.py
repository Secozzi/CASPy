#
#    CASPy - A program that provides both a GUI and a CLI to SymPy.
#    Copyright (C) 2021 Folke Ishii
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

# Standard library
from pathlib import Path
import pkg_resources
import typing as ty
import string
import random

# PyQt5
from PyQt5.QtWidgets import (
    QApplication,
    QColorDialog,
    QDialog,
    QFileDialog,
    QLabel,
    QMenu
)
from PyQt5.QtCore import (
    pyqtSignal,
    pyqtSlot,
    QMimeData,
    QObject,
    QRunnable,
    Qt,
    QTemporaryDir,
    QUrl,
)
from PyQt5.QtGui import QDrag, QPixmap, QPixmapCache
from PyQt5.uic import loadUi

# Relative
from caspy3.qt_assets.latex_pixmap import mathTex_to_QPixmap


class LaTeXSignals(QObject):
    finished = pyqtSignal()
    output = pyqtSignal(QPixmap)


class LaTeXWorker(QRunnable):
    def __init__(
            self,
            latex_str:
            str, fig:
            "matplotlib.pyplot.figure.Figure",
            fs: int
    ) -> None:
        super(LaTeXWorker, self).__init__()

        self.latex_str = latex_str
        self.fig = fig
        self.fs = fs

        self.signals = LaTeXSignals()

    @pyqtSlot()
    def run(self) -> None:
        if not self.latex_str:
            self.latex_str = r"\mathrm{Null}"
        out = mathTex_to_QPixmap(
            f"${self.latex_str}$",
            self.fs,
            fig=self.fig,
        )
        self.signals.output.emit(out)
        self.signals.finished.emit()


class SaveDialog(QDialog):
    def __init__(self, drag_label: "DragLabel", parent=None) -> None:
        super(SaveDialog, self).__init__(parent=parent)
        self.drag_label = drag_label

        loadUi(
            pkg_resources.resource_filename(
                "caspy3", "qt_assets/dialogs/save_dialog.ui"
            ),
            self,
        )
        self.fs_spinbox.setValue(self.drag_label.parent.latex_fs)

        self.color_hex = "#000000"
        self.update_color(self.color_hex)
        self.render_label()

        # Bindings
        self.pick_color.clicked.connect(self.get_color)
        self.preview.clicked.connect(self.render_label)
        self.cancel.clicked.connect(self.close)
        self.save.clicked.connect(lambda: self.drag_label.save_image(self.pixmap))

        self.show()

    def get_color(self) -> None:
        color = QColorDialog.getColor()
        if color.isValid():
            self.update_color(color.name())

    def update_color(self, color: str) -> None:
        self.color_preview.setStyleSheet(f"QLabel {{background-color:{color};}}")
        self.color_hex_line.setText(color)
        self.color_hex = color

    def render_label(self) -> None:
        formula = self.drag_label.formula
        self.pixmap = self.drag_label.get_latex_pixmap(
            formula=formula, fs=self.fs_spinbox.value(), color=self.color_hex
        )
        self.preview_pixmap.setPhoto(pixmap=self.pixmap)


class DragLabel(QLabel):
    """
    Custom QLabel class that allows for draggable QImages.
    Creates a LaTeX based on formula and MainWindow's LaTeX resolution,
    then saves it into a temporary directory and loads the path into
    QMimeData, and then the QDrag copies it.
    """

    def __init__(self, parent: "QWidget") -> None:
        super(DragLabel, self).__init__(parent)
        self._parent = parent
        self.formula = ""
        self.setStyleSheet("border: 1px solid gray;")
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.customContextMenuRequested.connect(
            lambda pos: self.customMenuEvent(self, pos)
        )

    def setFormula(self, formula):
        self.formula = formula

    def customMenuEvent(self, child: "DragLabel", eventPosition: "QPoint") -> None:
        context_menu = QMenu(self)
        copy = context_menu.addAction("Copy")
        copy_fs = context_menu.addAction("Copy with font-size")
        context_menu.addSeparator()
        save = context_menu.addAction("Save image")

        action = context_menu.exec_(child.mapToGlobal(eventPosition))

        if self.formula:
            if action == copy:
                QApplication.clipboard().setPixmap(child.pixmap())

            elif action == copy_fs:
                QApplication.setOverrideCursor(Qt.WaitCursor)
                QApplication.clipboard().setPixmap(self.get_latex_pixmap(self.formula))
                QApplication.restoreOverrideCursor()

            elif action == save:
                self._preview = SaveDialog(self)

    def save_image(self, qpixmap: "QPixmap") -> None:
        formula = self.formula.translate(str.maketrans("", "", '<>:"/\\|?*'))
        dialog = QFileDialog()
        fileName, _ = dialog.getSaveFileName(
            self,
            "Save Image",
            str(Path.home()) + f"/{formula}.png",
            "Images (*.png)",
            options=QFileDialog.DontUseNativeDialog,
        )
        if fileName:
            qpixmap.save(fileName, "PNG")
            self._preview.close()
        else:
            self._preview.show()

    def stop_thread(self) -> None:
        pass

    def render_latex(self) -> None:
        # Set loading pixmap
        self.setPixmap(
            QPixmap(
                pkg_resources.resource_filename(
                    "caspy3", "images/loading.png"
                )
            ).scaled(
                self.width() - 5,
                self.height() - 5,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )
        worker = LaTeXWorker(
            self.formula,
            self._parent.main_window.fig,
            self._parent.main_window.latex_fs
        )
        worker.signals.output.connect(self.update_pixmap)
        worker.signals.finished.connect(self.stop_thread)
        self._parent.main_window.threadpool.start(worker)

    def update_pixmap(self, pixmap: QPixmap) -> None:
        self.clear()
        self.setPixmap(
            pixmap.scaled(
                self.width() - 5,
                self.height() - 5,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    def get_latex_pixmap(
        self, formula: str, fs: ty.Union[int, None] = None, color: str = None
    ) -> "QPixmap":

        if not fs:
            fs = self._parent.main_window.latex_fs

        pixmap = mathTex_to_QPixmap(
            f"${self.formula}$", fs, fig=self._parent.main_window.fig, color=color
        )
        return pixmap

    def mouseMoveEvent(self, ev: "QtGui.QMouseEvent") -> None:
        if ev.buttons() == Qt.LeftButton and self.formula:
            drag = QDrag(self)
            mimeData = QMimeData()
            QApplication.setOverrideCursor(Qt.WaitCursor)

            rand = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
            td = QTemporaryDir()
            path = td.path() + rand + ".png"

            pixmap = self.get_latex_pixmap(self.formula)
            qimage = pixmap.toImage()
            qimage.save(path, "PNG")

            mimeData.setImageData(qimage)
            mimeData.setUrls([QUrl.fromLocalFile(path)])
            drag.setMimeData(mimeData)

            drag.setPixmap(pixmap.scaledToHeight(40, Qt.SmoothTransformation))
            QApplication.restoreOverrideCursor()
            drag.exec_(Qt.CopyAction)
            ev.accept()
            QPixmapCache.clear()
        else:
            ev.ignore()
