# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 09:09:50 2020

@author: Maximilian Skoda
"""
import json
import os.path


from PyQt5.QtCore import (QAbstractItemModel, QFile, QIODevice,
         QItemSelectionModel, QModelIndex, Qt, QDataStream, QVariant)
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import (QWidget, QLabel, QMessageBox, 
    QComboBox, QApplication, QTreeWidget, qApp, QFileDialog)

from functools import partial

#import NRActions
# Standard import
import importlib

# import custom 'actions' file
import NRActions
# define name string for dynamic import of action classes:
myActions = "NRActions"

HORIZONTAL_HEADERS = ("Action", "Paramters", "Ok", "")


class myStandardItemModel(QtGui.QStandardItemModel):
    def __init__(self, parent = None):
        super(myStandardItemModel, self).__init__(parent)
        #self.populate('C:/Users/ktd43279/Documents/build-Reorderable_tree-Desktop-Debug/debug/actionList2.json')
        self.populate('json_test.json')

    def flags(self, index):
        defaultFlags =  QtCore.Qt.ItemIsEnabled | super(myStandardItemModel, self).flags(index)
        
        if index.column() == 1:
            return defaultFlags | QtCore.Qt.ItemIsEditable
        
        if index.isValid():
            return defaultFlags | Qt.ItemIsDragEnabled# | Qt.ItemIsDropEnabled
        else:
            return defaultFlags | Qt.ItemIsDropEnabled
        
    def itemList(self, parent = QtCore.QModelIndex()):
        items = []
        for row in range(self.rowCount(parent)):
            idx = self.index(row, 0, parent)
            items.append(self.data(idx))
            if self.hasChildren(idx):
                items.append(self.itemList(idx))
        return items
    
    
    def headerData(self, column, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
        role == QtCore.Qt.DisplayRole):
            try:
                return QtCore.QVariant(HORIZONTAL_HEADERS[column])
            except IndexError:
                pass
        return QtCore.QVariant()
    
    
    def getItemText(self, row, col):
        return self.item(row,col).text()
    
    def getRootItem(self, row, col):
        return self.item(row,col)
    
    def setMyText(self, index, text):
        self.item(index.row(), index.column()).setText(text)

    
    def populate(self, file):
        if os.path.isfile(file):
            with open(file) as json_file:
                data = json.load(json_file)
            #keys_list=data['Action']
            #print(keys_list[0].values())
            for p in data['Action']:
                parentItem = self.invisibleRootItem()
                parentItem.setFlags(parentItem.flags() & ~QtCore.Qt.ItemIsEditable & ~QtCore.Qt.ItemIsDropEnabled)
                
                if isinstance(p, dict):
                    for key in p.keys():
                        #rowNoItem = QtGui.QStandardItem("")
                        item2 = QtGui.QStandardItem("")
                        item = QtGui.QStandardItem(key)
                        itemCheck = QtGui.QStandardItem("")
                        lastItem = QtGui.QStandardItem("")
                        
                        
                        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable \
                                                   & ~QtCore.Qt.ItemIsDropEnabled\
                                                   & ~QtCore.Qt.ItemIsDragEnabled)
                        itemCheck.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable \
                                                   & ~QtCore.Qt.ItemIsDropEnabled\
                                                   & ~QtCore.Qt.ItemIsDragEnabled)
                        lastItem.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable \
                                                   & ~QtCore.Qt.ItemIsDropEnabled\
                                                   & ~QtCore.Qt.ItemIsDragEnabled)
                    parentItem.appendRow([item,item2,itemCheck,lastItem])

                    for it in p.get(next(iter(p))):
                        par = QtGui.QStandardItem(it.get('label'))
                        par.setFlags(item.flags() & QtCore.Qt.ItemIsEditable & ~QtCore.Qt.ItemIsDragEnabled)
                        if isinstance(it.get('value'), list):
                            li = [float(i) if '.' in i else int(i) for i in it.get('value')]                            
                            values = str(li).strip('[]')
                        else:
                            values = it.get('value')
                        val = QtGui.QStandardItem(values)
                        val.setFlags(item.flags() & ~QtCore.Qt.ItemIsDragEnabled)
                        item.appendRow([par,val])
                                      
                       



class ComboBoxDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent=None):
        super(ComboBoxDelegate, self).__init__(parent)
        self.items = []

    def setItems(self, items):
        self.items = items

    def createEditor(self, parent, option, index):       
        row = index.row()
        if row == 0 and index.parent().row() >= 0:# not the very first row
            #print(index.parent().row())
            editor = QtWidgets.QComboBox(parent)
            editor.addItems(self.items)
            return editor
        else:
            return QtWidgets.QItemDelegate.createEditor(self, parent, option, index)

    def setEditorData(self, editor, index):        
        if index.column() == 1 and index.parent().row() >= 0 and index.row() == 0: #just to be sure that we have a QCombobox
            editor.setCurrentIndex(editor.findText(index.data(QtCore.Qt.DisplayRole), QtCore.Qt.MatchFixedString))           
        else:
            QtWidgets.QItemDelegate.setEditorData(self, editor, index)

        
    def setModelData(self, editor, model, index):
        row = index.row()
        if row == 0 and index.parent().row() >= 0:
            model.setData(index, editor.currentText(), QtCore.Qt.DisplayRole)
        else:
            QtWidgets.QItemDelegate.setModelData(self, editor, model, index)


    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

### probably not needed any more: 
class actionListWidget(QtWidgets.QListWidget):
    def __init__(self, type, parent=None):
        super(actionListWidget, self).__init__(parent)
        self.setDragEnabled(True)
        self.addItems(["RunAngle","ConrastChange", "Transmission"])
        
        mimeData = QtCore.QMimeData()
        mimeData.setText("NR_Action")
        
        self.setMaximumWidth(self.sizeHintForColumn(0)+20)
        self.setMinimumWidth(self.sizeHintForColumn(0)+10)


class Tree(QtWidgets.QTreeView):
    def __init__(self, type, parent=None):
        super(Tree, self).__init__(parent)
        
        self.model = myStandardItemModel()
        self.setModel(self.model)
        
        self.delegate = ComboBoxDelegate()
        self.setItemDelegateForColumn(1, self.delegate)
        
        self.setEditTriggers(QtWidgets.QAbstractItemView.CurrentChanged)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove|QtWidgets.QAbstractItemView.DragDrop)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        
        
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.resizeColumnToContents(0)        
        self.setAlternatingRowColors(True)
        self.resize(self.sizeHint().height(), self.minimumHeight())    
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)
        
        self.collapsed.connect(self.showSummary)
        self.expanded.connect(self.removeSummary)  
        rows = self.model.rowCount()

        for i in range(rows):
            self.showSummary(self.model.index(i,0))
    
   

    def showSummary(self, index):      
        it = self.model.getRootItem(index.row(), index.column())

        colors = ["black", "red","blue","brown","orange","darkviolet","salmon","lavender"]

        clName = it.text()
        MyClass = getattr(importlib.import_module(myActions), clName)
        # Instantiate the class (pass arguments to the constructor, if needed)
        tempAction = MyClass()
        tempAction.makeAction(it)

        if len(self.delegate.items) and it.child(0,1).text() in self.delegate.items:
            colorIndex = self.delegate.items.index(it.child(0,1).text())
            self.model.invisibleRootItem().child(index.row(),1).\
                        setForeground(QtGui.QColor(QtGui.QColor(colors[colorIndex])))
        
        self.model.invisibleRootItem().child(index.row(),1).setText(tempAction.summary())#setText(shortText)
        self.resizeColumnToContents(1)
#        tstr = tempAction.summary()
        if tempAction.isValid():
            self.model.invisibleRootItem().child(index.row(),2).\
                        setBackground(QtGui.QColor(QtGui.QColor("green")))
        else:
            self.model.invisibleRootItem().child(index.row(),2).\
                        setBackground(QtGui.QColor(QtGui.QColor("red")))
        return tempAction.summary()#shortText
        del tempAction
        
    def removeSummary(self, index):      
        self.model.invisibleRootItem().child(index.row(),1).setText("")
 
        
    def openMenu(self, position): 
        self.menu = QtWidgets.QMenu()
        index = self.indexAt(position)
         
        self.sub_menu = QtWidgets.QMenu("Insert Action")
        self.menu.addMenu(self.sub_menu)
        deleteAction = self.menu.addAction("Delete Row") 

        #insertAction = menu.addAction("Insert action")
        actions = NRActions.actions  #["RunAngles", "ContrastChange", "SetJulabo"]
        for name in actions:
            action = self.sub_menu.addAction(name)
            #action.setData(Person(name=name))
            action.triggered.connect(partial(self.menu_action, action, index))

        
        action = self.menu.exec_(self.viewport().mapToGlobal(position))
        
        if action == deleteAction:
            for items in self.selectionModel().selectedRows():
                self.model.takeRow(items.row())


    def menu_action(self, item, index):        
        item2 = QtGui.QStandardItem("")
        item = QtGui.QStandardItem(item.text())
        itemCheck = QtGui.QStandardItem("")
        rowNumberItem = QtGui.QStandardItem("")
        #print(item.text())
        clName = item.text()
        MyClass = getattr(importlib.import_module(myActions), clName)
        # Instantiate the class (pass arguments to the constructor, if needed)
        actionItem = MyClass()
            
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable \
                                  & ~QtCore.Qt.ItemIsDropEnabled\
                                  & ~QtCore.Qt.ItemIsDragEnabled)
        root = self.model.invisibleRootItem()
        root.insertRow(index.row()+1,[item,item2,itemCheck, rowNumberItem])
        newRow = self.model.item(index.row()+1) 
        for key in actionItem.__dict__:          
            par = QtGui.QStandardItem(key)
            if isinstance(actionItem.__dict__[key], list):
                #li = [float(i) if '.' in i else int(i) for i in runAngleItem.__dict__[key]]                            
                values = str(actionItem.__dict__[key]).strip('[]')
            else:
                values =str(actionItem.__dict__[key])
                
            val = QtGui.QStandardItem(values)
            newRow.appendRow([par,val])
        del actionItem
        
    def on_context_menu_factions(self, pos):
        self.menu.exec_( QtGui.QCursor.pos() )

       

            
##### Main App ###########
                    
class App(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)

        
        self.view = Tree(self)
        
        rows = self.view.model.rowCount()
        for i in range(rows):
            self.view.showSummary(self.view.model.index(i,0))
            
        # set the font
        font = QtGui.QFont("AnyStyle", 10)
        self.view.setFont(font)

        self.dataGroupBox = QtWidgets.QGroupBox("NR Script")
        dataLayout = QtWidgets.QHBoxLayout()
               
        actionList = actionListWidget(self)
              
        dataLayout.addWidget(actionList)
        dataLayout.addWidget(self.view)
        
        self.dataGroupBox.setLayout(dataLayout)
        
        mainLayout = QtWidgets.QVBoxLayout()
        
        buttonLayout = QtWidgets.QHBoxLayout()
        self.printTreeButton = QtWidgets.QPushButton("Output script")
        self.printTreeButton.clicked.connect(self.onPrintTree)
        buttonLayout.addWidget(self.printTreeButton)
        self.printSamplesButton = QtWidgets.QPushButton("Print samples")
        self.printSamplesButton.clicked.connect(self.onPrintSamples)
        buttonLayout.addWidget(self.printSamplesButton)
        
        self.fileLabel = QtWidgets.QLabel("Script file: ")
        self.fileEdit = QtWidgets.QLineEdit()
        self.fileOpenButton = QtWidgets.QPushButton("...")
        self.fileOpenButton.clicked.connect(self.onOpenFile)
        fileLayout = QtWidgets.QHBoxLayout()
        fileLayout.addWidget(self.fileLabel)
        fileLayout.addWidget(self.fileEdit)
        fileLayout.addWidget(self.fileOpenButton)
        
        mainLayout.addLayout(fileLayout)
        mainLayout.addLayout(buttonLayout)
        
        # Sample Table - this is NR specific and should be moved to NRActions.py!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.sampleTable = QtWidgets.QTableWidget()
        self.sampleTable.setRowCount(8)
        self.sampleTable.setColumnCount(9)
        self.sampleTable.verticalHeader().setDefaultSectionSize(20);
        self.sampleTable.setHorizontalHeaderLabels(["Sample/Title", "Trans", "Height", "Phi Offset",\
                                               "Psi", "Footprint", "Resolution", "Coarse_noMirror", "Switch"])
        self.initTable()
        self.sampleTable.cellChanged.connect(self.updateSample)
           
        # checkbox to hide table
        self.b = QtWidgets.QCheckBox("Hide/Show Sample Table",self)
        self.b.stateChanged.connect(self.clickBox)
        mainLayout.addWidget(self.dataGroupBox)
        mainLayout.addWidget(self.b)
        mainLayout.addWidget(self.sampleTable)
        self.setLayout(mainLayout)
        
        self.view.resizeColumnToContents(0)
        self.view.header().resizeSection(2, 25)
        
        self.show()
        
###########  
        
    def onOpenFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "",\
                                                  "OpenGenie Files (*.gcl);;All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            self.fileEdit.setText(fileName)
        
    def onPrintTree(self):
        f= open(self.fileEdit.text(),"w+")
        args = []
        for col in range(self.sampleTable.columnCount()):            
            if self.sampleTable.item(0,col).checkState()  == Qt.Checked:
                args.append(1)
            else:
                args.append(0)
        f.write(NRActions.writeHeader(self.onPrintSamples(), args))

        for row in range(self.view.model.rowCount()):
            it = self.view.model.item(row)
            
            MyClass = getattr(importlib.import_module(myActions), it.text())
           # Instantiate the class (pass arguments to the constructor, if needed)
            tempAction = MyClass()
            tempAction.makeAction(it)

            sampleNumber = self.view.delegate.items.index(it.child(0,1).text()) + 1
            f.write(tempAction.stringLine(sampleNumber)+"\n")

        f.write(NRActions.writeFooter(self.onPrintSamples()))
        f.close()

    def onPrintSamples(self):
        samples = []        
        for row in range(1,self.sampleTable.rowCount()):            
            if self.sampleTable.item(row,0).text() != "":
                sampleDict = {}
                for col in range(self.sampleTable.columnCount()):
                    sampleDict[self.sampleTable.horizontalHeaderItem(col).text()] = self.sampleTable.item(row,col).text()
                samples.append(sampleDict)

        return samples
            
            
   
    def clickBox(self, state):
        if state == QtCore.Qt.Checked:
            self.sampleTable.setHidden(True)
        else:
            self.sampleTable.setHidden(False)
    
    ### initialise sample table:   
    def initTable(self):
        self.sampleTable.setVerticalHeaderLabels(["","1","2","3","4","5","6","7"])
        for row in range(self.sampleTable.rowCount()):          
            for col in range(self.sampleTable.columnCount()):
                if row == 0:
                    checkItem = QtWidgets.QTableWidgetItem()
                    checkItem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    checkItem.setCheckState(Qt.Unchecked)
                    checkItem.setTextAlignment(Qt.AlignCenter)
                    self.sampleTable.setItem(row, col, checkItem)
                else:
                    item = QtWidgets.QTableWidgetItem()
                    item.setText("")
                    self.sampleTable.setItem(row, col, item)
        self.sampleTable.resizeColumnsToContents()

        
    def updateSample(self, index):
        sampleList=[]

        complete=True
        for row in range(1,self.sampleTable.rowCount()):
            sampleRow=[]
            for col in range(self.sampleTable.columnCount()):
                item = self.sampleTable.item(row,col)
                if item.text() != "":
                    sampleRow.append(item.text())
                else:
                    complete = False
            if complete:               
                sampleList.append(sampleRow[0])
                #self.sample = NRActions.NRSample(sampleRow)
                self.sampleTable.resizeColumnsToContents()
            else:
                return()
            self.view.delegate.setItems(sampleList)
            
        

class MyMainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        
        super(MyMainWindow, self).__init__(parent)
        self.form_widget = App(self) 
        self.setCentralWidget(self.form_widget)    
        
        openAct = QtWidgets.QAction(QtGui.QIcon('exit.png'), '&Open...', self)        
        openAct.setShortcut('Ctrl+O')
        openAct.setStatusTip('Open script')
        openAct.triggered.connect(self.openScript)

        saveAct = QtWidgets.QAction(QtGui.QIcon('exit.png'), '&Save', self)        
        saveAct.setShortcut('Ctrl+S')
        saveAct.setStatusTip('Save script')
        saveAct.triggered.connect(self.saveScript)
        
        exitAct = QtWidgets.QAction(QtGui.QIcon('exit.png'), '&Exit', self)        
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)
        
        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openAct)
        fileMenu.addAction(saveAct)
        fileMenu.addAction(exitAct)
        
        
        QtWidgets.qApp.installEventFilter(self)
      
        
    def openScript(self):
        print("Opening...")
        buttonReply = QMessageBox.question(self, 'MaxSkript', "All changes will be lost. Do you want to save?",\
                                           QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
        if buttonReply == QMessageBox.Yes:
            print('Yes clicked.')
        if buttonReply == QMessageBox.No:
            print('No clicked.')
        if buttonReply == QMessageBox.Cancel:
            print('Cancel')
        
        
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "",\
                                                  "MaxScript Files (*.json);;All Files (*)", options=options)


        for row in range(self.form_widget.view.model.invisibleRootItem().rowCount()):
            delrow = self.form_widget.view.model.takeRow(row)
            del delrow
        
        self.form_widget.view.model.populate(fileName)
        with open(fileName) as json_file:
            data = json.load(json_file)

            for row, samp in enumerate(data['Samples'],start=1):
                if len(samp):
                    for col in range(self.form_widget.sampleTable.columnCount()):
                        self.form_widget.sampleTable.item(row,col).setText(samp[col])
        
        rows = self.form_widget.view.model.rowCount()
        for i in range(rows):
            self.form_widget.view.showSummary(self.form_widget.view.model.index(i,0))

        
    def saveScript(self):
        print("Saved.")
        f= open("json_test_save.json","w+")
        outString = "{\"Samples\": ["
        ## get defined samples from table:
        for row in range(1,self.form_widget.sampleTable.rowCount()):
            sampleRow=[]
            for col in range(self.form_widget.sampleTable.columnCount()):
                item = self.form_widget.sampleTable.item(row,col)
                if item.text() != "":
                    sampleRow.append(item.text())
            outString += json.dumps(sampleRow) 
            if row < self.form_widget.sampleTable.rowCount()-1:
                outString += ",\n"
            else:
                outString += "],\n"


        outString += "\n\n\"Action\":[\n"
        for row in range(self.form_widget.view.model.rowCount()):
            it = self.form_widget.view.model.item(row)
            MyClass = getattr(importlib.import_module(myActions), it.text())
           # Instantiate the class (pass arguments to the constructor, if needed)
            tempAction = MyClass()
            tempAction.makeAction(it)
            outString += tempAction.makeJSON()
            if row < self.form_widget.view.model.rowCount() - 1:
                outString += ","
            del tempAction
                
        outString += "]\n}"
        f.write(outString)
        f.close()


    
    def eventFilter(self, object, event):          
        if (object is self.form_widget.view):
            #print(event.type())
            if (event.type() == QtCore.QEvent.DragEnter):
                print("accept1",event.mimeData())
                if event.mimeData().hasText():
                    event.accept()   # must accept the dragEnterEvent or else the dropEvent can't occur !!!
                    print("accept")
                else:
                    event.ignore()
                    print("ignore")
            if (event.type() == QtCore.QEvent.Drop):
                print("Dropped")
                if event.mimeData().hasUrls():   # if file or link is dropped
                    urlcount = len(event.mimeData().urls())  # count number of drops
                    url = event.mimeData().urls()[0]   # get first url
                    object.setText(url.toString())   # assign first url to editline
                    #event.accept()  # doesnt appear to be needed
            return False # lets the event continue to the edit
        return super(MyMainWindow, self).eventFilter(object, event)  

def main():

    app = QApplication([])
    app.aboutToQuit.connect(app.deleteLater)
    foo = MyMainWindow()
    foo.resize(600, 600)
    foo.setWindowTitle("McScript")
    foo.setWindowIcon(QtGui.QIcon('squareCogs.gif'))
    foo.show()
    app.exec_()


if __name__ == '__main__':
    main()
