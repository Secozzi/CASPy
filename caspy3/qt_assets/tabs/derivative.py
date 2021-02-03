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
import traceback

# Third party
import sympy as sy

# PyQt5
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QSplitter,
    QWidget,
)
from PyQt5.uic import loadUi

# Relative
from caspy3.qt_assets.widgets.tab import CaspyTab
from caspy3.qt_assets.widgets.worker import BaseWorker

if ty.TYPE_CHECKING:
    from caspy3.qt_assets.app.mainwindow import MainWindow
    from caspy3.qt_assets.widgets.input import TextEdit
    from caspy3.qt_assets.widgets.output import OutputWidget


class DerivativeWorker(BaseWorker):
    def __init__(
        self, command: str, params: list, copy: ty.Union[int, None] = None
    ) -> None:
        super().__init__(command, params, copy)

    @pyqtSlot()
    def prev_deriv(
        self,
        input_expression: str,
        input_variable: str,
        input_order: int,
        input_point: str,
        output_type: int,
        use_unicode: bool,
        line_wrap: bool,
        clashes: ty.Dict[str, sy.Symbol],
    ) -> ty.Dict[str, ty.List[str]]:
        sy.init_printing(use_unicode=use_unicode, wrap_line=line_wrap)

        approx_ans = "..."
        exact_ans = ""
        latex_ans = ""

        if not input_expression:
            return {"error": ["Enter an expression"]}
        if not input_variable:
            return {"error": ["Enter a variable"]}

        try:
            expr = sy.parse_expr(input_expression, local_dict=clashes)
            var = sy.parse_expr(input_variable, local_dict=clashes)

            derivative = sy.Derivative(expr, var, input_order)
            latex_ans = str(sy.latex(derivative))

            if input_point:
                exact_ans = f"At {input_variable} = {input_point}\n"

            if output_type == 1:
                exact_ans += str(sy.pretty(derivative))
            elif output_type == 2:
                exact_ans += latex_ans
            else:
                exact_ans += str(derivative)

            return {"deriv": [exact_ans, approx_ans], "latex": latex_ans}
        except:
            return {"error": [f"Error: \n{traceback.format_exc()}"]}

    @pyqtSlot()
    def calc_deriv(
        self,
        input_expression: str,
        input_variable: str,
        input_order: int,
        input_point: str,
        output_type: int,
        use_unicode: bool,
        line_wrap: bool,
        clashes: dict,
        use_scientific: int,
        accuracy: int,
    ) -> ty.Dict[str, ty.List[str]]:
        sy.init_printing(use_unicode=use_unicode, wrap_line=line_wrap)

        approx_ans = "..."
        exact_ans = ""
        latex_ans = ""

        if use_scientific:
            if use_scientific > accuracy:
                accuracy = use_scientific

        if not input_expression:
            return {"error": ["Enter an expression"]}
        if not input_variable:
            return {"error": ["Enter a variable"]}

        try:
            expr = sy.parse_expr(input_expression, local_dict=clashes)
            var = sy.parse_expr(input_variable, local_dict=clashes)

            exact_ans = sy.diff(expr, var, input_order)
            latex_ans = str(sy.latex(exact_ans))

            if input_point:
                point = sy.parse_expr(input_point, local_dict=clashes)
                exact_ans = exact_ans.subs(var, point)

                approx_ans = str(sy.N(exact_ans, accuracy))
                if use_scientific:
                    approx_ans = self.to_scientific_notation(approx_ans, use_scientific)
                latex_ans = str(sy.latex(exact_ans))

            if output_type == 1:
                exact_ans = str(sy.pretty(exact_ans))
            elif output_type == 2:
                exact_ans = latex_ans
            else:
                exact_ans = str(exact_ans)

            return {"deriv": [exact_ans, approx_ans], "latex": latex_ans}

        except:
            return {"error": [f"Error: \n{traceback.format_exc()}"]}


class DerivativeTab(CaspyTab):

    display_name = "Derivative"
    name = "derivative"

    def __stubs(self) -> None:
        """Stubs for auto-completion"""
        self.deriv_approx = OutputWidget(self)
        self.deriv_calc = QPushButton()
        self.deriv_exact = OutputWidget(self)
        self.deriv_input = TextEdit(self)
        self.deriv_order_input = QSpinBox()
        self.deriv_order_label = QLabel()
        self.deriv_point_input = QLineEdit()
        self.deriv_point_label = QLabel()
        self.deriv_prev = QPushButton()
        self.deriv_main_splitter = QSplitter()
        self.deriv_out_splitter = QSplitter()
        self.deriv_tab = QWidget()
        self.deriv_var_input = QLineEdit()
        self.deriv_var_label = QLabel()
        self.verticalLayoutWidget = QWidget()

        raise AssertionError("This should never be called")

    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window, self.name)
        loadUi(self.main_window.get_resource("qt_assets/tabs/derivative.ui"), self)
        self.setStyleSheet(
            f"font-size: {self.main_window.tabs_font.pointSize()}pt; font-family: {self.main_window.tabs_font.family()};"
        )

        self.eout = self.deriv_exact
        self.aout = self.deriv_approx
        self.out_splitter = self.deriv_out_splitter

        self.splitters: ty.List[QSplitter] = [
            self.deriv_main_splitter,
            self.deriv_out_splitter,
        ]

        self.init_bindings()

    def init_bindings(self) -> None:
        self.deriv_prev.clicked.connect(self.preview)
        self.deriv_calc.clicked.connect(self.calculate)

    def calculate(self) -> None:
        """Calculate from input, gets called on Ctrl+Return"""
        self.eout.set_cursor(Qt.WaitCursor)
        self.aout.set_cursor(Qt.WaitCursor)

        # input_expression: str,
        # input_variable: str,
        # input_order: int,
        # input_point: str,
        # output_type: int,
        # use_unicode: bool,
        # line_wrap: bool,
        # clashes: dict,
        # use_scientific: int,
        # accuracy: int,

        worker = DerivativeWorker(
            "calc_deriv",
            [
                self.deriv_input.toPlainText(),
                self.deriv_var_input.text(),
                self.deriv_order_input.value(),
                self.deriv_point_input.text(),
                self.main_window.output_type,
                self.main_window.use_unicode,
                self.main_window.line_wrap,
                self.main_window.clashes,
                self.main_window.use_scientific,
                self.main_window.accuracy,
            ],
        )
        worker.signals.output.connect(self.update_ui)
        worker.signals.finished.connect(self.stop_thread)

        self.main_window.threadpool.start(worker)

    def preview(self) -> None:
        """Preview from input, get called on Ctrl+Shift+Return"""
        self.eout.set_cursor(Qt.WaitCursor)
        self.aout.set_cursor(Qt.WaitCursor)

        # input_expression: str,
        # input_variable: str,
        # input_order: int,
        # input_point: str,
        # output_type: int,
        # use_unicode: bool,
        # line_wrap: bool,
        # clashes: ty.Dict[str, sy.Symbol],

        worker = DerivativeWorker(
            "prev_deriv",
            [
                self.deriv_input.toPlainText(),
                self.deriv_var_input.text(),
                self.deriv_order_input.value(),
                self.deriv_point_input.text(),
                self.main_window.output_type,
                self.main_window.use_unicode,
                self.main_window.line_wrap,
                self.main_window.clashes,
            ],
        )
        worker.signals.output.connect(self.update_ui)
        worker.signals.finished.connect(self.stop_thread)

        self.main_window.threadpool.start(worker)

    def close_event(self) -> None:
        self.write_splitters(self.splitters)
