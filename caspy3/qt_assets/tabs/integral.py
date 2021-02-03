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
import json

# Third party
import sympy as sy

# PyQt5
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QSplitter,
    QWidget,
)
from PyQt5.uic import loadUi

# Relative
from caspy3.qt_assets.widgets.tab import CaspyTab
from caspy3.qt_assets.widgets.worker import BaseWorker

if ty.TYPE_CHECKING:
    from caspy3.qt_assets.widgets.searchable_combo import SearchableComboBox
    from caspy3.qt_assets.widgets.fields_scroll import InputFSA
    from caspy3.qt_assets.app.mainwindow import MainWindow
    from caspy3.qt_assets.widgets.input import TextEdit
    from caspy3.qt_assets.widgets.output import OutputWidget


class IntegralWorker(BaseWorker):
    def __init__(
        self, command: str, params: list, copy: ty.Union[int, None] = None
    ) -> None:
        super().__init__(command, params, copy)

    @pyqtSlot()
    def prev_integral(
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

        approx_ans = ""
        exact_ans = ""
        latex_ans = ""

        if not input_expression:
            return {"error": ["Enter an expression"]}
        if not input_variable:
            return {"error": ["Enter a variable"]}

        try:
            expr = sy.parse_expr(input_expression, local_dict=clashes)
            var = sy.parse_expr(input_variable, local_dict=clashes)

            return {"deriv": [exact_ans, approx_ans], "latex": latex_ans}
        except:
            return {"error": [f"Error: \n{traceback.format_exc()}"]}

    @pyqtSlot()
    def calc_integ(
        self,
        input_expression: str,
        method: str,
        data: ty.List[ty.Any],
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

        try:
            expr = sy.parse_expr(input_expression, local_dict=clashes)

            if method == "Integrate":
                var = sy.parse_expr(data[0])
                lower = data[1]
                upper = data[2]
                approx = data[3]

                if not (lower or upper):
                    exact_ans = sy.Integral(expr, var)
                elif lower and not upper:
                    exact_ans = sy.Integral(expr, (var, sy.parse_expr(lower)))
                elif lower and upper:
                    exact_ans = sy.Integral(expr, (var, sy.parse_expr(lower), sy.parse_expr(upper)))
                else:
                    return {"error": ["Cannot integrate with only upper boundary"]}

                if approx:
                    exact_ans = sy.N(exact_ans, accuracy)
                else:
                    exact_ans = exact_ans.doit()

                approx_ans = str(sy.N(exact_ans, accuracy))
                if use_scientific:
                    approx_ans = self.to_scientific_notation(approx_ans, use_scientific)
                latex_ans = str(sy.latex(exact_ans))

            elif method == "Line Integral":
                curve = sy.parse_expr(data[0])
                if curve.__class__ != sy.Curve:
                    return {"error": [f"'Curve' must be of class Curve, not {curve.__class__}"]}
                variables = sy.parse_expr(data[1])
                if not all([i.__class__ == sy.Symbol for i in variables]):
                    return {"error": [f"All variables must be symbols, not {[i.__class__ == sy.Symbol for i in variables]}"]}

                exact_ans = sy.line_integrate(expr, curve, variables)
                approx_ans = sy.N(exact_ans, accuracy)
                if use_scientific:
                    approx_ans = self.to_scientific_notation(approx_ans, use_scientific)
                latex_ans = str(sy.latex(exact_ans))

            elif method == "Mellin Transform":
                var = sy.parse_expr(data[0])
                s = sy.parse_expr(data[1])
                sol_tuple = sy.mellin_transform(expr, var, s)

                if isinstance(sol_tuple, sy.MellinTransform):
                    exact_ans = sol_tuple
                else:
                    exact_ans = sol_tuple[:2]
                latex_ans = str(sy.latex(sol_tuple))
                approx_ans = sol_tuple[2]

            elif method == "Inverse Mellin Transform":
                var = sy.parse_expr(data[0])
                s = sy.parse_expr(data[1])
                strip = sy.parse_expr(data[2])
                exact_ans = sy.inverse_mellin_transform(expr, s, var, strip)
                latex_ans = str(sy.latex(exact_ans))
                approx_ans = "..."

            else:
                return {"error": [f"Method '{method}' not found"]}

            if output_type == 1:
                exact_ans = str(sy.pretty(exact_ans))
            elif output_type == 2:
                exact_ans = latex_ans
            else:
                exact_ans = str(exact_ans)

            latex_ans = latex_ans.replace(r"\text", r"\mathrm")

            return {"integ": [exact_ans, approx_ans], "latex": latex_ans}
        except:
            return {"error": [f"Error: \n{traceback.format_exc()}"]}


class IntegralTab(CaspyTab):

    display_name = "Integrals"
    name = "integral"

    def __stubs(self) -> None:
        """Stubs for auto-completion"""
        self.integ_approx = OutputWidget(self)
        self.integ_calc = QPushButton()
        self.integ_exact = OutputWidget(self)
        self.integ_input = TextEdit(self)
        self.integ_methods_combo = SearchableComboBox(self)
        self.integ_methods_label = QLabel()
        self.integ_prev = QPushButton()
        self.integ_main_splitter = QSplitter()
        self.integ_input_splitter = QSplitter()
        self.integ_output_splitter = QSplitter()
        self.integral_tab = QWidget()
        self.methods_scroll_area = InputFSA()
        self.methods_scroll_area_contents = QWidget()
        self.verticalLayoutWidget = QWidget()

        raise AssertionError("This should never be called")

    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window, self.name)
        loadUi(self.main_window.get_resource("qt_assets/tabs/integral.ui"), self)
        self.setStyleSheet(
            f"font-size: {self.main_window.tabs_font.pointSize()}pt;font-family: {self.main_window.tabs_font.family()};"
        )

        self.eout = self.integ_exact
        self.aout = self.integ_approx
        self.out_splitter = self.integ_output_splitter

        self.splitters: ty.List[QSplitter] = [
            self.integ_main_splitter,
            self.integ_input_splitter,
            self.integ_output_splitter,
        ]

        self.methods_list = []
        self.read_data()

        self.init_bindings()
        self.init_methods()

    def read_data(self) -> None:
        with open(self.main_window.get_resource("data/integ_methods.json"), "r") as f:
            self.integ_methods = json.loads(f.read())
        for item in self.integ_methods:
            self.methods_list.append(item["name"])

    def init_methods(self) -> None:
        for item in self.integ_methods:
            self.integ_methods_combo.addItem(item["name"])

    def init_bindings(self) -> None:
        self.integ_methods_combo.currentIndexChanged.connect(
            lambda i: self.methods_scroll_area.updateFields(self.integ_input, self.integ_methods[i])
        )
        self.integ_prev.clicked.connect(self.preview)
        self.integ_calc.clicked.connect(self.calculate)

    def calculate(self) -> None:
        """Calculate from input, gets called on Ctrl+Return"""
        self.eout.set_cursor(Qt.WaitCursor)
        self.aout.set_cursor(Qt.WaitCursor)

        _method = self.integ_methods_combo.currentText()
        if _method not in self.methods_list:
            self.main_window.show_error_box(f"{_method} isn't a valid method.")
            return

        worker = IntegralWorker(
            "calc_integ",
            [
                self.integ_input.toPlainText(),
                self.integ_methods_combo.currentText(),
                self.methods_scroll_area.get_data(),
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

    def close_event(self) -> None:
        self.write_splitters(self.splitters)
