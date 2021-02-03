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
    QCheckBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
)


class FieldsScrollArea(QScrollArea):
    def __init__(self, parent=None) -> None:
        super(FieldsScrollArea, self).__init__(parent)
        self._parent = parent

        self.scroll_grid = QGridLayout(self)

    def updateFields(self, data: ty.Dict[str, ty.Union[str, list, ty.Dict[str, str]]]) -> None:
        for i in reversed(range(self.scroll_grid.count())):
            self.scroll_grid.itemAt(i).widget().setParent(None)

        for i, field in enumerate(data["fields"]):
            if data[field]["type"] == "QLineEdit":
                label = QLabel(self)
                label.setText(data[field]["label"])
                label.setObjectName(field + "label")
                label.setFont(self._parent.font())

                qline = QLineEdit(self)
                qline.setFixedHeight(30)
                qline.setObjectName(field + "line")
                qline.setText(data[field]["default"])
                qline.setFont(self._parent.font())

                label.setToolTip(data[field]["tooltip"])
                qline.setToolTip(data[field]["tooltip"])

                self.scroll_grid.addWidget(label, i, 0)
                self.scroll_grid.addWidget(qline, i, 1)
            elif data[field]["type"] == "QCheckBox":
                checkbox = QCheckBox(self)
                checkbox.setText("")
                checkbox.setFont(self._parent.font())

                label = QLabel(self)
                label.setText(data[field]["label"])
                label.setFont(self._parent.font())

                label.setToolTip(data[field]["tooltip"])
                checkbox.setToolTip(data[field]["tooltip"])

                self.scroll_grid.addWidget(label, i, 0)
                self.scroll_grid.addWidget(checkbox, i, 1)

        self.scroll_grid.itemAtPosition(0, 1).widget().setFocus()

    def get_data(self) -> ty.List[str]:
        out = []
        for i in range(self.scroll_grid.count() // 2):
            widget = self.scroll_grid.itemAtPosition(i, 1).widget()
            if type(widget) == QCheckBox:
                _data = widget.isChecked()
            elif type(widget) == QLineEdit:
                _data = widget.text()
            else:
                _data = None
            out.append(_data)
        return out


class InputFSA(FieldsScrollArea):
    def __init__(self, parent=None):
        super(InputFSA, self).__init__(parent)

    def updateFields(self, input, data: ty.Dict[str, ty.Union[str, list, ty.Dict[str, str]]]) -> None:
        input.setPlainText(data["input"]["default"])
        input.setToolTip(data["input"]["tooltip"])
        return super(InputFSA, self).updateFields(data)
