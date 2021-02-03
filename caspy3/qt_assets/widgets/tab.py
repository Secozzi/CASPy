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
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSplitter, QWidget

# Relative
if ty.TYPE_CHECKING:
    from caspy3.qt_assets.app.mainwindow import MainWindow


class CaspyTab(QWidget):
    def __init__(self, main_window: "MainWindow", name: str) -> None:
        super().__init__()
        self.name = name
        self.main_window = main_window
        self.main_window.qapp.aboutToQuit.connect(self.close_event)
        self.setFont(self.main_window.tabs_font)

    def update_ui(self, input_dict: ty.Dict[str, ty.List[str]]) -> None:
        self.eout.set_cursor(Qt.ArrowCursor)
        self.aout.set_cursor(Qt.ArrowCursor)

        first_key = list(input_dict)[0]
        if first_key == "error":
            self.main_window.show_error_box(input_dict[first_key][0])
            self.main_window.latex_ans = ""
        else:
            if self.out_splitter.count() == 3:
                latex_label = self.out_splitter.widget(1)
                latex_label.setFormula(input_dict["latex"])
                latex_label.render_latex()
            self.main_window.latex_ans = input_dict["latex"]
            self.main_window.exact_ans = input_dict[first_key][0]
            self.main_window.approx_ans = input_dict[first_key][1]

            self.eout.setText(str(input_dict[first_key][0]))
            self.aout.setText(str(input_dict[first_key][1]))

    def stop_thread(self) -> None: ...

    def set_splitters(self, splitters: ty.List[QSplitter]) -> None:
        """Read splitter's state from QSettings by objectName"""
        self.main_window.settings.beginGroup(self.name)
        for splitter in splitters:
            state = self.main_window.settings.value(splitter.objectName())
            if not state:
                state = splitter.saveState().data()
            splitter.restoreState(state)
        self.main_window.settings.endGroup()

    def write_splitters(self, splitters: ty.List[QSplitter]) -> None:
        """Write splitter's state to QSettings by objectName"""
        self.main_window.settings.beginGroup(self.name)
        for splitter in splitters:
            state = splitter.saveState().data()
            self.main_window.settings.setValue(splitter.objectName(), state)
        self.main_window.settings.endGroup()
