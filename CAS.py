# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QFont
from PyQt5.QtWebEngineWidgets import *

from sympy import *
from sympy.parsing.sympy_parser import parse_expr
from sympy.abc import _clash1

from pyperclip import copy

import os
import sys
import json
import traceback

x, y, z, t = symbols('x y z t')
k, m, n = symbols('k m n', integer=True)
f, g, h = symbols('f g h', cls=Function)


class Ui_MainWindow(object):
    def __init__(self, *args, **kwargs):
        super(Ui_MainWindow, self).__init__(*args, **kwargs)

        self.exactAns = ""
        self.currentSide = ""

        self.approxAns = 0

        self.useUniC = False
        self.lineWrap = False

        init_printing(use_unicode=self.useUniC, wrap_line=self.lineWrap)

    # For debugging purposes
    def raise_error(self):
        assert False

    def showErrorBox(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def copyExact(self):
        copy(self.exactAns)

    def copyApprox(self):
        copy(self.approxAns)

    def toggleUni(self, state):
        if state:
            self.useUniC = True
            init_printing(use_unicode=self.useUniC, wrap_line=self.lineWrap)
        else:
            self.useUniC = False
            init_printing(use_unicode=self.useUniC, wrap_line=self.lineWrap)

    def toggleWrap(self, state):
        if state:
            self.lineWrap = True
            init_printing(use_unicode=self.useUniC, wrap_line=self.lineWrap)
        else:
            self.lineWrap = False
            init_printing(use_unicode=self.useUniC, wrap_line=self.lineWrap)

    def nextTab(self):
        if self.tabWidget.currentIndex() == 7:
            self.tabWidget.setCurrentIndex(0)
        else:
            self.tabWidget.setCurrentIndex(self.tabWidget.currentIndex() + 1)

    def previousTab(self):
        if self.tabWidget.currentIndex() == 0:
            self.tabWidget.setCurrentIndex(7)
        else:
            self.tabWidget.setCurrentIndex(self.tabWidget.currentIndex() - 1)

    def prevDeriv(self):
        if not self.DerivExp.toPlainText():
            self.showErrorBox("Please enter an expression")
            return 0
        if not self.DerivVar.text():
            self.showErrorBox("Please enter a variable")
            return 0
        self.approxAns = 0
        derivative = Derivative(str(self.DerivExp.toPlainText()), self.DerivVar.text(), self.DerivOrder.value())
        if self.DerivPP.isChecked():
            self.exactAns = str(pretty(derivative))
        elif self.DerivLatex.isChecked():
            self.exactAns = str(latex(derivative))
        else:
            self.exactAns = str(derivative)
        self.DerivOut.setText(self.exactAns)

    def prevInteg(self):
        if not self.checkInteg():
            return 0

        self.approxAns = 0
        if self.IntegLower.text():
            self.exactAns = Integral(parse_expr(self.IntegExp.toPlainText()),
                                     (parse_expr(self.IntegVar.text()), self.IntegLower.text(), self.IntegUpper.text()))

        else:
            self.exactAns = Integral(parse_expr(self.IntegExp.toPlainText()), parse_expr(self.IntegVar.text()))

        if self.IntegPP.isChecked():
            self.exactAns = pretty(self.exactAns)
        elif self.IntegLatex.isChecked():
            self.exactAns = latex(self.exactAns)

        self.exactAns = str(self.exactAns)
        self.IntegOut.setText(self.exactAns)

    def prevLimit(self):
        if not self.checkLimit():
            return 0

        self.currentSide = self.getCurrentSide()

        self.exactAns = Limit(parse_expr(self.LimExp.toPlainText()), parse_expr(self.LimVar.text()),
                              self.LimApproach.text(), self.currentSide)
        self.approxAns = 0
        if self.LimPP.isChecked():
            self.LimOut.setText(str(pretty(self.exactAns)))
        elif self.LimLatex.isChecked():
            self.LimOut.setText(str(latex(self.exactAns)))
        else:
            self.LimOut.setText(str(self.exactAns))

    def prevEq(self):
        if not self.EqLeft.toPlainText() or not self.EqRight.toPlainText():
            self.showErrorBox("Please enter expression both in left and right side")
            return 0

        if not self.EqVar.text():
            self.showErrorBox("Please enter a variable")
            return 0

        self.approxAns = 0
        if self.EqPP.isChecked():
            if self.EqOut.toPlainText() == "" or self.EqOut.toPlainText()[0:10] == "Right side":
                self.EqToOut = "Left side, click again for right side\n"
                self.EqToOut += str(pretty(parse_expr(self.EqLeft.toPlainText())))
                self.exactAns = self.EqToOut
            else:
                self.EqToOut = "Right side, click again for left side\n"
                self.EqToOut += str(pretty(parse_expr(self.EqRight.toPlainText())))
                self.exactAns = self.EqToOut
        elif self.EqLatex.isChecked():
            self.exactAns = latex(parse_expr(self.EqLeft.toPlainText())) + " = " + latex(
                parse_expr(self.EqRight.toPlainText()))
        else:
            self.exactAns = str(self.EqLeft.toPlainText()) + " = " + str(self.EqRight.toPlainText())

        self.EqOut.setText(str(self.exactAns))
        self.EqApprox.setText(str(self.approxAns))

    def prevSimpEq(self):
        if not self.SimpExp.toPlainText():
            self.showErrorBox("Please enter an expression")
            return 0

        self.exactAns = str(self.SimpExp.toPlainText())
        self.approxAns = 0

        if self.SimPP.isChecked():
            self.SimpOut.setText(str(pretty(self.exactAns)))
        elif self.SimpLatex.isChecked():
            self.SimpOut.setText(str(latex(self.exactAns)))
        else:
            self.SimpOut.setText(str(self.exactAns))

    def prevExpEq(self):
        if not self.ExpExp.toPlainText():
            self.showErrorBox("Please enter an expression")
            return 0

        self.exactAns = str(self.ExpExp.toPlainText())
        self.approxAns = 0

        if self.ExpPP.isChecked():
            self.ExpOut.setText(str(pretty(self.exactAns)))
        elif self.ExpLatex.isChecked():
            self.ExpOut.setText(str(latex(self.exactAns)))
        else:
            self.ExpOut.setText(str(self.exactAns))

    def prevEvalEq(self):
        if not self.EvalExp.toPlainText():
            self.showErrorBox("Please enter an expression")
            return 0

        self.approxAns = 0

        if self.EvalPP.isChecked():
            self.exactAns = str(pretty(self.EvalExp.toPlainText()))
        elif self.EvalLatex.isChecked():
            self.exactAns = str(latex(self.EvalExp.toPlainText()))
        else:
            self.exactAns = str(self.exactAns)

        self.EvalOut.setText(self.exactAns)

    def calcDeriv(self):
        if not self.DerivExp.toPlainText():
            self.showErrorBox("Please enter an expression")
            return 0

        if not self.DerivVar.text():
            self.showErrorBox("Please enter a variable")
            return 0

        self.exactAns = diff(parse_expr(self.DerivExp.toPlainText()), parse_expr(self.DerivVar.text()),
                             self.DerivOrder.value())
        QApplication.processEvents()

        if self.DerivPoint.text():
            if any(x in "abcdefghijklmnopqrstuvwxuzABCDEFGHIJKLMNOPQRSTUVWXYZ" for x in str(N(self.DerivPoint.text()))):
                self.showErrorBox("Point is not a valid number")
                return 0
            else:
                calcDerivP = str(self.exactAns).replace(self.DerivVar.text(), self.DerivPoint.text())
                self.DerivApprox.setText(str(N(calcDerivP)))
                QApplication.processEvents()
                self.approxAns = str(N(calcDerivP))
                QApplication.processEvents()
                if self.DerivPP.isChecked():
                    self.exactAns = str(pretty(simplify(calcDerivP)))
                elif self.DerivLatex.isChecked():
                    self.exactAns = str(latex(simplify(calcDerivP)))
                else:
                    self.exactAns = str(simplify(calcDerivP))
                self.DerivOut.setText(self.exactAns)

        else:
            if self.DerivPP.isChecked():
                self.exactAns = str(pretty(self.exactAns))
            elif self.DerivLatex.isChecked():
                self.exactAns = str(latex(self.exactAns))
            else:
                self.exactAns = str(self.exactAns)
            self.DerivOut.setText(self.exactAns)

    def checkInteg(self):
        if not self.IntegExp.toPlainText():
            self.showErrorBox("Please enter an expression")
            return False

        if not self.IntegVar.text():
            self.showErrorBox("Please enter a variable")
            return False

        if (self.IntegLower.text() and not self.IntegUpper.text()) or (
                not self.IntegLower.text() and self.IntegUpper.text()):
            self.showErrorBox("Please enter both upper and lower")
            return False

        return True

    def calcInteg(self):
        if not self.checkInteg():
            return 0

        if self.IntegLower.text():
            self.exactAns = integrate(parse_expr(self.IntegExp.toPlainText()),
                                      (
                                      parse_expr(self.IntegVar.text()), self.IntegLower.text(), self.IntegUpper.text()))
            QApplication.processEvents()

            try:
                self.approxAns = str(N(self.exactAns))
            except:
                self.approxAns = "0"
                self.IntegApprox.setText("Could not evaluate")
                return 0
            else:
                self.IntegApprox.setText(str(N(self.exactAns)))
                self.approxAns = N(N(self.exactAns))

        else:
            self.exactAns = integrate(parse_expr(self.IntegExp.toPlainText()), parse_expr(self.IntegVar.text()))
            QApplication.processEvents()

        if self.IntegPP.isChecked():
            self.exactAns = str(pretty(self.exactAns))
        elif self.IntegLatex.isChecked():
            self.exactAns = str(latex(self.exactAns))
        self.exactAns = str(self.exactAns)
        self.IntegOut.setText(self.exactAns)

    def checkLimit(self):
        if not self.LimExp.toPlainText():
            self.showErrorBox("Please enter an expression")
            return False

        if not self.LimApproach.text():
            self.showErrorBox("Please enter value that the variable approaches")
            return False

        if not self.LimVar.text():
            self.showErrorBox("Please enter a variable")
            return False

        return True
    
    def getCurrentSide(self):
        if self.LimSide.currentIndex() == 0:
            return "+-"
        elif self.LimSide.currentIndex() == 1:
            return "-"
        else:
            return "+"

    def calcLimit(self):
        if not self.checkLimit():
            return 0
        
        self.currentSide = self.getCurrentSide()

        try:
            self.exactAns = limit(parse_expr(self.LimExp.toPlainText()), parse_expr(self.LimVar.text()),
                                  self.LimApproach.text(), self.currentSide)
        except ValueError:
            self.showErrorBox("Limit does not exist")
            return 0

        self.approxAns = str(N(self.exactAns))
        self.LimApprox.setText(str(self.approxAns))

        if self.LimPP.isChecked():
            self.LimOut.setText(str(pretty(self.exactAns)))
        elif self.LimLatex.isChecked():
            self.LimOut.setText(str(latex(self.exactAns)))
        else:
            self.LimOut.setText(str(self.exactAns))

    def calcEq(self):
        if not self.EqLeft.toPlainText() or not self.EqRight.toPlainText():
            self.showErrorBox("Please enter expression both in left and right side")
            return 0

        if not self.EqVar.text():
            self.showErrorBox("Please enter a variable")
            return 0

        self.leftSide = str(self.EqLeft.toPlainText())
        self.rightSide = str(self.EqRight.toPlainText())
        if self.EqSolve.isChecked():
            self.exactAns = solve(Eq(parse_expr(self.leftSide), parse_expr(self.rightSide)),
                                  parse_expr(self.EqVar.text()))
            approxList = [N(i) for i in self.exactAns]
            self.EqApprox.setText(str(approxList))
        if self.EqSolveSet.isChecked():
            self.exactAns = solveset(Eq(parse_expr(self.leftSide), parse_expr(self.rightSide)),
                                     parse_expr(self.EqVar.text()))
            self.approxAns = 0

        if self.EqPP.isChecked():
            self.exactAns = str(pretty(self.exactAns))
        elif self.EqLatex.isChecked():
            self.exactAns = str(latex(self.exactAns))
        else:
            self.exactAns = str(self.exactAns)

        self.EqOut.setText(self.exactAns)

    def simpEq(self):
        if not self.SimpExp.toPlainText():
            self.showErrorBox("Please enter an expression")
            return 0

        self.exactAns = simplify(self.SimpExp.toPlainText())
        self.approxAns = 0

        if self.SimpPP.isChecked():
            self.exactAns = str(pretty(self.exactAns))
        elif self.SimpLatex.isChecked():
            self.exactAns = str(latex(self.exactAns))
        else:
            self.exactAns = str(self.exactAns)
        self.SimpOut.setText(self.exactAns)

    def expEq(self):
        if not self.ExpExp.toPlainText():
            self.showErrorBox("Please enter an expression")
            return 0

        self.exactAns = expand(self.ExpExp.toPlainText())
        self.approxAns = 0

        if self.ExpPP.isChecked():
            self.exactAns = str(pretty(self.exactAns))
        elif self.ExpLatex.isChecked():
            self.exactAns = str(latex(self.exactAns))
        else:
            self.exactAns = str(self.exactAns)

        self.ExpOut.setText(self.exactAns)

    def evalExp(self):
        if not self.EvalExp.toPlainText():
            self.showErrorBox("Please enter an expression")
            return 0

        self.exactAns = simplify(parse_expr(self.EvalExp.toPlainText()))
        self.approxAns = N(self.exactAns)
        self.EvalApprox.setText(str(self.approxAns))

        if self.EvalPP.isChecked():
            self.exactAns = str(pretty(self.exactAns))
        elif self.EvalLatex.isChecked():
            self.exactAns = str(latex(self.exactAns))
        else:
            self.exactAns = str(self.exactAns)

        self.EvalOut.setText(self.exactAns)

    def calcPf(self):
        self.approxAns = 0
        self.exactAns = factorint(self.PfInput.value())
        self.PfOut.setText(str(self.exactAns))

    def FormulaTreeSelected(self):
        getSelected = self.FormulaTree.selectedItems()
        if getSelected:
            baseNode = getSelected[0]
            self.selectedTreeItem = baseNode.text(0)
            if "=" in self.selectedTreeItem:
                expr = self.selectedTreeItem.split("=")
                # expr = list(map(lambda x: x.replace("_i", "(sqrt(-1))"), expr))
                self.FormulaSymbolsList = [str(i) for i in list(parse_expr(expr[0], _clash1).atoms(Symbol))]
                self.FormulaSymbolsList.extend((str(i) for i in list(parse_expr(expr[1], _clash1).atoms(Symbol))))
                self.FormulaUpdateVars()
                self.FormulaInfo = self.FormulaGetInfo(self.selectedTreeItem, self.FormulaTreeData)
                self.FormulaSetInfoText()

    def FormulaSetInfoText(self):
        _translate = QtCore.QCoreApplication.translate
        lines = [[self.FormulaScrollArea.findChild(QtWidgets.QLineEdit, str(i) + "line"), i] for i in
                 self.FormulaLabelNames]
        for line in lines:
            for i in self.FormulaInfo:
                FormulaInfoList = i.split("|")
                if FormulaInfoList[0] == line[1]:
                    line[0].setStatusTip(_translate("MainWindow", f"{FormulaInfoList[1]}, mäts i {FormulaInfoList[2]}"))
                    line[0].setToolTip(_translate("MainWindow", FormulaInfoList[1]))
                elif FormulaInfoList[0].split(";")[0] == line[1]:
                    line[0].setStatusTip(_translate("MainWindow", f"{FormulaInfoList[1]}, mäts i {FormulaInfoList[2]}"))
                    line[0].setToolTip(_translate("MainWindow", FormulaInfoList[1]))
                    line[0].setText(FormulaInfoList[0].split(";")[1])

    def FormulaUpdateVars(self):
        # Clear the scroll area of any labels and QLineEdits
        for i in reversed(range(self.FormulaGrid2.count())):
            self.FormulaGrid2.itemAt(i).widget().setParent(None)
        # Generate, set name and position for labels and QLineEdits
        self.FormulaLabelNames = self.FormulaSymbolsList
        self.FormulaLabelPos = [[i, 0] for i in range(len(self.FormulaLabelNames))]
        self.FormulaLinePos = [[i, 1] for i in range(len(self.FormulaLabelNames))]
        for self.FormulaNameLabel, FormulaPosLabel, FormulaPosLine in zip(self.FormulaLabelNames, self.FormulaLabelPos,
                                                                          self.FormulaLinePos):
            self.FormulaLabel = QLabel(self.FormulaScrollArea)
            self.FormulaLabel.setText(self.FormulaNameLabel)
            self.FormulaGrid2.addWidget(self.FormulaLabel, *FormulaPosLabel)
            self.FormulaQLine = QLineEdit(self.FormulaScrollArea)
            self.FormulaQLine.setObjectName(self.FormulaNameLabel + "line")
            self.FormulaGrid2.addWidget(self.FormulaQLine, *FormulaPosLine)

    # Retrieves info from given formula, note that two formulas cannot be the same
    def FormulaGetInfo(self, text, data):
        for branch in data:
            for subBranch in branch[1]:
                for formula in subBranch[1]:
                    if formula[0] == text:
                        return formula[1]

    def prevFormula(self):
        try:
            lines = [[self.FormulaScrollArea.findChild(QtWidgets.QLineEdit, str(i) + "line"), i] for i in
                     self.FormulaLabelNames]
        except:
            self.showErrorBox("Select a formula")
        else:
            emptyVarList, varVarList, values = [], [], []
            for line in lines:
                if line[0].text() == "":
                    emptyVarList.append(line[1])
                elif line[0].text() == "var":
                    varVarList.append(line[1])
                else:
                    values.append([line[0].text(), line[1]])
            if len(emptyVarList) > 1 and len(varVarList) != 1:
                self.showErrorBox(
                    "Solve for only one variable, if multiple empty lines type 'var' to solve for the variable")
                return 0
            if len(varVarList) == 1:
                var = varVarList[0]
            else:
                var = emptyVarList[0]
            valuesString = self.selectedTreeItem.split("=")
            leftSide = valuesString[0]
            rightSide = valuesString[1]
            self.exactAns = solve(Eq(parse_expr(leftSide, _clash1), parse_expr(rightSide, _clash1)),
                                  parse_expr(var, _clash1))
            self.approxAns = 0
            if self.FormulaPP.isChecked():
                if self.FormulaExact.toPlainText() == "" or self.FormulaExact.toPlainText()[0:10] == "Right side":
                    self.FormulaToOut = "Left side, click again for right side\n"
                    self.FormulaToOut += str(pretty(parse_expr(var, _clash1)))
                    self.exactAns = self.FormulaToOut
                    self.FormulaExact.setText(self.exactAns)
                else:
                    self.FormulaToOut = "Right side, click again for left side\n"
                    self.FormulaToOut += str(pretty(self.exactAns))
                    self.exactAns = self.FormulaToOut
                    self.FormulaExact.setText(self.exactAns)
            elif self.FormulaLatex.isChecked():
                self.exactAns = latex(parse_expr(var)) + " = " + latex(parse_expr(self.exactAns))
                self.FormulaExact.setText(self.exactAns)
            else:
                self.exactAns = str(var) + " = " + str(self.exactAns)
                self.FormulaExact.setText(self.exactAns)
            self.FormulaApprox.setText(str(self.approxAns))

    def calcFormula(self):
        try:
            lines = [[self.FormulaScrollArea.findChild(QtWidgets.QLineEdit, str(i) + "line"), i] for i in
                     self.FormulaLabelNames]
        except:
            self.showErrorBox("Select a formula")
        else:
            emptyVarList, varVarList, values = [], [], []
            for line in lines:
                if line[0].text() == "":
                    emptyVarList.append(line[1])
                elif line[0].text() == "var":
                    varVarList.append(line[1])
                else:
                    values.append([line[0].text(), line[1]])
            if len(emptyVarList) > 1 and len(varVarList) != 1:
                self.showErrorBox(
                    "Solve for only one variable, if multiple empty lines type 'var' to solve for the variable")
                return 0
            if len(varVarList) == 1:
                var = varVarList[0]
            else:
                var = emptyVarList[0]
            valuesString = self.selectedTreeItem
            for i in values:
                valuesString = valuesString.replace(i[1], f"({i[0]})")
            leftSide = valuesString.split("=")[0]
            rightSide = valuesString.split("=")[1]
            if self.FormulaSolveSolve.isChecked():
                self.exactAns = solve(Eq(parse_expr(leftSide, _clash1), parse_expr(rightSide, _clash1)),
                                      parse_expr(var, _clash1))
                self.approxAns = list(map(lambda x: N(x), self.exactAns))
            if self.FormulaSolveSolveSet.isChecked():
                self.exactAns = solveset(Eq(parse_expr(leftSide, _clash1), parse_expr(rightSide, _clash1)),
                                         parse_expr(var, _clash1))
                self.approxAns = 0
            if self.FormulaPP.isChecked():
                self.FormulaExact.setText(str(pretty(self.exactAns)))
                self.FormulaApprox.setText(str(self.approxAns))
            elif self.FormulaLatex.isChecked():
                self.FormulaExact.setText(str(latex(self.exactAns)))
                self.FormulaApprox.setText(str(self.approxAns))
            else:
                self.FormulaExact.setText(str(self.exactAns))
                self.FormulaApprox.setText(str(self.approxAns))

    def executeCode(self):
        self.consoleIn.moveCursor(QtGui.QTextCursor.End)
        self.NewCode = self.consoleIn.toPlainText().replace(self.currentCode, "")
        if self.NewCode:
            if self.NewCode[0] == "\n":
                self.NewCode = self.NewCode[1:]
        if self.NewCode[0:4] == ">>> ":
            self.NewCode = self.NewCode[4:]
        self.NewCode = self.NewCode.replace("... ", "")
        self.toExecute = ""
        for i in self.alreadyExecuted:
            self.toExecute += f"{i}\n"
        self.toExecute += self.NewCode
        self.toExecute = self.toExecute.replace("\n\t", "|")
        for command in self.toExecute.split("\n"):
            newToExec = command.replace("|", "\n\t")
            try:
                exec(f"print({newToExec})")
            except:
                try:
                    exec(newToExec)
                except Exception as e:
                    self.consoleIn.insertPlainText(f"\nerror: {e}")
                else:
                    if newToExec not in self.alreadyExecuted:
                        self.alreadyExecuted.append(newToExec)
            else:
                self.consoleIn.insertPlainText("\n")
                exec(f"self.consoleIn.insertPlainText(str({newToExec}))")
                exec(f"self.exactAns = str({newToExec})")
                self.consoleIn.insertPlainText("\n")

        self.currentCode = self.consoleIn.toPlainText()
        self.consoleIn.insertPlainText("\n>>> ")
        self.consoleIn.moveCursor(QtGui.QTextCursor.End)

    def updateWeb(self, action):
        if action.text() == "Desmos":
            desmos_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "desmos.html"))
            self.web.load(QUrl.fromLocalFile(desmos_path))
        else:
            for i in self.WebList:
                for key in i:
                    if action.text() == key:
                        self.web.load(QUrl(i[key]))

    def setupUi(self, MainWindow):
        lowerReg = QtCore.QRegExp("[a-z]+")
        lowerVal = QtGui.QRegExpValidator(lowerReg)
        textReg = QtCore.QRegExp("[A-Za-z]+")
        textVal = QtGui.QRegExpValidator(textReg)

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1278, 806)
        MainWindow.setMinimumSize(QtCore.QSize(400, 350))
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777215))
        MainWindow.setFont(QFont("Courier New"))
        MainWindow.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setIconSize(QtCore.QSize(50, 24))

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setMinimumSize(QtCore.QSize(400, 25))
        self.tabWidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.tabWidget.setObjectName("tabWidget")

        self.Deriv = QtWidgets.QWidget()
        self.Deriv.setObjectName("Deriv")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.Deriv)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.DerivPrev = QtWidgets.QPushButton(self.Deriv)
        self.DerivPrev.setObjectName("DerivPrev")
        self.DerivPrev.clicked.connect(self.prevDeriv)
        self.gridLayout_2.addWidget(self.DerivPrev, 6, 0, 1, 2)
        self.DerivCalc = QtWidgets.QPushButton(self.Deriv)
        self.DerivCalc.setObjectName("DerivCalc")
        self.DerivCalc.clicked.connect(self.calcDeriv)
        self.gridLayout_2.addWidget(self.DerivCalc, 7, 0, 1, 2)
        self.label_9 = QtWidgets.QLabel(self.Deriv)
        self.label_9.setObjectName("label_9")
        self.gridLayout_2.addWidget(self.label_9, 4, 0, 1, 1)
        self.DerivExp = QtWidgets.QTextEdit(self.Deriv)
        self.DerivExp.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.DerivExp.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.DerivExp.setObjectName("DerivExp")
        self.gridLayout_2.addWidget(self.DerivExp, 0, 0, 3, 2)
        self.label = QtWidgets.QLabel(self.Deriv)
        self.label.setMaximumSize(QtCore.QSize(40, 16777215))
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 3, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.DerivOutType = QtWidgets.QLabel(self.Deriv)
        self.DerivOutType.setObjectName("DerivOutType")
        self.horizontalLayout.addWidget(self.DerivOutType)
        self.DerivPP = QtWidgets.QRadioButton(self.Deriv)
        self.DerivPP.setChecked(True)
        self.DerivPP.setObjectName("DerivPP")
        self.horizontalLayout.addWidget(self.DerivPP)
        self.DerivLatex = QtWidgets.QRadioButton(self.Deriv)
        self.DerivLatex.setObjectName("DerivLatex")
        self.horizontalLayout.addWidget(self.DerivLatex)
        self.DerivNormal = QtWidgets.QRadioButton(self.Deriv)
        self.DerivNormal.setObjectName("DerivNormal")
        self.horizontalLayout.addWidget(self.DerivNormal)
        self.gridLayout_2.addLayout(self.horizontalLayout, 8, 0, 1, 2)
        self.DerivOrder = QtWidgets.QSpinBox(self.Deriv)
        self.DerivOrder.setMinimumSize(QtCore.QSize(0, 25))
        self.DerivOrder.setMaximumSize(QtCore.QSize(16777215, 25))
        self.DerivOrder.setMinimum(1)
        self.DerivOrder.setMaximum(999)
        self.DerivOrder.setObjectName("DerivOrder")
        self.gridLayout_2.addWidget(self.DerivOrder, 3, 1, 1, 1)
        self.DerivVar = QtWidgets.QLineEdit(self.Deriv)
        self.DerivVar.setMinimumSize(QtCore.QSize(0, 25))
        self.DerivVar.setMaximumSize(QtCore.QSize(16777215, 25))
        self.DerivVar.setObjectName("DerivVar")
        self.DerivVar.setValidator(lowerVal)
        self.DerivVar.setMaxLength(1)
        self.DerivVar.setText("x")
        self.gridLayout_2.addWidget(self.DerivVar, 5, 1, 1, 1)
        self.DerivPoint = QtWidgets.QLineEdit(self.Deriv)
        self.DerivPoint.setMinimumSize(QtCore.QSize(0, 25))
        self.DerivPoint.setMaximumSize(QtCore.QSize(16777215, 25))
        self.DerivPoint.setPlaceholderText("")
        self.DerivPoint.setObjectName("DerivPoint")
        self.gridLayout_2.addWidget(self.DerivPoint, 4, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.Deriv)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 5, 0, 1, 1)
        self.DerivOut = QtWidgets.QTextBrowser(self.Deriv)
        self.DerivOut.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.DerivOut.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.DerivOut.setObjectName("DerivOut")
        self.gridLayout_2.addWidget(self.DerivOut, 0, 3, 8, 1)
        self.DerivApprox = QtWidgets.QLineEdit(self.Deriv)
        self.DerivApprox.setReadOnly(True)
        self.DerivApprox.setMinimumSize(QtCore.QSize(0, 25))
        self.DerivApprox.setMaximumSize(QtCore.QSize(16777215, 25))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.DerivApprox.setFont(font)
        self.DerivApprox.setObjectName("DerivApprox")
        self.gridLayout_2.addWidget(self.DerivApprox, 8, 3, 1, 1)
        self.tabWidget.addTab(self.Deriv, "")

        self.Integ = QtWidgets.QWidget()
        self.Integ.setObjectName("Integ")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.Integ)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.IntegExp = QtWidgets.QTextEdit(self.Integ)
        self.IntegExp.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.IntegExp.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.IntegExp.setObjectName("IntegExp")
        self.gridLayout_3.addWidget(self.IntegExp, 0, 0, 1, 2)
        self.IntegOut = QtWidgets.QTextBrowser(self.Integ)
        self.IntegOut.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.IntegOut.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.IntegOut.setObjectName("IntegOut")
        self.gridLayout_3.addWidget(self.IntegOut, 0, 2, 6, 1)
        self.label_2 = QtWidgets.QLabel(self.Integ)
        self.label_2.setMaximumSize(QtCore.QSize(40, 16777215))
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 1, 0, 1, 1)
        self.IntegLower = QtWidgets.QLineEdit(self.Integ)
        self.IntegLower.setMinimumSize(QtCore.QSize(0, 25))
        self.IntegLower.setMaximumSize(QtCore.QSize(16777215, 25))
        self.IntegLower.setPlaceholderText("")
        self.IntegLower.setObjectName("IntegLower")
        self.gridLayout_3.addWidget(self.IntegLower, 1, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.Integ)
        self.label_5.setObjectName("label_5")
        self.gridLayout_3.addWidget(self.label_5, 2, 0, 1, 1)
        self.IntegUpper = QtWidgets.QLineEdit(self.Integ)
        self.IntegUpper.setMinimumSize(QtCore.QSize(0, 25))
        self.IntegUpper.setMaximumSize(QtCore.QSize(16777215, 25))
        self.IntegUpper.setObjectName("IntegUpper")
        self.gridLayout_3.addWidget(self.IntegUpper, 2, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.Integ)
        self.label_4.setObjectName("label_4")
        self.gridLayout_3.addWidget(self.label_4, 3, 0, 1, 1)
        self.IntegVar = QtWidgets.QLineEdit(self.Integ)
        self.IntegVar.setMinimumSize(QtCore.QSize(0, 25))
        self.IntegVar.setMaximumSize(QtCore.QSize(16777215, 25))
        self.IntegVar.setObjectName("IntegVar")
        self.IntegVar.setValidator(lowerVal)
        self.IntegVar.setMaxLength(1)
        self.IntegVar.setText("x")
        self.gridLayout_3.addWidget(self.IntegVar, 3, 1, 1, 1)
        self.IntegPrev = QtWidgets.QPushButton(self.Integ)
        self.IntegPrev.setObjectName("IntegPrev")
        self.IntegPrev.clicked.connect(self.prevInteg)
        self.gridLayout_3.addWidget(self.IntegPrev, 4, 0, 1, 2)
        self.IntegCalc = QtWidgets.QPushButton(self.Integ)
        self.IntegCalc.setObjectName("IntegCalc")
        self.IntegCalc.clicked.connect(self.calcInteg)
        self.gridLayout_3.addWidget(self.IntegCalc, 5, 0, 1, 2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.IntegOutType = QtWidgets.QLabel(self.Integ)
        self.IntegOutType.setObjectName("IntegOutType")
        self.horizontalLayout_2.addWidget(self.IntegOutType)
        self.IntegPP = QtWidgets.QRadioButton(self.Integ)
        self.IntegPP.setChecked(True)
        self.IntegPP.setObjectName("IntegPP")
        self.horizontalLayout_2.addWidget(self.IntegPP)
        self.IntegLatex = QtWidgets.QRadioButton(self.Integ)
        self.IntegLatex.setObjectName("IntegLatex")
        self.horizontalLayout_2.addWidget(self.IntegLatex)
        self.IntegNormal = QtWidgets.QRadioButton(self.Integ)
        self.IntegNormal.setObjectName("IntegNormal")
        self.horizontalLayout_2.addWidget(self.IntegNormal)
        self.gridLayout_3.addLayout(self.horizontalLayout_2, 6, 0, 1, 2)
        self.IntegApprox = QtWidgets.QLineEdit(self.Integ)
        self.IntegApprox.setReadOnly(True)
        self.IntegApprox.setMinimumSize(QtCore.QSize(0, 25))
        self.IntegApprox.setMaximumSize(QtCore.QSize(16777215, 25))
        self.IntegApprox.setObjectName("IntegApprox")
        self.gridLayout_3.addWidget(self.IntegApprox, 6, 2, 1, 1)
        self.tabWidget.addTab(self.Integ, "")

        self.Lim = QtWidgets.QWidget()
        self.Lim.setObjectName("Lim")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.Lim)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.LimExp = QtWidgets.QTextEdit(self.Lim)
        self.LimExp.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.LimExp.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.LimExp.setObjectName("LimExp")
        self.gridLayout_4.addWidget(self.LimExp, 0, 0, 1, 2)
        self.LimOut = QtWidgets.QTextBrowser(self.Lim)
        self.LimOut.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.LimOut.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.LimOut.setObjectName("LimOut")
        self.gridLayout_4.addWidget(self.LimOut, 0, 2, 6, 1)
        self.label_6 = QtWidgets.QLabel(self.Lim)
        self.label_6.setMaximumSize(QtCore.QSize(40, 16777215))
        self.label_6.setObjectName("label_6")
        self.gridLayout_4.addWidget(self.label_6, 1, 0, 1, 1)
        self.LimSide = QtWidgets.QComboBox(self.Lim)
        self.LimSide.setMinimumSize(QtCore.QSize(0, 25))
        self.LimSide.setMaximumSize(QtCore.QSize(16777215, 25))
        self.LimSide.setEditable(False)
        self.LimSide.setObjectName("LimSide")
        self.LimSide.addItem("")
        self.LimSide.addItem("")
        self.LimSide.addItem("")
        self.gridLayout_4.addWidget(self.LimSide, 1, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.Lim)
        self.label_7.setObjectName("label_7")
        self.gridLayout_4.addWidget(self.label_7, 2, 0, 1, 1)
        self.LimVar = QtWidgets.QLineEdit(self.Lim)
        self.LimVar.setMinimumSize(QtCore.QSize(0, 25))
        self.LimVar.setMaximumSize(QtCore.QSize(16777215, 25))
        self.LimVar.setObjectName("LimVar")
        self.LimVar.setText("x")
        self.LimVar.setValidator(lowerVal)
        self.LimVar.setMaxLength(1)
        self.gridLayout_4.addWidget(self.LimVar, 2, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.Lim)
        self.label_8.setObjectName("label_8")
        self.gridLayout_4.addWidget(self.label_8, 3, 0, 1, 1)
        self.LimApproach = QtWidgets.QLineEdit(self.Lim)
        self.LimApproach.setMinimumSize(QtCore.QSize(0, 25))
        self.LimApproach.setMaximumSize(QtCore.QSize(16777215, 25))
        self.LimApproach.setObjectName("LimApproach")
        self.gridLayout_4.addWidget(self.LimApproach, 3, 1, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.LimOutType = QtWidgets.QLabel(self.Lim)
        self.LimOutType.setObjectName("LimOutType")
        self.horizontalLayout_3.addWidget(self.LimOutType)
        self.LimPP = QtWidgets.QRadioButton(self.Lim)
        self.LimPP.setChecked(True)
        self.LimPP.setObjectName("LimPP")
        self.horizontalLayout_3.addWidget(self.LimPP)
        self.LimLatex = QtWidgets.QRadioButton(self.Lim)
        self.LimLatex.setObjectName("LimLatex")
        self.horizontalLayout_3.addWidget(self.LimLatex)
        self.LimNormal = QtWidgets.QRadioButton(self.Lim)
        self.LimNormal.setObjectName("LimNormal")
        self.horizontalLayout_3.addWidget(self.LimNormal)
        self.gridLayout_4.addLayout(self.horizontalLayout_3, 6, 0, 1, 2)
        self.LimApprox = QtWidgets.QLineEdit(self.Lim)
        self.LimApprox.setReadOnly(True)
        self.LimApprox.setMinimumSize(QtCore.QSize(0, 25))
        self.LimApprox.setMaximumSize(QtCore.QSize(16777215, 25))
        self.LimApprox.setObjectName("LimApprox")
        self.gridLayout_4.addWidget(self.LimApprox, 6, 2, 1, 1)
        self.LimPrev = QtWidgets.QPushButton(self.Lim)
        self.LimPrev.setObjectName("LimPrev")
        self.LimPrev.clicked.connect(self.prevLimit)
        self.gridLayout_4.addWidget(self.LimPrev, 4, 0, 1, 2)
        self.LimCalc = QtWidgets.QPushButton(self.Lim)
        self.LimCalc.setObjectName("LimCalc")
        self.LimCalc.clicked.connect(self.calcLimit)
        self.gridLayout_4.addWidget(self.LimCalc, 5, 0, 1, 2)
        self.tabWidget.addTab(self.Lim, "")

        self.Eq = QtWidgets.QWidget()
        self.Eq.setObjectName("Eq")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.Eq)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.EqOutType = QtWidgets.QLabel(self.Eq)
        self.EqOutType.setObjectName("EqOutType")
        self.horizontalLayout_4.addWidget(self.EqOutType)
        self.EqPP = QtWidgets.QRadioButton(self.Eq)
        self.EqPP.setChecked(True)
        self.EqPP.setObjectName("EqPP")
        self.OutTypeGroup = QtWidgets.QButtonGroup(MainWindow)
        self.OutTypeGroup.setObjectName("OutTypeGroup")
        self.OutTypeGroup.addButton(self.EqPP)
        self.horizontalLayout_4.addWidget(self.EqPP)
        self.EqLatex = QtWidgets.QRadioButton(self.Eq)
        self.EqLatex.setObjectName("EqLatex")
        self.OutTypeGroup.addButton(self.EqLatex)
        self.horizontalLayout_4.addWidget(self.EqLatex)
        self.EqNormal = QtWidgets.QRadioButton(self.Eq)
        self.EqNormal.setObjectName("EqNormal")
        self.OutTypeGroup.addButton(self.EqNormal)
        self.horizontalLayout_4.addWidget(self.EqNormal)
        self.gridLayout_5.addLayout(self.horizontalLayout_4, 6, 0, 1, 2)
        self.EqApprox = QtWidgets.QTextBrowser(self.Eq)
        self.EqApprox.setMinimumSize(QtCore.QSize(0, 25))
        self.EqApprox.setMaximumSize(QtCore.QSize(16777215, 25))
        self.EqApprox.setObjectName("EqApprox")
        self.gridLayout_5.addWidget(self.EqApprox, 6, 2, 1, 1)
        self.EqLeft = QtWidgets.QTextEdit(self.Eq)
        self.EqLeft.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.EqLeft.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.EqLeft.setObjectName("EqLeft")
        self.gridLayout_5.addWidget(self.EqLeft, 0, 0, 1, 2)
        self.EqCalc = QtWidgets.QPushButton(self.Eq)
        self.EqCalc.setObjectName("EqCalc")
        self.EqCalc.clicked.connect(self.calcEq)
        self.gridLayout_5.addWidget(self.EqCalc, 5, 0, 1, 2)
        self.EqRight = QtWidgets.QTextEdit(self.Eq)
        self.EqRight.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.EqRight.setObjectName("EqRight")
        self.gridLayout_5.addWidget(self.EqRight, 1, 0, 1, 2)
        self.EqPrev = QtWidgets.QPushButton(self.Eq)
        self.EqPrev.setObjectName("EqPrev")
        self.EqPrev.clicked.connect(self.prevEq)
        self.gridLayout_5.addWidget(self.EqPrev, 4, 0, 1, 2)
        self.EqOut = QtWidgets.QTextBrowser(self.Eq)
        self.EqOut.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.EqOut.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.EqOut.setObjectName("EqOut")
        self.gridLayout_5.addWidget(self.EqOut, 0, 2, 6, 1)
        self.horizontalLayoutEq = QtWidgets.QHBoxLayout()
        self.horizontalLayoutEq.setObjectName("horizontalLayoutEq")
        self.EqSolve = QtWidgets.QRadioButton(self.Eq)
        self.EqSolve.setChecked(True)
        self.EqSolve.setObjectName("EqSolve")
        self.horizontalLayoutEq.addWidget(self.EqSolve)
        self.EqSolveSet = QtWidgets.QRadioButton(self.Eq)
        self.EqSolveSet.setObjectName("EqSolveSet")
        self.horizontalLayoutEq.addWidget(self.EqSolveSet)
        self.gridLayout_5.addLayout(self.horizontalLayoutEq, 3, 0, 1, 1)
        self.EqVar = QtWidgets.QLineEdit(self.Eq)
        self.EqVar.setObjectName("EqVar")
        self.EqVar.setText("x")
        self.EqVar.setValidator(textVal)
        self.gridLayout_5.addWidget(self.EqVar, 2, 0, 1, 1)
        self.tabWidget.addTab(self.Eq, "")

        self.Simp = QtWidgets.QWidget()
        self.Simp.setObjectName("Simp")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.Simp)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.SimpOutType = QtWidgets.QLabel(self.Simp)
        self.SimpOutType.setMinimumSize(QtCore.QSize(0, 25))
        self.SimpOutType.setMaximumSize(QtCore.QSize(16777215, 25))
        self.SimpOutType.setObjectName("SimpOutType")
        self.horizontalLayout_5.addWidget(self.SimpOutType)
        self.SimpPP = QtWidgets.QRadioButton(self.Simp)
        self.SimpPP.setChecked(True)
        self.SimpPP.setObjectName("SimpPP")
        self.horizontalLayout_5.addWidget(self.SimpPP)
        self.SimpLatex = QtWidgets.QRadioButton(self.Simp)
        self.SimpLatex.setObjectName("SimpLatex")
        self.horizontalLayout_5.addWidget(self.SimpLatex)
        self.SimpNormal = QtWidgets.QRadioButton(self.Simp)
        self.SimpNormal.setObjectName("SimpNormal")
        self.horizontalLayout_5.addWidget(self.SimpNormal)
        self.gridLayout_6.addLayout(self.horizontalLayout_5, 3, 0, 1, 1)
        self.SimpCalc = QtWidgets.QPushButton(self.Simp)
        self.SimpCalc.setObjectName("SimpCalc")
        self.SimpCalc.clicked.connect(self.simpEq)
        self.gridLayout_6.addWidget(self.SimpCalc, 2, 0, 1, 1)
        self.SimpExp = QtWidgets.QTextEdit(self.Simp)
        self.SimpExp.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.SimpExp.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.SimpExp.setObjectName("SimpExp")
        self.gridLayout_6.addWidget(self.SimpExp, 0, 0, 1, 1)
        self.SimpPrev = QtWidgets.QPushButton(self.Simp)
        self.SimpPrev.setObjectName("SimpPrev")
        self.SimpPrev.clicked.connect(self.prevSimpEq)
        self.gridLayout_6.addWidget(self.SimpPrev, 1, 0, 1, 1)
        self.SimpOut = QtWidgets.QTextBrowser(self.Simp)
        self.SimpOut.setEnabled(True)
        self.SimpOut.setMinimumSize(QtCore.QSize(0, 0))
        self.SimpOut.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.SimpOut.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.SimpOut.setObjectName("SimpOut")
        self.gridLayout_6.addWidget(self.SimpOut, 0, 1, 4, 1)
        self.tabWidget.addTab(self.Simp, "")

        self.Exp = QtWidgets.QWidget()
        self.Exp.setObjectName("Exp")
        self.gridLayout_13 = QtWidgets.QGridLayout(self.Exp)
        self.gridLayout_13.setObjectName("gridLayout_13")
        self.ExpExp = QtWidgets.QTextEdit(self.Exp)
        self.ExpExp.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.ExpExp.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.ExpExp.setObjectName("ExpExp")
        self.gridLayout_13.addWidget(self.ExpExp, 0, 0, 1, 1)
        self.ExpOut = QtWidgets.QTextBrowser(self.Exp)
        self.ExpOut.setEnabled(True)
        self.ExpOut.setMinimumSize(QtCore.QSize(0, 0))
        self.ExpOut.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.ExpOut.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.ExpOut.setObjectName("ExpOut")
        self.gridLayout_13.addWidget(self.ExpOut, 0, 1, 4, 1)
        self.ExpPrev = QtWidgets.QPushButton(self.Exp)
        self.ExpPrev.setObjectName("ExpPrev")
        self.ExpPrev.clicked.connect(self.prevExpEq)
        self.gridLayout_13.addWidget(self.ExpPrev, 1, 0, 1, 1)
        self.ExpCalc = QtWidgets.QPushButton(self.Exp)
        self.ExpCalc.setObjectName("ExpCalc")
        self.ExpCalc.clicked.connect(self.expEq)
        self.gridLayout_13.addWidget(self.ExpCalc, 2, 0, 1, 1)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.ExpOutType = QtWidgets.QLabel(self.Exp)
        self.ExpOutType.setMinimumSize(QtCore.QSize(0, 25))
        self.ExpOutType.setMaximumSize(QtCore.QSize(16777215, 25))
        self.ExpOutType.setObjectName("ExpOutType")
        self.horizontalLayout_11.addWidget(self.ExpOutType)
        self.ExpPP = QtWidgets.QRadioButton(self.Exp)
        self.ExpPP.setChecked(True)
        self.ExpPP.setObjectName("ExpPP")
        self.horizontalLayout_11.addWidget(self.ExpPP)
        self.ExpLatex = QtWidgets.QRadioButton(self.Exp)
        self.ExpLatex.setObjectName("ExpLatex")
        self.horizontalLayout_11.addWidget(self.ExpLatex)
        self.ExpNormal = QtWidgets.QRadioButton(self.Exp)
        self.ExpNormal.setObjectName("ExpNormal")
        self.horizontalLayout_11.addWidget(self.ExpNormal)
        self.gridLayout_13.addLayout(self.horizontalLayout_11, 3, 0, 1, 1)
        self.tabWidget.addTab(self.Exp, "")

        self.Eval = QtWidgets.QWidget()
        self.Eval.setObjectName("Eval")
        self.gridLayout_14 = QtWidgets.QGridLayout(self.Eval)
        self.gridLayout_14.setObjectName("gridLayout_14")
        self.EvalExp = QtWidgets.QTextEdit(self.Eval)
        self.EvalExp.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.EvalExp.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.EvalExp.setObjectName("EvalExp")
        self.gridLayout_14.addWidget(self.EvalExp, 0, 0, 1, 1)
        self.EvalOut = QtWidgets.QTextBrowser(self.Eval)
        self.EvalOut.setEnabled(True)
        self.EvalOut.setMinimumSize(QtCore.QSize(0, 0))
        self.EvalOut.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.EvalOut.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.EvalOut.setObjectName("EvalOut")
        self.gridLayout_14.addWidget(self.EvalOut, 0, 1, 4, 1)
        self.EvalPrev = QtWidgets.QPushButton(self.Eval)
        self.EvalPrev.setObjectName("EvalPrev")
        self.EvalPrev.clicked.connect(self.prevEvalEq)
        self.gridLayout_14.addWidget(self.EvalPrev, 1, 0, 1, 1)
        self.EvalCalc = QtWidgets.QPushButton(self.Eval)
        self.EvalCalc.setObjectName("EvalCalc")
        self.EvalCalc.clicked.connect(self.evalExp)
        self.gridLayout_14.addWidget(self.EvalCalc, 2, 0, 1, 1)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.EvalOutType = QtWidgets.QLabel(self.Eval)
        self.EvalOutType.setObjectName("EvalOutType")
        self.horizontalLayout_13.addWidget(self.EvalOutType)
        self.EvalPP = QtWidgets.QRadioButton(self.Eval)
        self.EvalPP.setChecked(True)
        self.EvalPP.setObjectName("EvalPP")
        self.horizontalLayout_13.addWidget(self.EvalPP)
        self.EvalLatex = QtWidgets.QRadioButton(self.Eval)
        self.EvalLatex.setObjectName("EvalLatex")
        self.horizontalLayout_13.addWidget(self.EvalLatex)
        self.EvalNormal = QtWidgets.QRadioButton(self.Eval)
        self.EvalNormal.setObjectName("EvalNormal")
        self.horizontalLayout_13.addWidget(self.EvalNormal)
        self.gridLayout_14.addLayout(self.horizontalLayout_13, 4, 0, 1, 1)
        self.EvalApprox = QtWidgets.QTextBrowser(self.Eval)
        self.EvalApprox.setMinimumSize(QtCore.QSize(0, 25))
        self.EvalApprox.setMaximumSize(QtCore.QSize(16777215, 25))
        self.EvalApprox.setObjectName("EvalApprox")
        self.gridLayout_14.addWidget(self.EvalApprox, 4, 1, 1, 1)
        self.tabWidget.addTab(self.Eval, "")

        self.Pf = QtWidgets.QWidget()
        self.Pf.setObjectName("Pf")
        self.gridLayout_15 = QtWidgets.QGridLayout(self.Pf)
        self.gridLayout_15.setObjectName("gridLayout_15")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.label_32 = QtWidgets.QLabel(self.Pf)
        self.label_32.setMinimumSize(QtCore.QSize(40, 0))
        self.label_32.setMaximumSize(QtCore.QSize(40, 16777215))
        self.label_32.setObjectName("label_32")
        self.horizontalLayout_14.addWidget(self.label_32)
        self.PfInput = QtWidgets.QSpinBox(self.Pf)
        self.PfInput.setMinimum(1)
        self.PfInput.setMaximum(999999999)
        self.PfInput.setObjectName("PfInput")
        self.horizontalLayout_14.addWidget(self.PfInput)
        self.verticalLayout.addLayout(self.horizontalLayout_14)
        self.PfCalc = QtWidgets.QPushButton(self.Pf)
        self.PfCalc.setObjectName("PfCalc")
        self.PfCalc.clicked.connect(self.calcPf)
        self.verticalLayout.addWidget(self.PfCalc)
        self.PfOut = QtWidgets.QTextBrowser(self.Pf)
        self.PfOut.setPlaceholderText("")
        self.PfOut.setObjectName("PfOut")
        self.verticalLayout.addWidget(self.PfOut)
        self.gridLayout_15.addLayout(self.verticalLayout, 1, 0, 1, 1)
        self.tabWidget.addTab(self.Pf, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.Web = QtWidgets.QWidget()
        self.Web.setObjectName("Web")
        self.gridWeb = QtWidgets.QGridLayout(self.Web)
        self.gridWeb.setObjectName("gridWeb")
        self.web = QWebEngineView()
        desmos_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "desmos.html"))
        self.web.load(QUrl.fromLocalFile(desmos_path))
        self.gridWeb.addWidget(self.web, 0, 0, 1, 1)
        self.tabWidget.addTab(self.Web, "")

        self.Formula = QtWidgets.QWidget()
        self.Formula.setObjectName("Formula")
        self.FormulaGrid = QGridLayout(self.Formula)
        self.FormulaGrid.setObjectName("FormulaGrid")
        self.FormulaOutputLayout = QVBoxLayout()
        self.FormulaOutputLayout.setObjectName("FormulaOutputLayout")
        self.FormulaSolveGroup = QButtonGroup(MainWindow)
        self.FormulaSolveGroup.setObjectName("FormulaSolveGroup")
        self.FormulaSolveLayout = QHBoxLayout()
        self.FormulaSolveLayout.setObjectName("FormulaSolveLayout")
        self.FormulaSolveSolve = QRadioButton(self.Formula)
        self.FormulaSolveSolve.setObjectName("FormulaSolveSolve")
        self.FormulaSolveSolve.setChecked(True)
        self.FormulaSolveGroup.addButton(self.FormulaSolveSolve)
        self.FormulaSolveLayout.addWidget(self.FormulaSolveSolve)
        self.FormulaSolveSolveSet = QRadioButton(self.Formula)
        self.FormulaSolveSolveSet.setObjectName("FormulaSolveSolveSet")
        self.FormulaSolveGroup.addButton(self.FormulaSolveSolveSet)
        self.FormulaSolveLayout.addWidget(self.FormulaSolveSolveSet)
        self.FormulaOutputLayout.addLayout(self.FormulaSolveLayout)
        self.FormulaPreview = QPushButton(self.Formula)
        self.FormulaPreview.setObjectName("FormulaPreview")
        self.FormulaPreview.clicked.connect(self.prevFormula)
        self.FormulaOutputLayout.addWidget(self.FormulaPreview)
        self.FormulaCalculate = QPushButton(self.Formula)
        self.FormulaCalculate.setObjectName("FormulaCalculate")
        self.FormulaCalculate.clicked.connect(self.calcFormula)
        self.FormulaOutputLayout.addWidget(self.FormulaCalculate)
        self.FormulaOutTypeLayout = QHBoxLayout()
        self.FormulaOutTypeLayout.setObjectName("FormulaOutTypeLayout")
        self.FormulaOutTypeLabel = QLabel(self.Formula)
        self.FormulaOutTypeLabel.setObjectName("FormulaOutTypeLabel")
        self.FormulaOutTypeLayout.addWidget(self.FormulaOutTypeLabel)
        self.FormulaPP = QRadioButton(self.Formula)
        self.FormulaPP.setChecked(True)
        self.FormulaPP.setObjectName("FormulaPP")
        self.FormulaOutTypeLayout.addWidget(self.FormulaPP)
        self.FormulaLatex = QRadioButton(self.Formula)
        self.FormulaLatex.setObjectName("FormulaLatex")
        self.FormulaOutTypeLayout.addWidget(self.FormulaLatex)
        self.FormulaNormal = QRadioButton(self.Formula)
        self.FormulaNormal.setObjectName("FormulaNormal")
        self.FormulaOutTypeLayout.addWidget(self.FormulaNormal)
        self.FormulaOutputLayout.addLayout(self.FormulaOutTypeLayout)
        self.FormulaExact = QTextBrowser(self.Formula)
        self.FormulaExact.setObjectName("FomulaExact")
        self.FormulaOutputLayout.addWidget(self.FormulaExact)
        self.FormulaApprox = QLineEdit(self.Formula)
        self.FormulaApprox.setReadOnly(True)
        self.FormulaApprox.setObjectName("FomulaApprox")
        self.FormulaOutputLayout.addWidget(self.FormulaApprox)
        self.FormulaGrid.addLayout(self.FormulaOutputLayout, 0, 1, 1, 1)
        self.FormulaViewerLayout = QVBoxLayout()
        self.FormulaViewerLayout.setObjectName("FormulaViewerLayout")
        self.FormulaTree = QTreeWidget(self.Formula)
        self.FormulaTree.setObjectName("FormulaTree")
        self.FormulaTree.itemDoubleClicked.connect(self.FormulaTreeSelected)
        with open("formulas.json", encoding='utf-8') as f:
            self.FormulaTreeData = json.loads(f.read())
        self.FormulaTreeData = self.FormulaTreeData[0]
        for branch in self.FormulaTreeData:
            parent = QTreeWidgetItem(self.FormulaTree)
            parent.setText(0, str(branch[0]))
            for subBranch in branch[1]:
                child = QTreeWidgetItem(parent)
                child.setText(0, str(subBranch[0]))
                for formula in subBranch[1]:
                    formulaChild = QTreeWidgetItem(child)
                    formulaChild.setText(0, formula[0])
        self.FormulaViewerLayout.addWidget(self.FormulaTree)
        self.FormulaLine = QFrame(self.Formula)
        self.FormulaLine.setFrameShape(QFrame.HLine)
        self.FormulaLine.setFrameShadow(QFrame.Sunken)
        self.FormulaLine.setObjectName("FormulaLine")
        self.FormulaViewerLayout.addWidget(self.FormulaLine)
        self.FormulaScroll = QScrollArea(self.Formula)
        self.FormulaScroll.setEnabled(True)
        self.FormulaScroll.setWidgetResizable(True)
        self.FormulaScroll.setObjectName("FormulaScroll")
        self.FormulaScrollArea = QWidget()
        self.FormulaScrollArea.setGeometry(QRect(0, 0, 372, 364))
        self.FormulaScrollArea.setObjectName("FormulaScrollArea")
        self.FormulaGrid2 = QGridLayout(self.FormulaScrollArea)
        self.FormulaGrid2.setObjectName("FormulaGrid2")
        self.FormulaScroll.setWidget(self.FormulaScrollArea)
        self.FormulaViewerLayout.addWidget(self.FormulaScroll)
        self.FormulaGrid.addLayout(self.FormulaViewerLayout, 0, 0, 1, 1)
        self.tabWidget.addTab(self.Formula, "")

        self.Shell = QtWidgets.QWidget()
        self.Shell.setObjectName("Shell")
        self.currentCode = "This is a very simple shell using 'exec' commands, so it has some limitations.\n" \
                           "Every variable declared and function defined will be saved until the program is closed" \
                           " or when the 'clear commands' button in the menubar is pressed.\n" \
                           "It will automatically output to the shell, but it can't use 'print' commands. To copy" \
                           " output, press the 'copy exact answer' in the menubar\nTheses commands were executed:\n" \
                           "from __future__ import division\n" \
                           "from sympy import *\n" \
                           "from sympy.parsing.sympy_parser import parse_expr\n" \
                           "from sympy.abc import _clash1\nx, y, z, t = symbols('x y z t')\n" \
                           "k, m, n = symbols('k m n', integer=True)\nf, g, h = symbols('f g h', cls=Function)\n\n>>> "
        self.toExecute = ""
        self.alreadyExecuted = []
        self.ShellGrid = QGridLayout(self.Shell)
        self.ShellGrid.setObjectName("ShellGrid")
        self.consoleIn = QPlainTextEdit(self.centralwidget)
        self.consoleIn.setObjectName("consoleIn")
        self.consoleIn.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.consoleIn.insertPlainText(self.currentCode)
        self.consoleIn.setTabStopWidth(40)
        self.consoleIn.setTabStopDistance(40.0)
        self.ShellGrid.addWidget(self.consoleIn, 0, 0, 1, 1)
        self.ShellRun = QPushButton(self.centralwidget)
        self.ShellRun.setObjectName("ShellRun")
        self.ShellRun.clicked.connect(self.executeCode)
        self.ShellGrid.addWidget(self.ShellRun, 1, 0, 1, 1)
        self.tabWidget.addTab(self.Shell, "")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 678, 21))
        self.menubar.setObjectName("menubar")
        self.menuCopy = QtWidgets.QMenu(self.menubar)
        self.menuCopy.setObjectName("menuCopy")
        self.menuTab = QtWidgets.QMenu(self.menubar)
        self.menuTab.setObjectName("menuTab")
        self.menuSettings = QtWidgets.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        self.menuWeb = QtWidgets.QMenu(self.menubar)
        self.menuWeb.setObjectName("menuWeb")
        with open("formulas.json", encoding='utf-8') as f:
            self.WebList = json.loads(f.read())
        self.WebList = self.WebList[1]
        webGroup = QActionGroup(self.menuWeb)
        for i in self.WebList:
            for key in i:
                webAction = QAction(key, self.menuWeb, checkable=True)
                if webAction.text() == "Desmos":
                    webAction.setChecked(True)
                self.menuWeb.addAction(webAction)
                webGroup.addAction(webAction)
        webGroup.setExclusive(True)
        webGroup.triggered.connect(self.updateWeb)
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionCopy_exact_answer = QtWidgets.QAction(MainWindow)
        self.actionCopy_exact_answer.setObjectName("actionCopy_exact_answer")
        self.actionCopy_approximate_answer = QtWidgets.QAction(MainWindow)
        self.actionCopy_approximate_answer.setObjectName("actionCopy_approximate_answer")
        self.actionNext_Tab = QtWidgets.QAction(MainWindow)
        self.actionNext_Tab.setObjectName("actionNext_Tab")
        self.actionPrevious_Tab = QtWidgets.QAction(MainWindow)
        self.actionPrevious_Tab.setObjectName("actionPrevious_Tab")
        self.actionUse_Unicode = QtWidgets.QAction(MainWindow)
        self.actionUse_Unicode.setCheckable(True)
        self.actionUse_Unicode.setObjectName("actionUse_Unicode")
        self.actionLine_Wrap = QtWidgets.QAction(MainWindow)
        self.actionLine_Wrap.setCheckable(True)
        self.actionLine_Wrap.setObjectName("actionLine-Wrap")
        self.menuSettings.addAction(self.actionUse_Unicode)
        self.menuSettings.addAction(self.actionLine_Wrap)
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menuCopy.addAction(self.actionCopy_exact_answer)
        self.menuCopy.addAction(self.actionCopy_approximate_answer)
        self.menuTab.addAction(self.actionNext_Tab)
        self.menuTab.addAction(self.actionPrevious_Tab)
        self.menubar.addAction(self.menuCopy.menuAction())
        self.menubar.addAction(self.menuTab.menuAction())
        self.menubar.addAction(self.menuWeb.menuAction())
        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Calculus"))
        self.tabWidget.setToolTip(_translate("MainWindow", "Tabs"))
        self.tabWidget.setStatusTip(_translate("MainWindow", "Tabs for actions"))
        self.tabWidget.setWhatsThis(_translate("MainWindow", "Tabs for actions"))
        self.Deriv.setToolTip(_translate("MainWindow", "<html><head/><body><p><br/></p></body></html>"))
        self.DerivPrev.setToolTip(_translate("MainWindow", "Preview"))
        self.DerivPrev.setStatusTip(_translate("MainWindow", "Preview the expression"))
        self.DerivPrev.setWhatsThis(_translate("MainWindow", "Preview"))
        self.DerivPrev.setText(_translate("MainWindow", "Preview"))
        self.DerivCalc.setToolTip(_translate("MainWindow", "Calculate"))
        self.DerivCalc.setStatusTip(_translate("MainWindow", "Calculate the derivative"))
        self.DerivCalc.setWhatsThis(_translate("MainWindow", "Calculate"))
        self.DerivCalc.setText(_translate("MainWindow", "Calculate"))
        self.label_9.setText(_translate("MainWindow", "At point"))
        self.DerivExp.setToolTip(_translate("MainWindow", "Your expression"))
        self.DerivExp.setStatusTip(_translate("MainWindow", "Type in your expression here"))
        self.DerivExp.setWhatsThis(_translate("MainWindow", "Input expression"))
        self.DerivExp.setPlaceholderText(_translate("MainWindow", "Expression"))
        self.label.setText(_translate("MainWindow", "Order"))
        self.DerivOutType.setText(_translate("MainWindow", "Output type"))
        self.DerivPP.setToolTip(_translate("MainWindow", "Pretty print"))
        self.DerivPP.setStatusTip(_translate("MainWindow", "Pretty print"))
        self.DerivPP.setWhatsThis(_translate("MainWindow", "Pretty print"))
        self.DerivPP.setText(_translate("MainWindow", "Pretty"))
        self.DerivLatex.setToolTip(_translate("MainWindow", "Latex"))
        self.DerivLatex.setStatusTip(_translate("MainWindow", "Latex"))
        self.DerivLatex.setWhatsThis(_translate("MainWindow", "Latex"))
        self.DerivLatex.setText(_translate("MainWindow", "Latex"))
        self.DerivNormal.setToolTip(_translate("MainWindow", "Normal"))
        self.DerivNormal.setStatusTip(_translate("MainWindow", "Normal"))
        self.DerivNormal.setWhatsThis(_translate("MainWindow", "Normal"))
        self.DerivNormal.setText(_translate("MainWindow", "Normal"))
        self.DerivOrder.setToolTip(_translate("MainWindow", "The order of the derivative"))
        self.DerivOrder.setStatusTip(_translate("MainWindow", "The order of the derivative, default is 1, max is 999"))
        self.DerivOrder.setWhatsThis(_translate("MainWindow", "The order of the derivative"))
        self.DerivVar.setToolTip(_translate("MainWindow", "Variable"))
        self.DerivVar.setStatusTip(_translate("MainWindow", "Derivative with respect to variable"))
        self.DerivVar.setWhatsThis(_translate("MainWindow", "Variable"))
        self.DerivPoint.setToolTip(_translate("MainWindow", "Calculate the derivative at a point"))
        self.DerivPoint.setStatusTip(
            _translate("MainWindow", "Calculate the derivative at a point, leave blank for at point x"))
        self.DerivPoint.setWhatsThis(_translate("MainWindow", "Calculate the derivative at a point"))
        self.label_3.setText(_translate("MainWindow", "Variable"))
        self.DerivOut.setToolTip(_translate("MainWindow", "Output"))
        self.DerivOut.setStatusTip(_translate("MainWindow", "Output in exact form"))
        self.DerivOut.setWhatsThis(_translate("MainWindow", "Output in exact form"))
        self.DerivApprox.setToolTip(_translate("MainWindow", "Output"))
        self.DerivApprox.setStatusTip(_translate("MainWindow",
                                                 "Output in approximate form, will only show when the derivative is calculated at a certain point"))
        self.DerivApprox.setWhatsThis(_translate("MainWindow", "Output in approximate form"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Deriv), _translate("MainWindow", "Derivative"))
        self.IntegExp.setToolTip(_translate("MainWindow", "Your expression"))
        self.IntegExp.setStatusTip(_translate("MainWindow", "Type in your expression here"))
        self.IntegExp.setWhatsThis(_translate("MainWindow", "Input expression"))
        self.IntegExp.setPlaceholderText(_translate("MainWindow", "Expression"))
        self.IntegOut.setToolTip(_translate("MainWindow", "Output"))
        self.IntegOut.setStatusTip(_translate("MainWindow", "Output in exact form"))
        self.IntegOut.setWhatsThis(_translate("MainWindow", "Output in exact form"))
        self.label_2.setText(_translate("MainWindow", "From"))
        self.IntegLower.setToolTip(_translate("MainWindow", "Lower boundry"))
        self.IntegLower.setStatusTip(
            _translate("MainWindow", "Lower boundry, infinity is \"oo\", leave empty for indefinite integral"))
        self.IntegLower.setWhatsThis(_translate("MainWindow", "Lower boundry"))
        self.label_5.setText(_translate("MainWindow", "To"))
        self.IntegUpper.setToolTip(_translate("MainWindow", "Upper boundry"))
        self.IntegUpper.setStatusTip(
            _translate("MainWindow", "Upper boundry, infinity is \"oo\", leave empty for indefinite integral"))
        self.IntegUpper.setWhatsThis(_translate("MainWindow", "Upper boundry"))
        self.label_4.setText(_translate("MainWindow", "Variable"))
        self.IntegVar.setToolTip(_translate("MainWindow", "Variable"))
        self.IntegVar.setStatusTip(_translate("MainWindow", "Integral with respect to variable"))
        self.IntegVar.setWhatsThis(_translate("MainWindow", "Variable"))
        self.IntegPrev.setText(_translate("MainWindow", "Preview"))
        self.IntegCalc.setToolTip(_translate("MainWindow", "Calculate"))
        self.IntegCalc.setStatusTip(_translate("MainWindow", "Calculate the integral"))
        self.IntegCalc.setWhatsThis(_translate("MainWindow", "Calculate"))
        self.IntegCalc.setText(_translate("MainWindow", "Calculate"))
        self.IntegOutType.setText(_translate("MainWindow", "Output type"))
        self.IntegPP.setToolTip(_translate("MainWindow", "Pretty print"))
        self.IntegPP.setStatusTip(_translate("MainWindow", "Pretty print"))
        self.IntegPP.setWhatsThis(_translate("MainWindow", "Pretty print"))
        self.IntegPP.setText(_translate("MainWindow", "Pretty"))
        self.IntegLatex.setToolTip(_translate("MainWindow", "Latex"))
        self.IntegLatex.setStatusTip(_translate("MainWindow", "Latex"))
        self.IntegLatex.setWhatsThis(_translate("MainWindow", "Latex"))
        self.IntegLatex.setText(_translate("MainWindow", "Latex"))
        self.IntegNormal.setToolTip(_translate("MainWindow", "Normal"))
        self.IntegNormal.setStatusTip(_translate("MainWindow", "Normal"))
        self.IntegNormal.setWhatsThis(_translate("MainWindow", "Normal"))
        self.IntegNormal.setText(_translate("MainWindow", "Normal"))
        self.IntegApprox.setToolTip(_translate("MainWindow", "Output"))
        self.IntegApprox.setStatusTip(_translate("MainWindow",
                                                 "Output in approximate form, will only show when a definite integral is calculated"))
        self.IntegApprox.setWhatsThis(_translate("MainWindow", "Output in approximate form"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Integ), _translate("MainWindow", "Integral"))
        self.LimExp.setToolTip(_translate("MainWindow", "Your expression"))
        self.LimExp.setStatusTip(_translate("MainWindow", "Type in your expression here"))
        self.LimExp.setWhatsThis(_translate("MainWindow", "Input expression"))
        self.LimExp.setPlaceholderText(_translate("MainWindow", "Expression"))
        self.LimOut.setToolTip(_translate("MainWindow", "Output"))
        self.LimOut.setStatusTip(_translate("MainWindow", "Output in exact form"))
        self.LimOut.setWhatsThis(_translate("MainWindow", "Output in exact form"))
        self.label_6.setText(_translate("MainWindow", "Side"))
        self.LimSide.setItemText(0, _translate("MainWindow", "Both sides"))
        self.LimSide.setItemText(1, _translate("MainWindow", "Left"))
        self.LimSide.setItemText(2, _translate("MainWindow", "Right"))
        self.label_7.setText(_translate("MainWindow", "Variable"))
        self.LimVar.setToolTip(_translate("MainWindow", "Variable"))
        self.LimVar.setStatusTip(_translate("MainWindow", "Limit with respect to variable"))
        self.LimVar.setWhatsThis(_translate("MainWindow", "Variable"))
        self.label_8.setText(_translate("MainWindow", "As variable approaces"))
        self.LimOutType.setText(_translate("MainWindow", "Output type"))
        self.LimPP.setText(_translate("MainWindow", "Pretty"))
        self.LimLatex.setToolTip(_translate("MainWindow", "Latex"))
        self.LimLatex.setStatusTip(_translate("MainWindow", "Latex"))
        self.LimLatex.setWhatsThis(_translate("MainWindow", "Latex"))
        self.LimLatex.setText(_translate("MainWindow", "Latex"))
        self.LimNormal.setToolTip(_translate("MainWindow", "Normal"))
        self.LimNormal.setStatusTip(_translate("MainWindow", "Normal"))
        self.LimNormal.setWhatsThis(_translate("MainWindow", "Normal"))
        self.LimNormal.setText(_translate("MainWindow", "Normal"))
        self.LimApprox.setToolTip(_translate("MainWindow", "Output"))
        self.LimApprox.setStatusTip(_translate("MainWindow", "Output in approximate form"))
        self.LimApprox.setWhatsThis(_translate("MainWindow", "Output in approximate form"))
        self.LimPrev.setText(_translate("MainWindow", "Preview"))
        self.LimCalc.setToolTip(_translate("MainWindow", "Calculate"))
        self.LimCalc.setStatusTip(_translate("MainWindow", "Calculate the limit"))
        self.LimCalc.setWhatsThis(_translate("MainWindow", "Calculate"))
        self.LimCalc.setText(_translate("MainWindow", "Calculate"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Lim), _translate("MainWindow", "Limit"))
        self.EqOutType.setText(_translate("MainWindow", "Output type"))
        self.EqPP.setText(_translate("MainWindow", "Pretty"))
        self.EqSolve.setText(_translate("MainWindow", "Solve"))
        self.EqSolve.setToolTip(_translate("MainWindow", "Solve"))
        self.EqSolve.setStatusTip(_translate("MainWindow", "See Sympy Solve vs Solveset"))
        self.EqSolve.setWhatsThis(_translate("MainWindow", "See Sympy Solve vs Solveset"))
        self.EqSolveSet.setText(_translate("MainWindow", "Solveset"))
        self.EqSolveSet.setToolTip(_translate("MainWindow", "Solveset"))
        self.EqSolveSet.setStatusTip(_translate("MainWindow", "See Sympy Solve vs Solveset"))
        self.EqSolveSet.setWhatsThis(_translate("MainWindow", "See Sympy Solve vs Solveset"))
        self.EqLatex.setToolTip(_translate("MainWindow", "Latex"))
        self.EqLatex.setStatusTip(_translate("MainWindow", "Latex"))
        self.EqLatex.setWhatsThis(_translate("MainWindow", "Latex"))
        self.EqLatex.setText(_translate("MainWindow", "Latex"))
        self.EqNormal.setToolTip(_translate("MainWindow", "Normal"))
        self.EqNormal.setStatusTip(_translate("MainWindow", "Normal"))
        self.EqNormal.setWhatsThis(_translate("MainWindow", "Normal"))
        self.EqNormal.setText(_translate("MainWindow", "Normal"))
        self.EqApprox.setToolTip(_translate("MainWindow", "Output"))
        self.EqApprox.setStatusTip(_translate("MainWindow", "Output in approximate form"))
        self.EqApprox.setWhatsThis(_translate("MainWindow", "Output in approximate form"))
        self.EqLeft.setToolTip(_translate("MainWindow", "Left side "))
        self.EqLeft.setStatusTip(_translate("MainWindow", "Left side of your expression"))
        self.EqLeft.setWhatsThis(_translate("MainWindow", "Left side"))
        self.EqLeft.setPlaceholderText(_translate("MainWindow", "Left side"))
        self.EqCalc.setToolTip(_translate("MainWindow", "Calculate"))
        self.EqCalc.setStatusTip(_translate("MainWindow", "Calculate the equation"))
        self.EqCalc.setWhatsThis(_translate("MainWindow", "Calculate"))
        self.EqCalc.setText(_translate("MainWindow", "Calculate"))
        self.EqRight.setToolTip(_translate("MainWindow", "Right side"))
        self.EqRight.setStatusTip(_translate("MainWindow", "Right side of your expression"))
        self.EqRight.setWhatsThis(_translate("MainWindow", "Right side"))
        self.EqRight.setPlaceholderText(_translate("MainWindow", "Right side"))
        self.EqPrev.setText(_translate("MainWindow", "Preview"))
        self.EqOut.setToolTip(_translate("MainWindow", "Output"))
        self.EqOut.setStatusTip(_translate("MainWindow", "Output in exact form"))
        self.EqOut.setWhatsThis(_translate("MainWindow", "Output in exact form"))
        self.EqVar.setToolTip(_translate("MainWindow", "Variable"))
        self.EqVar.setStatusTip(_translate("MainWindow", "Solve for variable"))
        self.EqVar.setWhatsThis(_translate("MainWindow", "Solve for variable"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Eq), _translate("MainWindow", "Equation Solver"))
        self.SimpOutType.setText(_translate("MainWindow", "Output type"))
        self.SimpPP.setToolTip(_translate("MainWindow", "Pretty print"))
        self.SimpPP.setStatusTip(_translate("MainWindow", "Pretty print"))
        self.SimpPP.setWhatsThis(_translate("MainWindow", "Pretty print"))
        self.SimpPP.setText(_translate("MainWindow", "Pretty"))
        self.SimpLatex.setToolTip(_translate("MainWindow", "Latex"))
        self.SimpLatex.setStatusTip(_translate("MainWindow", "Latex"))
        self.SimpLatex.setWhatsThis(_translate("MainWindow", "Latex"))
        self.SimpLatex.setText(_translate("MainWindow", "Latex"))
        self.SimpNormal.setToolTip(_translate("MainWindow", "Normal"))
        self.SimpNormal.setStatusTip(_translate("MainWindow", "Normal"))
        self.SimpNormal.setWhatsThis(_translate("MainWindow", "Normal"))
        self.SimpNormal.setText(_translate("MainWindow", "Normal"))
        self.SimpCalc.setToolTip(_translate("MainWindow", "Simplify"))
        self.SimpCalc.setStatusTip(_translate("MainWindow", "Simplify the expression"))
        self.SimpCalc.setWhatsThis(_translate("MainWindow", "Simplify the expression"))
        self.SimpCalc.setText(_translate("MainWindow", "Simplify"))
        self.SimpExp.setToolTip(_translate("MainWindow", "Your expression"))
        self.SimpExp.setStatusTip(_translate("MainWindow", "Type in your expression here"))
        self.SimpExp.setWhatsThis(_translate("MainWindow", "Input expression"))
        self.SimpExp.setPlaceholderText(_translate("MainWindow", "Expression"))
        self.SimpPrev.setToolTip(_translate("MainWindow", "Preview"))
        self.SimpPrev.setStatusTip(_translate("MainWindow", "Preview the expression"))
        self.SimpPrev.setWhatsThis(_translate("MainWindow", "Preview"))
        self.SimpPrev.setText(_translate("MainWindow", "Preview"))
        self.SimpOut.setToolTip(_translate("MainWindow", "Output"))
        self.SimpOut.setStatusTip(_translate("MainWindow", "Output"))
        self.SimpOut.setWhatsThis(_translate("MainWindow", "Output"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Simp), _translate("MainWindow", "Simplify"))
        self.ExpExp.setToolTip(_translate("MainWindow", "Your expression"))
        self.ExpExp.setStatusTip(_translate("MainWindow", "Type in your expression here"))
        self.ExpExp.setWhatsThis(_translate("MainWindow", "Input expression"))
        self.ExpExp.setPlaceholderText(_translate("MainWindow", "Expression"))
        self.ExpOut.setToolTip(_translate("MainWindow", "Output"))
        self.ExpOut.setStatusTip(_translate("MainWindow", "Output"))
        self.ExpOut.setWhatsThis(_translate("MainWindow", "Output"))
        self.ExpPrev.setToolTip(_translate("MainWindow", "Preview"))
        self.ExpPrev.setStatusTip(_translate("MainWindow", "Preview the expression"))
        self.ExpPrev.setWhatsThis(_translate("MainWindow", "Preview the expression"))
        self.ExpPrev.setText(_translate("MainWindow", "Preview"))
        self.ExpCalc.setToolTip(_translate("MainWindow", "Expand"))
        self.ExpCalc.setStatusTip(_translate("MainWindow", "Expand the expression"))
        self.ExpCalc.setWhatsThis(_translate("MainWindow", "Expand the expression"))
        self.ExpCalc.setText(_translate("MainWindow", "Expand"))
        self.ExpOutType.setText(_translate("MainWindow", "Output type"))
        self.ExpPP.setToolTip(_translate("MainWindow", "Pretty print"))
        self.ExpPP.setStatusTip(_translate("MainWindow", "Pretty print"))
        self.ExpPP.setWhatsThis(_translate("MainWindow", "Pretty print"))
        self.ExpPP.setText(_translate("MainWindow", "Pretty"))
        self.ExpLatex.setToolTip(_translate("MainWindow", "Latex"))
        self.ExpLatex.setStatusTip(_translate("MainWindow", "Latex"))
        self.ExpLatex.setWhatsThis(_translate("MainWindow", "Latex"))
        self.ExpLatex.setText(_translate("MainWindow", "Latex"))
        self.ExpNormal.setToolTip(_translate("MainWindow", "Normal"))
        self.ExpNormal.setStatusTip(_translate("MainWindow", "Normal"))
        self.ExpNormal.setWhatsThis(_translate("MainWindow", "Normal"))
        self.ExpNormal.setText(_translate("MainWindow", "Normal"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Exp), _translate("MainWindow", "Expand"))
        self.EvalExp.setToolTip(_translate("MainWindow", "Your expression"))
        self.EvalExp.setStatusTip(_translate("MainWindow", "Type in your expression here"))
        self.EvalExp.setWhatsThis(_translate("MainWindow", "Input expression"))
        self.EvalExp.setPlaceholderText(_translate("MainWindow", "Expression"))
        self.EvalOut.setToolTip(_translate("MainWindow", "Output"))
        self.EvalOut.setStatusTip(_translate("MainWindow", "Output"))
        self.EvalOut.setWhatsThis(_translate("MainWindow", "Output"))
        self.EvalPrev.setToolTip(_translate("MainWindow", "Preview"))
        self.EvalPrev.setStatusTip(_translate("MainWindow", "Preview the expression"))
        self.EvalPrev.setWhatsThis(_translate("MainWindow", "Preview"))
        self.EvalPrev.setText(_translate("MainWindow", "Preview"))
        self.EvalCalc.setToolTip(_translate("MainWindow", "Evaluate"))
        self.EvalCalc.setStatusTip(_translate("MainWindow", "Evaluate the expression"))
        self.EvalCalc.setWhatsThis(_translate("MainWindow", "Evaluate"))
        self.EvalCalc.setText(_translate("MainWindow", "Evaluate"))
        self.EvalOutType.setText(_translate("MainWindow", "Output type"))
        self.EvalPP.setToolTip(_translate("MainWindow", "Pretty print"))
        self.EvalPP.setStatusTip(_translate("MainWindow", "Pretty print"))
        self.EvalPP.setWhatsThis(_translate("MainWindow", "Pretty print"))
        self.EvalPP.setText(_translate("MainWindow", "Pretty"))
        self.EvalLatex.setToolTip(_translate("MainWindow", "Latex"))
        self.EvalLatex.setStatusTip(_translate("MainWindow", "Latex"))
        self.EvalLatex.setWhatsThis(_translate("MainWindow", "Latex"))
        self.EvalLatex.setText(_translate("MainWindow", "Latex"))
        self.EvalNormal.setToolTip(_translate("MainWindow", "Normal"))
        self.EvalNormal.setStatusTip(_translate("MainWindow", "Normal"))
        self.EvalNormal.setWhatsThis(_translate("MainWindow", "Normal"))
        self.EvalNormal.setText(_translate("MainWindow", "Normal"))
        self.PfCalc.setToolTip(_translate("MainWindow", "Calculate"))
        self.PfCalc.setWhatsThis(_translate("MainWindow", "Calculate"))
        self.PfCalc.setWhatsThis(_translate("MainWindow", "Calculate"))
        self.PfCalc.setText(_translate("MainWindow", "Calculate"))
        self.FormulaPreview.setText(_translate("MainWindow", "Preview"))
        self.FormulaCalculate.setText(_translate("MainWindow", "Calculate"))
        self.FormulaOutTypeLabel.setText(_translate("MainWindow", "Output type"))
        self.FormulaSolveSolve.setText(_translate("MainWindow", "Solve"))
        self.FormulaSolveSolve.setStatusTip(_translate("MainWindow", "See Sympy Solve vs Solveset"))
        self.FormulaSolveSolve.setWhatsThis(_translate("MainWindow", "See Sympy Solve vs Solveset"))
        self.FormulaSolveSolveSet.setText(_translate("MainWindow", "Solveset"))
        self.FormulaSolveSolveSet.setStatusTip(_translate("MainWindow", "See Sympy Solve vs Solveset"))
        self.FormulaSolveSolveSet.setWhatsThis(_translate("MainWindow", "See Sympy Solve vs Solveset"))
        self.FormulaPP.setText(_translate("MainWindow", "PP"))
        self.FormulaLatex.setText(_translate("MainWindow", "Latex"))
        self.FormulaNormal.setText(_translate("MainWindow", "Normal"))
        self.FormulaTree.headerItem().setText(0, _translate("MainWindow", "Formulas"))
        self.FormulaTree.setSortingEnabled(True)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Eval), _translate("MainWindow", "Evaluate"))
        self.label_32.setText(_translate("MainWindow", "Number"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Pf), _translate("MainWindow", "Prime Factors"))
        self.ShellRun.setText(_translate("MainWindow", "Run"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Shell), _translate("MainWindow", "Shell"))
        self.menuCopy.setTitle(_translate("MainWindow", "Copy"))
        self.menuTab.setTitle(_translate("MainWindow", "Tab"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Web), _translate("MainWindow", "Web"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Formula), _translate("MainWindow", "Formulas"))
        self.actionCopy_exact_answer.setText(_translate("MainWindow", "Copy exact answer"))
        self.actionCopy_exact_answer.setShortcut(_translate("MainWindow", "Ctrl+E"))
        self.actionCopy_exact_answer.triggered.connect(self.copyExact)
        self.actionCopy_approximate_answer.setText(_translate("MainWindow", "Copy approximate answer"))
        self.actionCopy_approximate_answer.setShortcut(_translate("MainWindow", "Ctrl+A"))
        self.actionCopy_approximate_answer.triggered.connect(self.copyApprox)
        self.actionNext_Tab.setText(_translate("MainWindow", "Next Tab"))
        self.actionNext_Tab.setShortcut(_translate("MainWindow", "Ctrl+Right"))
        self.actionNext_Tab.triggered.connect(self.nextTab)
        self.actionPrevious_Tab.setText(_translate("MainWindow", "Previous Tab"))
        self.actionPrevious_Tab.setShortcut(_translate("MainWindow", "Ctrl+Left"))
        self.menuSettings.setTitle(_translate("MainWindow", "Settings"))
        self.actionUse_Unicode.setText(_translate("MainWindow", "Use Unicode"))
        self.actionUse_Unicode.setShortcut(_translate("MainWindow", "Ctrl+U"))
        self.actionUse_Unicode.triggered.connect(self.toggleUni)
        self.actionLine_Wrap.setText(_translate("MainWindow", "Line Wrap"))
        self.actionLine_Wrap.setShortcut(_translate("Mainwindow", "Ctrl+L"))
        self.actionLine_Wrap.triggered.connect(self.toggleWrap)
        self.menuWeb.setTitle(_translate("MainWindow", "Web"))


if __name__ == "__main__":
    ### For Debugging purposes, Removing the comments from the next 6 rows will catch and print all errors that occurs
    def excepthook(exc_type, exc_value, exc_tb):
        tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print("error catched!:")
        print("error message:\n", tb)
        QtWidgets.QApplication.quit()


    sys.excepthook = excepthook
    e = Ui_MainWindow()
    print("Debug mode")
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
