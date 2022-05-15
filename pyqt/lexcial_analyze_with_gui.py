from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot,Qt
from PyQt5.QtWidgets import *
import sys
from lexical_analyze_gui import Ui_MainWindow
import re
from lexical_analyze_with_nonGui import *

class lexcialWithGui(QtWidgets.QMainWindow,Ui_MainWindow,QWidget):
    def __init__(self, parent=None):
        super(lexcialWithGui, self).__init__(parent)
        self.setupUi(self)
        self.initGUI()
#        self.initValue()
        self.initProcess()
        self.setFocusPolicy(Qt.ClickFocus)
        self.setWindowTitle('词法分析器')

    def initGUI(self): #初始化所有GUI
        self.action_ShowKEY.triggered.connect(self.FshowKEY)  # 绑定显示关键字事件
        self.actionOP_Arithmetic.triggered.connect(self.FshowOP_Arithmetic)
        self.actionOP_Relation.triggered.connect(self.FshowOP_Relation)
        self.actionOP_Delimiter.triggered.connect(self.FshowDelimeter)
        self.actionShowAll.triggered.connect(self.FshowAll)
        self.plainTextEdit.textChanged.connect(self.InputChanged)
        self.actionShowDefault.triggered.connect(self.FshowDeRule)
        self.actionReDefault_2.triggered.connect(self.DefaultValue)
        self.lexical_analyzer = lexical()
        self.lexical_analyzer.read_grammar('lexical_grammar')
        self.lexical_analyzer.build_nfa()
        self.lexical_analyzer.nfa_to_dfa()


    def initProcess(self): #初始化处理过程的变量
        self.curPoint = 0;  # 当前指针
        self.finalI = 0; # 最末指针
        self.curRow = 1;  # 当前行
        self.beforeRow= 1;  #先前行
        self.curColumn = 1;  # 当前列
        self.cont  = ''
        self.printList  = [] #输出的表格
        self.identifierL = []  # 存放标识符
        self.constantL = []  # 存放常数

    def RefreshValue(self): #刷新每个GUI显示的内容
        self.label.setText(self.mode)
        # 初始化显示对话框
        self.setListToTableWidget(self.UserKEY, self.DialogShowKEY.tableWidget)
        self.setListToTableWidget(self.UserArith, self.DialogOPArithmetic.tableWidget)
        self.setListToTableWidget(self.UserRelation, self.DialogOPRelation.tableWidget)
        self.setListToTableWidget(self.UserDelim, self.DialogDelimeter.tableWidget)
        self.set4ListToTableWidget(self.UserKEY, self.UserArith, self.UserRelation, self.UserDelim,
                                   self.DialogShowAll.tableWidget)
        self.setDialogSet(self.UserKEY, self.UserArith, self.UserRelation, self.UserDelim, self.DialogSet)
        self.InputChanged()

    def DefaultValue(self): #刷新为默认规则
        self.mode = '默认'
        #初始化显示对话框
        self.setListToTableWidget(self.DeKEY, self.DialogShowKEY.tableWidget)
        self.setListToTableWidget(self.DeArith,self.DialogOPArithmetic.tableWidget)
        self.setListToTableWidget(self.DeRelation,self.DialogOPRelation.tableWidget)
        self.setListToTableWidget(self.DeDelim,self.DialogDelimeter.tableWidget)
        self.set4ListToTableWidget(self.DeKEY,self.DeArith,self.DeRelation,self.DeDelim,self.DialogShowAll.tableWidget)

        #初始化设置对话框
        self.setDialogSet(self.DeKEY,self.DeArith,self.DeRelation,self.DeDelim,self.DialogSet)

        #初始化显示默认对话框
        self.set4ListToTableWidget(self.DeKEY, self.DeArith, self.DeRelation, self.DeDelim,self.DialogDefa.tableWidget)

        #初始化User
        self.UserKEY = self.DeKEY
        self.UserArith = self.DeArith
        self.UserRelation = self.DeRelation
        self.UserDelim = self.DeDelim

    def FshowDeRule(self): #显示默认对话框
        self.DialogDefa.show()
        self.DialogDefa.exec()

    def setDialogSet(self,List1,List2,List3,List4,obj): #专门为DialogSet设计，显示特定内容
        #参数obj是tabwidget
        str1 = '\t'.join(List1)
        str2 = '\t'.join(List2)
        str3 = '\t'.join(List3)
        str4 = '\t'.join(List4)
        obj.textEdit1.clear()
        obj.textEdit1.append(str1)
        obj.textEdit2.clear()
        obj.textEdit2.append(str2)
        obj.textEdit3.clear()
        obj.textEdit3.append(str3)
        obj.textEdit4.clear()
        obj.textEdit4.append(str4)

    def FshowKEY(self):  #显示关键字
        self.RefreshValue()
        self.DialogShowKEY.show()

    def FshowOP_Arithmetic(self): #显示算术运算符
        self.RefreshValue()
        self.DialogOPArithmetic.show()
        self.DialogOPArithmetic.exec_()

    def FshowOP_Relation(self): #显示逻辑运算符
        self.DialogOPRelation.show()
        self.DialogOPRelation.exec_()

    def FshowDelimeter(self): #显示分界符
        self.RefreshValue()
        self.DialogDelimeter.show()
        self.DialogDelimeter.exec_()

    def FshowAll(self): #显示所有
        self.RefreshValue()
        self.DialogShowAll.show()
        self.DialogShowAll.exec_




    def setListToTableWidget(self,List,obj): #将List列表显示到obj(QtableWidget)中,不适用于showall
        k = 0
        obj.setRowCount(round(len(List)/2)+20) #设置行数
        rowNum = obj.rowCount()  # 获取行数
        columnNum = obj.columnCount()  # 获取列数
        for i in range(0,rowNum):
            for j in range(0,columnNum):
                if k >= len(List):
                    obj.setItem(i, j, None)
                else:
                    item = QtWidgets.QTableWidgetItem(List[k])
                    obj.setItem(i,j,item)
                    obj.item(i,j).setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
                k = k + 1

    def set4ListToTableWidget(self,List1,List2,List3,List4,obj):
        tmp = [len(List1), len(List2),len(List3),len(List4)]
        maxrows = max(tmp)
        L = [List1,List2,List3,List4]
        obj.setRowCount(maxrows+20) #设置最大行数
        rowNum = obj.rowCount()  # 获取行数
        columnNum = obj.columnCount()  # 获取列数
        for i in range(0, rowNum): #将所有格子清除内容
            for j in range(0, columnNum):
                obj.setItem(i, j, None)
        for j in range(0,columnNum):
            for i in range(0,len(L[j])):
                item = QtWidgets.QTableWidgetItem(L[j][i])
                obj.setItem(i, j, item)
                obj.item(i, j).setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

    def FprintList(self,obj):
        obj.setRowCount(len(self.printList))  # 设置最大行数
        rowNum = obj.rowCount()  # 获取行数
        columnNum = obj.columnCount()  # 获取列数
        rowNum = 100
        columnNum = 40
        for i in range(0, rowNum):  # 将所有格子清除内容
            for j in range(0, columnNum):
                obj.setItem(i, j, None)
        for i in range(0, len(self.printList)):
            print(self.printList[i])
            item = QtWidgets.QTableWidgetItem(str(self.printList[i][0]))
            obj.setItem(i, 0, item)
            obj.item(i, 0).setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

            if self.printList[i][1][0] == 'Error':
                tmpstr = 'Error'
            else:
                tmpstr = str(self.printList[i][1])

            item = QtWidgets.QTableWidgetItem(tmpstr)
            obj.setItem(i, 1, item)
            obj.item(i, 1).setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

            item = QtWidgets.QTableWidgetItem(self.printList[i][2])
            obj.setItem(i, 2, item)
            obj.item(i, 2).setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

            tmpstr = str(self.printList[i][3][0])
            item = QtWidgets.QTableWidgetItem(tmpstr)
            obj.setItem(i, 3, item)
            obj.item(i, 3).setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

    def InputChanged(self):
        if self.plainTextEdit.toPlainText()[-1]== '\n':
            self.printList.clear()
            reader = open('token_table.data', 'r')
            # print((reader.__str__().split('\n')))
            # self.curRow=reader.split('\n')
            for line in reader:
                self.curRow = line[0]
                tmp = [line.split(' ')[0], line.split(' ')[1], line.split(' ')[2], line.split(' ')[3]]
                self.printList.append(tmp)
                    #print('exe1')
            # self.curRow = self.beforeRow
            #print('exe2')
            reader.close()
        #self.cont = self.plainTextEdit.toPlainText() + '\n'
        writer = open('inputCode.c', 'w+', encoding='UTF-8')
        writer.write('%s' % self.plainTextEdit.toPlainText());
        writer.close()
        self.lexical_analyzer.start_lexical_analyze('inputCode.c')
        #self.mainProcess()

        print(self.curRow)
        print(self.beforeRow)
        self.beforeRow=self.curRow
        self.FprintList(self.tableWidget)


    def oneWordProcess(self): #向前处理一个单词
        if(self.curPoint >= self.finalI): #处理完毕，到了字符串的末尾
            print('已经到达末尾')
            return
        elif self.cont[self.curPoint] == '\n': #处理换行
            self.curRow += 1
            self.curColumn = 1
            self.curPoint += 1
            return
        return


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('fusion')
    lexical_analyzer = lexcialWithGui()
    lexical_analyzer.show()
    sys.exit(app.exec_())


