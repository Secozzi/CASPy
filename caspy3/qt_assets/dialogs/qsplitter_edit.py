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
import typing as ty

# PyQt5
from PyQt5.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QSplitter,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

# Third party
from pkg_resources import resource_filename

# Relative
from caspy3.qt_assets.widgets.focus_line import FocusLine


class SplitterEditor(QWidget):
    def __init__(self, parent) -> None:
        super(SplitterEditor, self).__init__(parent)
        self._parent = parent
        self.resize(600, 400)
        self.setWindowTitle(f"{self._parent.display_name} QSplitter Editor")
        self.setWindowIcon(QIcon(resource_filename("caspy3", "images/logo.png")))
        self.setWindowFlags(Qt.Tool)

        self.v_layout = QVBoxLayout(self)

        # Setup Splitter
        self.preview_splitter = QSplitter(self)
        self.preview_splitter.splitterMoved.connect(lambda x, y: self.update_splitter())

        # Setup combobox
        self.splitter_combo = QComboBox(self)
        self.splitter_combo.currentIndexChanged.connect(self.update_splitter_area)
        for splitter in self._parent.splitters:
            self.splitter_combo.addItem(splitter.objectName())

        # Setup buttons
        self.button_layout = QHBoxLayout()
        self.update_pre = QPushButton("Update Preview")
        self.preview = QPushButton("Preview changes")
        self.apply = QPushButton("Apply changes")
        self.close_b = QPushButton("Close")
        self.update_pre.clicked.connect(self.update_preview)
        self.preview.clicked.connect(self.preview_split)
        self.apply.clicked.connect(self.apply_changes)
        self.close_b.clicked.connect(self.close)

        self.button_layout.addWidget(self.update_pre)
        self.button_layout.addWidget(self.preview)
        self.button_layout.addWidget(self.apply)
        self.button_layout.addWidget(self.close_b)

        self.v_layout.addWidget(self.splitter_combo)
        self.v_layout.addWidget(self.preview_splitter)
        self.v_layout.addLayout(self.button_layout)

        self.setLayout(self.v_layout)

    def resizeEvent(self, event) -> None:
        self.update_splitter()

    def update_preview(self):
        self.preview_splitter.restoreState(
               self._parent.splitters[self.splitter_combo.currentIndex()].saveState()
           )
        self.update_splitter()

    def get_data(self) -> ty.List[float]:
        per_list = []
        for i in range(self.preview_splitter.count()):
            text = self.preview_splitter.widget(i).text()
            per_list.append(
                float(
                    f'0.{text.replace(".", "").replace("%", "") if text else "00"}'
                )
            )
        return per_list

    def preview_split(self):
        per_list = self.get_data()
        if self.preview_splitter.orientation() == Qt.Horizontal:
            _max = self.preview_splitter.width()
        else:
            _max = self.preview_splitter.height()
        _max -= self.preview_splitter.handleWidth() * (self.preview_splitter.count() - 1)
        self.preview_splitter.setSizes([int(i * _max) for i in per_list])

    def apply_changes(self):
        per_list = self.get_data()
        parent_splitter: QSplitter = self._parent.splitters[self.splitter_combo.currentIndex()]
        if parent_splitter.orientation() == Qt.Horizontal:
            _max = parent_splitter.width()
        else:
            _max = parent_splitter.height()
        _max -= parent_splitter.handleWidth() * (parent_splitter.count() - 1)
        parent_splitter.setSizes([int(i * _max) for i in per_list])

    def update_splitter(self):
        if self.preview_splitter.orientation() == Qt.Horizontal:
            _max = self.preview_splitter.width()
        else:
            _max = self.preview_splitter.height()
        _max -= self.preview_splitter.handleWidth() * (
            self.preview_splitter.count() - 1
        )
        sizes = self.preview_splitter.sizes()
        for i in range(self.preview_splitter.count()):
            self.preview_splitter.widget(i).setText(f"{(sizes[i] / _max * 100):.6f}%")

    def update_splitter_area(self, index):
        for i in reversed(range(self.preview_splitter.count())):
            self.preview_splitter.widget(i).setParent(None)

        splitter: QSplitter = self._parent.splitters[index]

        self.preview_splitter.setOrientation(splitter.orientation())
        for i in range(splitter.count()):
            qline = FocusLine(self)
            qline.setInputMask("99.999999%")
            self.preview_splitter.addWidget(qline)

        self.preview_splitter.restoreState(
            self._parent.splitters[index].saveState()
        )

        self.update_splitter()
