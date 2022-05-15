from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
from syntax_analyze_gui import Ui_MainWindow
from syntax_analyze_with_nonGui import *
from lexical_analyze_with_nonGui import *

class LR1(QtWidgets.QMainWindow,Ui_MainWindow):
    def __init__(self, parent=None):
        super(LR1, self).__init__(parent)
        self.setupUi(self)
        self.initGUI()
        self.initValue()

    def initGUI(self): # 初始化GUI
        self.syntax_analyze = syntax()
        self.syntax_analyze.read_grammar('syntax_grammar')
        self.syntax_analyze.get_terminate_nonterminate()
        self.syntax_analyze.init_first_set()
        self.syntax_analyze.init_action_goto_table()

        self.lexical_analyzer = lexical()
        self.lexical_analyzer.read_grammar('lexical_grammar')
        self.lexical_analyzer.build_nfa()
        self.lexical_analyzer.nfa_to_dfa()

        self.tableWidget.horizontalHeader().setStretchLastSection(True);
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tableWidget.setHorizontalHeaderLabels(['状态栈', '符号栈', '剩余输入栈(因为栈故逆序)', '动作'])
        self.tableWidget.setRowCount(3)  # 需要设置

        self.lineEdit.textChanged.connect(self.inputLineChanged)

    def initValue(self): #初始化必要变量
        self.Fprocedure()

    def showProcedure(self): #显示处理过程
        obj = self.tableWidget
        obj.setRowCount(len(self.procedure))
        rowNum = obj.rowCount()
        columnNum = obj.columnCount()
        for i in range(0,rowNum):
            for j in range(0,columnNum):
                item = QtWidgets.QTableWidgetItem(self.procedure[i][j])
                obj.setItem(i,j,item)
                obj.item(i,j).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                if j == 2:
                    obj.item(i, j).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

    def inputLineChanged(self): #输入串改变
        writer = open('inputCode.c', 'w+', encoding='UTF-8')
        writer.write('%s' % self.lineEdit.text());
        writer.close()
        self.Fprocedure()

    def Fprocedure(self):
        self.procedure = []
        self.lexical_analyzer.start_lexical_analyze('inputCode.c')
        self.syntax_analyze.read_and_analyze('token_table.data')
        self.procedure = self.syntax_analyze.procedure
        self.showProcedure()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('fusion')
    LR_1 = LR1()
    LR_1.setWindowTitle('语法分析器')
    LR_1.show()
    sys.exit(app.exec_())
