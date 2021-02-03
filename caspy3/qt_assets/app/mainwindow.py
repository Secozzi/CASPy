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

# Third party
import matplotlib.pyplot as mpl
from pkg_resources import resource_filename
from pyperclip import copy
from sympy.abc import _clash1, _clash2

# PyQt5
from PyQt5.QtCore import QSettings, QSize, QThreadPool
from PyQt5.QtGui import QCloseEvent, QFont, QKeySequence
from PyQt5.QtWidgets import (
    QAction,
    QActionGroup,
    QApplication,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QShortcut,
    QWidget
)
from PyQt5.uic import loadUi

# Relative
from caspy3.qt_assets.tabs import get_tabs
from caspy3.qt_assets.dialogs.tab_list import TabList
from caspy3.qt_assets.dialogs.qsplitter_edit import SplitterEditor
from caspy3.qt_assets.widgets.latex_drag_label import DragLabel


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        # Load ui file
        loadUi(self.get_resource("qt_assets/app/mainwindow.ui"), self)

        # Initialize variables
        self.approx_ans: str = ""
        self.exact_ans: str = ""
        self.latex_ans: str = ""

        self.output_type: int = 1
        self.use_unicode: bool = False
        self.line_wrap: bool = False
        self.use_scientific: int = 0
        self.accuracy: int = 0
        self.use_latex: bool = False
        self.latex_fs: int = 150
        self.use_clash1: bool = False
        self.use_clash2: bool = False
        self.clashes: dict = {}
        self.fig = mpl.figure()

        # Qt variables
        self.settings: QSettings = QSettings(QSettings.IniFormat, QSettings.UserScope, "CASPy")
        self.qapp: QApplication = QApplication.instance()
        self.threadpool: QThreadPool = QThreadPool()
        self.tab_list: ty.List[QWidget] = get_tabs()
        self.tabs_font = QFont("Courier New", 8)
        self.main_font = QFont("Segoe UI", 9)

        # Functions
        self.read_settings()
        self.init_ui()

    @staticmethod
    def get_resource(relative_path: str) -> str:
        """
        Returns path to a file relative to source directory (CASPy/caspy3)
        """
        return resource_filename("caspy3", relative_path)

    @staticmethod
    def show_error_box(message: str) -> None:
        """
        Show a message box containing an error

        :param message: str
            The message that is to be displayed by the message box
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def read_settings(self) -> None:
        self.settings.beginGroup("mainwindow")

        self.output_type = self.settings.value("output_type", 1, int)
        self.use_clash1 = self.settings.value("use_clash1", False, bool)
        self.use_clash2 = self.settings.value("use_clash2", False, bool)
        self.use_unicode = self.settings.value("use_unicode", False, bool)
        self.line_wrap = self.settings.value("line_wrap", False, bool)
        self.use_scientific = self.settings.value("use_scientific", 0, int)
        self.accuracy = self.settings.value("accuracy", 10, int)
        self.use_latex = self.settings.value("use_latex", False, bool)
        self.latex_fs = self.settings.value("latex_fs", 150, int)

        self.resize(self.settings.value("size", QSize(1500, 900)))

        self.settings.endGroup()

    def write_settings(self) -> None:
        self.settings.beginGroup("mainwindow")

        self.settings.setValue("output_type", self.output_type)
        self.settings.setValue("use_clash1", self.use_clash1)
        self.settings.setValue("use_clash2", self.use_clash2)
        self.settings.setValue("use_unicode", self.use_unicode)
        self.settings.setValue("line_wrap", self.line_wrap)
        self.settings.setValue("use_scientific", self.use_scientific)
        self.settings.setValue("accuracy", self.accuracy)
        self.settings.setValue("use_latex", self.use_latex)
        self.settings.setValue("latex_fs", self.latex_fs)

        self.settings.setValue("size", self.size())
        self.settings.endGroup()

    def init_ui(self) -> None:
        # Displaying icon in taskbar
        try:
            from PyQt5.QtWinExtras import QtWin
            from caspy3 import version

            my_app_id = f"secozzi.caspy3.{''.join(map(str, version))}"
            QtWin.setCurrentProcessExplicitAppUserModelID(my_app_id)
        except ImportError:
            pass

        self.init_menu()
        self.init_tabs()
        self.init_shortcuts()

    def init_menu(self) -> None:
        """
        Initialize menu and add bindings to actions
        """
        # Set font
        self.setStyleSheet(f"QMenuBar {{font - size: {self.main_font.pointSize()}pt; font-family: {self.main_font.family()}}}")
        self.tab_manager.setFont(self.tabs_font)

        # For the QActionGroup Output Type -> Pretty - Latex - Normal
        self.output_type_group = QActionGroup(self.menu_output_type)
        self.output_type_group.addAction(self.action_pretty)
        self.output_type_group.addAction(self.action_latex)
        self.output_type_group.addAction(self.action_normal)
        self.output_type_group.setExclusive(True)
        self.output_type_group.triggered.connect(self.change_output_type)

        # For the QActionGroup SymPy Clashing -> _clash1 - _clash2
        self.clash_group = QActionGroup(self.menu_clashing)
        self.clash_group.addAction(self.action_clash1)
        self.action_clash1.setChecked(self.use_clash1)
        self.action_clash1.triggered.connect(self.toggle_clash1)
        self.clash_group.addAction(self.action_clash2)
        self.action_clash2.setChecked(self.use_clash2)
        self.action_clash2.triggered.connect(self.toggle_clash2)
        self.clash_group.setExclusive(False)

        # Object name of QAction and function to call when triggered
        action_bindings = {
            "action_unicode": self.toggle_unicode,
            "action_linewrap": self.toggle_line_wrap,
            "action_scientific_notation": self.toggle_use_scientific,
            "action_accuracy": self.change_accuracy,
            "action_tab_list": self.open_tab_list,
            "action_copy_exact_answer": self.copy_exact_ans,
            "action_copy_approximate_answer": self.copy_approx_ans,
            "action_next_tab": self.goto_next_tab,
            "action_previous_tab": self.goto_previous_tab,
            "action_edit_qsplitter": self.edit_qsplitter,
            "action_latex_fs": self.change_latex_fs,
            "action_use_latex": self.toggle_use_latex,
        }

        # Actions that are also checkable, value must be bool
        checkable_actions = {
            "action_unicode": self.use_unicode,
            "action_linewrap": self.line_wrap,
            "action_use_latex": self.use_latex,
            "action_scientific_notation": bool(self.use_scientific)
        }

        for action in (
            self.menu_settings.actions() +
            self.menu_copy.actions() +
            self.menu_tab.actions()
        ):
            action: QAction
            object_name = action.objectName()

            if object_name in action_bindings.keys():
                action.triggered.connect(action_bindings[object_name])

            if object_name in checkable_actions.keys():
                action.setChecked(checkable_actions[object_name])

        # Set text to QActions
        if self.use_scientific:
            self.action_scientific_notation.setText(
                f"Scientific Notation - {self.use_scientific}"
            )

        self.action_accuracy.setText(
            f"Accuracy - {self.accuracy}"
        )

        self.action_latex_fs.setText(
            f"LaTeX font-size - {self.latex_fs}"
        )

        # Set output type
        if self.output_type == 1:
            self.action_pretty.setChecked(True)
        elif self.output_type == 2:
            self.action_latex.setChecked(True)
        else:
            self.action_normal.setChecked(True)

        # Other
        self.update_clashes()

    def change_output_type(self, action: QAction) -> None:
        types = ["Pretty", "Latex", "Normal"]
        self.output_type = types.index(action.text()) + 1

    def toggle_unicode(self, state: bool) -> None:
        self.use_unicode = state

    def toggle_line_wrap(self, state: bool) -> None:
        self.line_wrap = state

    def toggle_clash1(self, state: bool) -> None:
        self.use_clash1 = state
        self.update_clashes()

    def toggle_clash2(self, state: bool) -> None:
        self.use_clash2 = state
        self.update_clashes()

    def update_clashes(self) -> None:
        if self.use_clash1 and self.use_clash2:
            self.clashes = {**_clash1, **_clash2}
        elif self.use_clash1 and not self.use_clash2:
            self.clashes = _clash1
        elif not self.use_clash1 and self.use_clash2:
            self.clashes = _clash2
        else:
            self.clashes = {}

    def get_scientific_notation(self) -> int:
        """
        Get accuracy of scientific notation. An accuracy
        of 0 indicates that scientific notation is disabled
        """
        number, confirmed = QInputDialog.getInt(
            self,
            "Get scientific notation",
            "Enter the accuracy for scientific notation",
            5,
            1,
            999999,
            1,
        )
        if confirmed:
            return number
        else:
            return 0

    def toggle_use_scientific(self, state: bool) -> None:
        if state:
            self.use_scientific = self.get_scientific_notation()
            if self.use_scientific:
                self.action_scientific_notation.setChecked(True)
                self.action_scientific_notation.setText(
                    f"Scientific Notation - {self.use_scientific}"
                )
            else:
                self.action_scientific_notation.setChecked(False)
                self.action_scientific_notation.setText(
                    f"Scientific Notation"
                )
        else:
            self.use_scientific = 0
            self.action_scientific_notation.setChecked(False)
            self.action_scientific_notation.setText(
                f"Scientific Notation"
            )

    def get_accuracy(self) -> int:
        number, confirmed = QInputDialog.getInt(
            self,
            "Get accuracy",
            "Enter accuracy for evaluation",
            self.accuracy,
            1,
            999999,
            1,
        )
        if confirmed:
            return number

    def change_accuracy(self) -> None:
        self.accuracy = self.get_accuracy()
        self.action_accuracy.setText(
            f"Accuracy - {self.accuracy}"
        )

    def toggle_use_latex(self, state: bool) -> None:
        self.use_latex = state

    def get_latex_fs(self) -> int:
        """Get font-size used by LaTeX renderer"""
        number, confirmed = QInputDialog.getInt(
            self,
            "LaTeX font-size",
            "Enter font-size used by LaTeX renderer. Higher font-size equals greater resolution",
            self.latex_fs,
            1,
            999999,
            1,
        )
        if confirmed:
            return number

    def change_latex_fs(self) -> None:
        self.latex_fs = self.get_latex_fs()
        self.action_latex_fs.setText(
            f"LaTeX font-size - {self.latex_fs}"
        )

    def copy_exact_ans(self) -> None:
        print(self.clashes)
        if type(self.exact_ans) == list:
            if len(self.exact_ans) == 1:
                copy(str(self.exact_ans[0]))
            else:
                copy(str(self.exact_ans))
        else:
            copy(str(self.exact_ans))

    def copy_approx_ans(self) -> None:
        if type(self.approx_ans) == list:
            if len(self.approx_ans) == 1:
                copy(str(self.approx_ans[0]))
            else:
                copy(str(self.approx_ans))
        else:
            copy(str(self.approx_ans))

    def goto_next_tab(self) -> None:
        curr = self.tab_manager.currentIndex()
        if curr == self.tab_manager.count() - 1:
            self.tab_manager.setCurrentIndex(0)
        else:
            self.tab_manager.setCurrentIndex(curr + 1)

    def goto_previous_tab(self) -> None:
        curr = self.tab_manager.currentIndex()
        if curr == 0:
            self.tab_manager.setCurrentIndex(self.tab_manager.count() - 1)
        else:
            self.tab_manager.setCurrentIndex(curr - 1)

    def edit_qsplitter(self) -> None:
        self.qsedit = SplitterEditor(self.tab_manager.currentWidget())
        self.qsedit.show()
        self.qsedit.update_splitter()

    def open_tab_list(self) -> None:
        # TODO: Tab list
        self.tab_list = TabList(self)

    def init_tabs(self) -> None:
        self.tab_manager.clear()
        for tab in self.tab_list:
            _tab = tab(main_window=self)
            self.tab_manager.addTab(_tab, tab.display_name)
            if self.use_latex:
                _tab.out_splitter.insertWidget(1, DragLabel(_tab))
            _tab.set_splitters(_tab.splitters)

    def init_shortcuts(self) -> None:
        cshortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        cshortcut.activated.connect(
            lambda: self.tab_manager.currentWidget().calculate()
        )
        pshortcut = QShortcut(QKeySequence("Ctrl+Shift+Return"), self)
        pshortcut.activated.connect(
            lambda: self.tab_manager.currentWidget().preview()
        )

        s1 = QShortcut(QKeySequence("Alt+1"), self)
        s2 = QShortcut(QKeySequence("Alt+2"), self)
        s3 = QShortcut(QKeySequence("Alt+3"), self)
        s4 = QShortcut(QKeySequence("Alt+4"), self)
        s5 = QShortcut(QKeySequence("Alt+5"), self)
        s6 = QShortcut(QKeySequence("Alt+6"), self)
        s7 = QShortcut(QKeySequence("Alt+7"), self)
        s8 = QShortcut(QKeySequence("Alt+8"), self)
        s9 = QShortcut(QKeySequence("Alt+9"), self)

        s1.activated.connect(lambda: self.goto_tab(1))
        s2.activated.connect(lambda: self.goto_tab(2))
        s3.activated.connect(lambda: self.goto_tab(3))
        s4.activated.connect(lambda: self.goto_tab(4))
        s5.activated.connect(lambda: self.goto_tab(5))
        s6.activated.connect(lambda: self.goto_tab(6))
        s7.activated.connect(lambda: self.goto_tab(7))
        s8.activated.connect(lambda: self.goto_tab(8))
        s9.activated.connect(lambda: self.goto_tab(9))

    def goto_tab(self, tab: int) -> None:
        if tab <= self.tab_manager.count():
            self.tab_manager.setCurrentIndex(tab - 1)

    def closeEvent(self, event: QCloseEvent) -> None:
        print("CLOSING MAIN")
        self.write_settings()
        event.accept()
