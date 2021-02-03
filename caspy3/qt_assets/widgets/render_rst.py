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
from inspect import getfullargspec
import typing as ty
import re

# Third party
from pkg_resources import resource_filename
import matplotlib.pyplot as mpl

# PyQt5
from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtCore import QTemporaryFile
from PyQt5.QtGui import QFont

# Relative
from caspy3.qt_assets.latex_pixmap import mathTex_to_QPixmap

from sympy import Sum


class RichRenderer(QTextBrowser):
    """
    A very simple rst to html converter used to display
    the docstring of a SymPy function. Does not have full
    rst support but most of those found in SymPy's
    documentation. Takes half a second to load :/
    """
    def __init__(self, parent=None):
        super(RichRenderer, self).__init__(parent)
        self.fig = mpl.figure()
        self.document().setDocumentMargin(40)
        function = Sum.is_convergent

        text = function.__doc__

        text = re.sub(r"(?: *).. ?math ?::(?:[\s]*)(.*)", self.generate_latex, text, re.DOTALL)  # Generate latex
        text = re.sub(r"(?:\n +)?``([^`]*)``", self.code_block, text, re.DOTALL)  # Convert code block
        text = re.sub(r"`([^`]*)`", self.expression, text, re.DOTALL)  # Convert expression
        text = re.sub(r":\w+:", "", text)  # Remove that

        paragraphs = text.split("\n\n")  # Convert doctest into mono text
        for i in range(len(paragraphs)):
            if ">>>" in paragraphs[i]:
                new = paragraphs[i].replace(">", "&#62;")
                new = new.replace("<", "&#60;")
                paragraphs[i] =  f"<span style='font-family: Courier New;'>{new}</span>"
        text = "\n\n".join(paragraphs)

        text = re.sub(r">>>.*\n+([^>].+)", self.mono, text, re.DOTALL)
        text = re.sub(r"(>>>.*)", self.mono, text, re.DOTALL)
        text = text.replace("\n", "<br>")  # Convert newline to break tag

        self.setFont(QFont("SansSerif", 12))
        self.setHtml(self.get_function_args(function))
        self.append(text)

        self.setLineWrapMode(QTextBrowser.NoWrap)

    def generate_latex(self, match: re.Match) -> str:
        pixmap = mathTex_to_QPixmap(
            f"${match.group(1)}$",
            15,
            fig=self.fig
        )
        file = QTemporaryFile(self)
        if file.open():
            pixmap.save(file, "PNG")
            path = file.fileName()
            file.close()
        return f"<p style='text-align:center'><img src='{path}'></p>"

    @staticmethod
    def get_function_args(func: ty.Callable) -> str:
        args = ""
        info = getfullargspec(func)
        args += str(", ".join(info.args)) if info.args else ""
        args += f", *{info.varargs}" if info.varargs else ""
        args += ", " + str(", ".join(
            [f"{k}={i}" for k, i in info.kwonlydefaults.items()]
        )) if info.kwonlydefaults else ""
        args += f", **{info.varkw}" if info.varkw else ""
        return f"<p style='font-family: Courier New;'><b>{func.__name__}</b>(<i>{args}</i>)</p>"

    @staticmethod
    def code_block(match: re.Match) -> str:
        text = match.group(1)
        text = text.replace(">", "&#62;")
        text = text.replace("<", "&#60;")
        return f"<span style='font-family: Courier New;background-color: #ECF0F3;'>{text}</span>"

    @staticmethod
    def mono(match: re.Match) -> str:
        text = match.group(1)
        text = text.replace(">", "&#62;")
        text = text.replace("<", "&#60;")
        return f"<span style='font-family: Courier New;'>{text}</span>"

    @staticmethod
    def expression(match: re.Match) -> str:
        text = match.group(1)
        text = text.replace(">", "&#62;")
        text = text.replace("<", "&#60;")
        return f"<code><b><i>{text}</i></b></code>"


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)

    ex = RichRenderer()
    ex.resize(900, 800)
    ex.show()
    sys.exit(app.exec_())