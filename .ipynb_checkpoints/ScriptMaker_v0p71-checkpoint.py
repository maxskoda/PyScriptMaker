# -*- coding: utf-8 -*-
"""
Created on Thu May 12 09:09:50 2020

@author: Maximilian Skoda
"""
import json
import os.path
import zmq

from PyQt5.QtCore import (QAbstractItemModel, QFile, QIODevice, pyqtSlot, QSortFilterProxyModel,
         QItemSelectionModel, QModelIndex, Qt, QDataStream, QVariant)
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (QWidget, QLabel, QMessageBox, QShortcut, QAbstractItemDelegate, QListWidgetItem,
    QComboBox, QApplication, QTreeWidget, qApp, QFileDialog, QAbstractItemView, QStyledItemDelegate, QDoubleSpinBox,
                             QSpinBox, QLCDNumber, QSizePolicy)

from functools import partial
import numpy as np

# Standard import
import importlib

# import custom 'actions' file
import NRActions

# define name string for dynamic import of action classes:
myActions = "NRActions"

HORIZONTAL_HEADERS = ("Action", "Parameters", "Ok", "Row Number")


class myStandardItemModel(QtGui.QStandardItemModel):
    def __init__(self, parent = None):
        super(myStandardItemModel, self).__init__(parent)
        #self.populate('C:/Users/ktd43279/Documents/build-Reorderable_tree-Desktop-Debug/debug/actionList2.json')
        #self.populate('INTER_4Samples_2Contrasts_test.json')

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
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
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
            for p in data['Action']:
                parentItem = self.invisibleRootItem()
                parentItem.setFlags(parentItem.flags() & ~QtCore.Qt.ItemIsEditable & ~QtCore.Qt.ItemIsDropEnabled)
                
                if isinstance(p, dict):
                    for key in p.keys():
                        # rowNoItem = QtGui.QStandardItem("")
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
                    parentItem.appendRow([item, item2, itemCheck, lastItem])

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
                        item.appendRow([par, val])


class ProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(ProxyModel, self).__init__(parent)


class ComboBoxDelegate(QtWidgets.QStyledItemDelegate):
    instances = []
    def __init__(self, owner, choices):
        super().__init__(owner)
        self.pModel = owner.tableModel
        self.treeView = owner
        list = []
        self.editor = dict()
        for item in choices:
            if item[0] !="":
                list.append(item[0])
        self.items = list

    def commit_editor(self):
        editor = self.sender()
        self.commitData.emit(editor)

    def createEditor(self, parent, option, index):
        self.updateCombo(index)
        row = index.row()
        hasSample = (self.treeView.model.item(index.parent().row(), 0).child(0, 0).text() == "Sample")
        if row == 0 and index.parent().row() >= 0 and hasSample:# not the very first row
            editor = QtWidgets.QComboBox(parent)
            self.editor[index] = editor
            ComboBoxDelegate.instances.append(editor)
            editor.addItems(self.items)
            editor.currentTextChanged.connect(self.commit_editor)
            editor.highlighted.connect(self.commit_editor)
            return editor
        else:
            editor = QtWidgets.QStyledItemDelegate.createEditor(self, parent, option, index)
            return editor

    def paint(self, painter, option, index):
        self.updateCombo(index)
        try:
            hasSample = (self.treeView.model.item(index.row(), 0).child(0, 0).text() == "Sample")
        except AttributeError:
            pass
        if index.column() == 1 and index.parent().row() >= 0 and index.row() == 0 and hasSample:
            value = index.data(QtCore.Qt.DisplayRole)
            style = QtWidgets.QApplication.style()
            opt = QtWidgets.QStyleOptionComboBox()
            opt.text = str(value)
            opt.rect = option.rect
            style.drawComplexControl(QtWidgets.QStyle.CC_ComboBox, opt, painter)
            QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)
            self.treeView.openPersistentEditor(index)
        else:
            QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)

    def setModelData(self, editor, model, index):
        self.updateCombo(index)
        row = index.row()
        hasSample = (model.item(index.parent().row(), 0).child(0, 0).text() == "Sample")
        if row == 0 and index.parent().row() >= 0 and hasSample:
            if model.item(index.parent().row(), 0).child(0, 0).text() == "Sample":
                model.setData(index, editor.currentText(), QtCore.Qt.DisplayRole)
                editor.setCurrentIndex(editor.findText(editor.currentText()))
        else:
            QtWidgets.QStyledItemDelegate.setModelData(self, editor, model, index)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def updateCombo(self, index):
        # print(self.parent().itemDelegateForColumn(1))
        if isinstance(self.sender(), TableModel):
            indToDelete = []
            for ind in self.editor:
                try:
                    currentIndex = self.editor[ind].findText(self.editor[ind].currentText())
                except RuntimeError:
                    #print("oops")
                    indToDelete.append(ind)
                else:
                    pass
                    # print(currentIndex)
            print(indToDelete)
            for ind in indToDelete:
                del self.editor[ind]
            for ind in self.editor:
                currentIndex = self.editor[ind].findText(self.editor[ind].currentText())
                self.editor[ind].clear()
                list = []
                for item in self.pModel._data:
                    if item[0] != "":
                        list.append(item[0])
                self.items = list
                self.editor[ind].addItems(self.items)
                self.editor[ind].setCurrentIndex(currentIndex)


class SpinBoxDelegate(QStyledItemDelegate):
    def __init__(self, min, max, intOnly=False, parent=None):
        super(SpinBoxDelegate, self).__init__(parent)
        self.min = min
        self.max = max
        self.int = intOnly

    def createEditor(self, parent, option, index):
        if self.int:
            spinBox = QSpinBox(parent)
        else:
            spinBox = QDoubleSpinBox(parent)
            spinBox.setDecimals(3)
        spinBox.setMinimum(self.min)
        spinBox.setMaximum(self.max)
        return spinBox

    def setEditorData(self, spinBox, index):
        # print(index.model().data(index, QtCore.Qt.EditRole))
        value = index.model().data(index, QtCore.Qt.EditRole)
        try:
            spinBox.setValue(float(value))
        except ValueError:
            spinBox.setValue(0.0)

    def setModelData(self, spinBox, model, index):
        spinBox.interpretText()
        value = spinBox.value()
        model.setData(index, value, QtCore.Qt.EditRole)


class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, view, data, headerData):
        super(TableModel, self).__init__()
        self.view = view
        self._data = data
        self.header = headerData
        self.dataChanged.connect(self.onSampleChange)

    def getData(self):
        return self._data

    def data(self, index, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            value = self._data[index.row()][index.column()]
            return str(value)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False
        if role == QtCore.Qt.EditRole:
            self._data[index.row()][index.column()] = str(value)
            self.dataChanged.emit(index, index, [QtCore.Qt.DisplayRole])
            return True
        else:
            return False
        return True

    def rowCount(self, index):
        return len(self._data)
        #return self._data.shape[0]

    def columnCount(self, index):
        return len(self._data[0])
        # return self._data.shape[1]

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def onSampleChange(self):
        for row in range(self.view.model.rowCount()):
            if self.view.model.item(row, 0).child(0, 0).text() == "Sample":
                # print(self.view.model.item(row, 0).child(0, 1).updateCombo())
                self.view.updateSummary()


    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[section]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return str(section+1)

class Tree(QtWidgets.QTreeView):
    def __init__(self, parent=None):
        super(Tree, self).__init__(parent)
        
        self.model = myStandardItemModel()
        self.setModel(self.model)

        # DATA
        # sampleTable = np.array([["S12345", "11", "12", "13", "14"],
        #                         ["S2", "21", "22", "23", "24"],
        #                         ["S3", "31", "32", "33", "34"], ])

        sampleTable = [["S1", "100", "1", "1", "1", "1", "1", "1", "1"],
                       ["S2", "200", "2", "2", "2", "2", "2", "2", "2"],
                       ["S3", "300", "3", "3", "3", "3", "3", "3", "3"],
                       ["S4", "400", "4", "4", "4", "4", "4", "4", "4"],
                       ["", "", " ", " ", " ", " ", " ", " ", " "],
                       ["", "", " ", " ", " ", " ", " ", " ", " "],
                       ["", "", " ", " ", " ", " ", " ", " ", " "]]

        self.headerLabels_sampTable = ["Sample/Title", "Trans", "Height", "Phi Offset",\
                                       "Psi", "Footprint", "Resolution", "Coarse_noMirror", "Switch"]
        self.tableModel = TableModel(self, sampleTable, self.headerLabels_sampTable)

        self.delegate = ComboBoxDelegate(self, sampleTable)
        self.setItemDelegateForColumn(1, self.delegate)
        self.tableModel.dataChanged.connect(self.delegate.updateCombo)
        self.tableModel.dataChanged.connect(self.updateSummary)
        self.model.dataChanged.connect(self.updateRuntime)

        #self.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)#CurrentChanged)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove | QtWidgets.QAbstractItemView.DragDrop)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)

        
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.resizeColumnToContents(0)        
        self.setAlternatingRowColors(True)
        font = QtGui.QFont("Verdana", 10.5)
        font.setWeight(QtGui.QFont.Bold)
        self.header().setFont(font)
        # self.resize(self.sizeHint().height(), self.minimumHeight())
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)
        
        self.collapsed.connect(self.showSummary)
        self.expanded.connect(self.removeSummary)  

        self.shortcut = QShortcut(QKeySequence("Del"), self)
        self.shortcut.activated.connect(self.del_action)

        self.updateSummary()

        # define shortcuts
        self.menu = QtWidgets.QMenu()
        self.sub_menu = QtWidgets.QMenu("Insert Action")
        self.menu.addMenu(self.sub_menu)
        actions = NRActions.actions
        for name in actions:
            shortcut = "Ctrl+" + name[0].lower()
            action = self.sub_menu.addAction(name)
            #action.setShortcut(QtGui.QKeySequence(shortcut))
            short = QtWidgets.QShortcut(QtGui.QKeySequence(shortcut), self)
            short.activated.connect(partial(self.menu_action, action))
            action.triggered.connect(partial(self.menu_action, action))

    def updateRuntime(self):
        self.totalTime = 0.0

        for row in range(self.model.rowCount()):
            try:
                self.model.item(row, 3).setText(str(row + 1))
                it = self.model.getRootItem(row, 0)
                clName = it.text()
                MyClass = getattr(importlib.import_module(myActions), clName)
                # Instantiate the class (pass arguments to the constructor, if needed)
                tempAction = MyClass()
                tempAction.makeAction(it)
                it.setToolTip(tempAction.toolTip())
            except AttributeError as err:
                print("makeAction method undefined in ", tempAction)
            try:
                self.rtime = tempAction.calcTime(self.parent().parent().instrumentSelector.currentText())
                self.totalTime += self.rtime
            except AttributeError:
                pass
        self.parent().parent().runTime.setText("{:02d}h {:02d}min".format(int(divmod(self.totalTime, 60)[0]), int(divmod(self.totalTime, 60)[1])))
        # update window title to indicate unsaved changes:
        self.parent().parent().parent().setWindowModified(True)

    def updateSummary(self):
        for row in range(self.model.rowCount()):
            self.showSummary(self.model.index(row, 0))


    def showSummary(self, index):
        it = self.model.getRootItem(index.row(), index.column())

        colors = ["black", "red", "blue", "green", "orange", "darkviolet", "salmon", "lavender"]

        clName = it.text()
        MyClass = getattr(importlib.import_module(myActions), clName)
        # Instantiate the class (pass arguments to the constructor, if needed)
        tempAction = MyClass()

        try:
            tempAction.makeAction(it)
        except AttributeError as err:
            print("ShowSummary: makeAction method undefined in ", tempAction)

        if len(self.delegate.items) and it.child(0, 1).text() in self.delegate.items:
            colorIndex = self.delegate.items.index(it.child(0, 1).text())
            self.model.invisibleRootItem().child(index.row(), 1).\
                        setForeground(QtGui.QColor(QtGui.QColor(colors[colorIndex])))
        
        self.model.invisibleRootItem().child(index.row(), 1).setText(tempAction.summary())
        self.resizeColumnToContents(1)

        # self.updateRuntime(index)
        try:
            if tempAction.isValid()[0]:
                self.model.invisibleRootItem().child(index.row(), 2).\
                            setBackground(QtGui.QColor(QtGui.QColor("green")))
                item = self.model.getRootItem(index.row(), 2)
                item.setToolTip("")
            else:
                self.model.invisibleRootItem().child(index.row(),2).\
                            setBackground(QtGui.QColor(QtGui.QColor("red")))
                item = self.model.getRootItem(index.row(), 2)
                item.setToolTip(tempAction.isValid()[1])

        except AttributeError as err:
            print("isValid method undefined in ", tempAction)

        #return self.rtime, tempAction.summary()  # shortText
        del tempAction
        
    def removeSummary(self, index):
        self.model.invisibleRootItem().child(index.row(),1).setText("")
 
        
    def openMenu(self, position):
        # self.menu = QtWidgets.QMenu()
        index = self.indexAt(position)
         
        # self.sub_menu = QtWidgets.QMenu("Insert Action")
        # self.menu.addMenu(self.sub_menu)

        deleteAction = QtWidgets.QAction(QtGui.QIcon('exit.png'), '&Delete row(s)', )
        #deleteAction = self.menu.addAction("Delete Row(s)", self.del_action)
        deleteAction.setShortcut(QKeySequence("Del"))
        deleteAction.triggered.connect(self.del_action)
        self.menu.addAction(deleteAction)
        action = self.menu.exec_(self.viewport().mapToGlobal(position))
        
        if action == deleteAction:
            pass
            #for items in self.selectionModel().selectedRows():
             #   self.model.takeRow(items.row())


    def del_action(self):
        # for items in self.selectionModel().selectedRows():
        #     print(self.model.item(items.row(), 0).child(0,1))
        #     self.model.removeRow(items.row())

        index_list = []
        for model_index in self.selectionModel().selectedRows():
            index = QtCore.QPersistentModelIndex(model_index)
            index_list.append(index)

        for index in index_list:
            self.model.removeRow(index.row())


    def menu_action(self, item):
        item2 = QtGui.QStandardItem("")
        item = QtGui.QStandardItem(item.text())
        itemCheck = QtGui.QStandardItem("")
        rowNumberItem = QtGui.QStandardItem("")
        # override index temporarily test
        index = self.selectedIndexes()[0]

        clName = item.text()
        MyClass = getattr(importlib.import_module(myActions), clName)
        # Instantiate the class (pass arguments to the constructor, if needed)
        actionItem = MyClass()
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable \
                                  & ~QtCore.Qt.ItemIsDropEnabled\
                                  & ~QtCore.Qt.ItemIsDragEnabled)
        root = self.model.invisibleRootItem()
        root.insertRow(index.row()+1, [item, item2, itemCheck, rowNumberItem])
        newRow = self.model.item(index.row()+1) 
        for key in actionItem.__dict__:          
            par = QtGui.QStandardItem(key)
            par.setFlags(newRow.flags() & QtCore.Qt.ItemIsEditable & ~QtCore.Qt.ItemIsDragEnabled)
            if isinstance(actionItem.__dict__[key], list):
                values = str(actionItem.__dict__[key]).strip('[]')
            else:
                values =str(actionItem.__dict__[key])
                
            val = QtGui.QStandardItem(values)
            newRow.appendRow([par, val])
            self.resizeColumnToContents(0)
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
        myFont = "Verdana" # Consolas ok
        font = QtGui.QFont(myFont, 10.5)
        self.view.setFont(font)

        self.dataGroupBox = QtWidgets.QGroupBox("NR Script")
        dataLayout = QtWidgets.QHBoxLayout()
               

        #dataLayout.addWidget(actionList)
        dataLayout.addWidget(self.view)
        
        self.dataGroupBox.setLayout(dataLayout)
        
        mainLayout = QtWidgets.QVBoxLayout()

        self.instrumentSelector = QtWidgets.QComboBox()
        self.instrumentSelector.addItems(NRActions.instruments)
        self.instrumentSelector.setFont(QtGui.QFont(myFont, 12, QtGui.QFont.Black))

        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(self.instrumentSelector)
        self.printTreeButton = QtWidgets.QPushButton("Output script (Ctrl + p)", self)
        self.printTreeButton.setFont(QtGui.QFont(myFont, 12, QtGui.QFont.Black))
        self.printTreeButton.setShortcut('Ctrl+p')
        self.printTreeButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.printTreeButton.clicked.connect(self.onPrintTree)
        buttonLayout.addWidget(self.printTreeButton)
        self.printSamplesButton = QtWidgets.QPushButton("Print samples")
        self.printSamplesButton.clicked.connect(self.onPrintSamples)
        # buttonLayout.addWidget(self.printSamplesButton)
        self.timeLabel = QLabel("Duration:~ ")
        self.timeLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.timeLabel.setFont(QtGui.QFont(myFont, 12, QtGui.QFont.Black))
        self.runTime = QLabel("00:00")
        self.runTime.setFont(QtGui.QFont(myFont, 12, QtGui.QFont.Black))
        buttonLayout.addWidget(self.timeLabel)
        buttonLayout.addWidget(self.runTime)
        
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
        self.sampleTableGroupBox = QtWidgets.QGroupBox("Sample table")
        sampleLayout = QtWidgets.QHBoxLayout()

        self.sampleTable = QtWidgets.QTableView()
        # Delegates for enterin correct numbers --- THIS IS NR SPECIFIC ##################################
        self.transDelegate = SpinBoxDelegate(-600.0, 600.0)
        self.sampleTable.setItemDelegateForColumn(1, self.transDelegate)

        self.heightDelegate = SpinBoxDelegate(-30.0, 30.0)
        self.sampleTable.setItemDelegateForColumn(2, self.heightDelegate)

        self.phiDelegate = SpinBoxDelegate(-5.0, 5.0)
        self.sampleTable.setItemDelegateForColumn(3, self.phiDelegate)

        self.psiDelegate = SpinBoxDelegate(-5.0, 5.0)
        self.sampleTable.setItemDelegateForColumn(4, self.psiDelegate)

        self.fpDelegate = SpinBoxDelegate(1.0, 300.0)
        self.sampleTable.setItemDelegateForColumn(5, self.fpDelegate)

        self.resDelegate = SpinBoxDelegate(0.005, 0.15)
        self.sampleTable.setItemDelegateForColumn(6, self.resDelegate)

        self.coarseNoMDelegate = SpinBoxDelegate(-60, 100.0)
        self.sampleTable.setItemDelegateForColumn(7, self.coarseNoMDelegate)

        self.switchDelegate = SpinBoxDelegate(1.0, 6.0, True)
        self.sampleTable.setItemDelegateForColumn(8, self.switchDelegate)

        ##################################################################################################
        # tableModel = TableModel(sampleTable)
        self.sampleTable.setAlternatingRowColors(True)
        self.sampleTable.setModel(self.view.tableModel)
        self.sampleTable.resizeColumnsToContents()

        # Create buttons:
        self.addLayerButton = QtWidgets.QPushButton("Add sample")
        self.addLayerButton.clicked.connect(self.on_addLayer)
        self.removeLayerButton = QtWidgets.QPushButton("Remove Sample(s)")
        self.removeLayerButton.clicked.connect(self.on_removeLayer)

        self.hbox_layers = QtWidgets.QHBoxLayout()

        self.hbox_layers.addWidget(self.addLayerButton)
        self.hbox_layers.addWidget(self.removeLayerButton)
        self.hbox_layers.addStretch(1)
        self.vbox_samples = QtWidgets.QVBoxLayout()

        # checkbox to hide table
        self.b = QtWidgets.QCheckBox("Hide/Show Sample Table",self)
        self.b.stateChanged.connect(self.clickBox)
        mainLayout.addWidget(self.dataGroupBox)
        mainLayout.addWidget(self.sampleTableGroupBox)

        self.vbox_samples.addWidget(self.b)
        self.vbox_samples.addLayout(self.hbox_layers)
        self.vbox_samples.addWidget(self.sampleTable)
        sampleLayout.addLayout(self.vbox_samples)
        self.sampleTableGroupBox.setLayout(sampleLayout)
        self.setLayout(mainLayout)
        
        self.view.resizeColumnToContents(0)
        #self.view.resizeColumnToContents(2)
        self.view.header().resizeSection(2, 5)
        
        self.show()
        
###########  
        
    def onOpenFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"Open Script File...", "",\
                                                  "OpenGenie Files (*.gcl);;All Files (*);;Python Files (*.py)", options=options)

        try:
            with open(fileName) as f:
                self.fileEdit.setText(fileName)
                return fileName
        except IOError:
            print("Created new file " + fileName)
            self.fileEdit.setText(fileName)
            f = open(fileName, "w")
            f.close()

        # if fileName:
        #     self.fileEdit.setText(fileName)
        #     return fileName
        
    def onPrintTree(self):
        self.view.updateSummary()
        if os.path.isfile(self.fileEdit.text()):
            f = open(self.fileEdit.text(),"w+")
        else:
            f = self.onOpenFile()
            if os.path.isfile(self.fileEdit.text()):
                f = open(self.fileEdit.text(), "w+")
            else:
                return

        # NEED TO REVISIT THIS
        args = []
        for col in range(self.view.tableModel.columnCount(QModelIndex)):
            args.append(0)
            # if self.sampleTable.item(0,col).checkState()  == Qt.Checked:
            #     args.append(1)
            # else:
            #     args.append(0)
        f.write(NRActions.writeHeader(self.onPrintSamples(), args))


        for row in range(self.view.model.rowCount()):
            it = self.view.model.item(row)
            MyClass = getattr(importlib.import_module(myActions), it.text())
           # Instantiate the class (pass arguments to the constructor, if needed)
            tempAction = MyClass()
            tempAction.makeAction(it)
            # Check if sample entry exists for Action:
            if it.child(0, 0).text() == "Sample":
                sampleNumber = self.view.delegate.items.index(it.child(0, 1).text()) + 1
            else:
                sampleNumber = -1
            f.write(tempAction.stringLine(sampleNumber)+"\n")

        f.write(NRActions.writeFooter(self.onPrintSamples()))
        f.close()

    def onPrintSamples(self):
        samples = []
        #print(self.view.tableModel.getData())
        for row in range(self.view.tableModel.rowCount(QModelIndex)):
            # print(self.view.tableModel.getData()[row][0])
            #print(self.view.tableModel.headerData(0, Qt.Horizontal, Qt.DisplayRole))

            if self.view.tableModel.getData()[row][0] != "":
                sampleDict = {}
                for col in range(self.view.tableModel.columnCount(QModelIndex)):
                    sampleDict[self.view.tableModel.headerData(col, Qt.Horizontal, Qt.DisplayRole)] = self.view.tableModel.getData()[row][col]
                    # print(sampleDict)
                samples.append(sampleDict)
        return samples

   
    def clickBox(self, state):
        if state == QtCore.Qt.Checked:
            self.addLayerButton.setHidden(True)
            self.removeLayerButton.setHidden(True)
            self.sampleTable.setHidden(True)
        else:
            self.addLayerButton.setHidden(False)
            self.removeLayerButton.setHidden(False)
            self.sampleTable.setHidden(False)
    
    def on_addLayer(self):
        pass
        # data = self.view.tableModel.getData()
        # rowNo = len(data)
        # data.append(["S"+str(rowNo+1), "", "", "", "", "", "", "", ""])
        # self.view.tableModel = TableModel(data, self.view.headerLabels_sampTable)
        # self.sampleTable.setModel(self.view.tableModel)
        #
        # self.view.tableModel.rowsInserted.connect(self.view.delegate.updateCombo)


    def on_removeLayer(self):
        pass
        

class MyMainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        
        super(MyMainWindow, self).__init__(parent)
        self.form_widget = App(self) 
        self.setCentralWidget(self.form_widget)    
        
        openAct = QtWidgets.QAction(QtGui.QIcon('exit.png'), '&Open...', self)        
        openAct.setShortcut('Ctrl+O')
        openAct.setStatusTip('Open script')
        openAct.triggered.connect(self.openScript)

        saveAct = QtWidgets.QAction(QtGui.QIcon('exit.png'), '&Save as...', self)
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

        # Open default file
        fileName = "INTER_4Samples_2Contrasts_inject.json"
        self.form_widget.view.model.populate(fileName)

        with open(fileName) as json_file:
            data = json.load(json_file)
            """
            for row, samp in enumerate(data['Samples'], start=1):
                if len(samp):
                    for col in range(self.form_widget.sampleTable.columnCount()):
                        self.form_widget.sampleTable.item(row, col).setText(samp[col])
            """
        rows = self.form_widget.view.model.rowCount()
        for i in range(rows):
            if self.form_widget.view.model.item(i, 0).child(0, 0).text() == "Sample":
                self.form_widget.view.openPersistentEditor(self.form_widget.view.model.item(i, 0).child(0, 1).index())
            self.form_widget.view.showSummary(self.form_widget.view.model.index(i, 0))
        self.form_widget.view.resizeColumnToContents(0)
        self.form_widget.fileEdit.setText('runScriptTest2.gcl')
        ############################
        
    def openScript(self):
        print("Opening...")
        buttonReply = QMessageBox.question(self, 'MaxSkript', "All changes will be lost. Do you want to save?",\
                                           QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
        if buttonReply == QMessageBox.Yes:
            print('Yes clicked.')
            self.saveScript()
        if buttonReply == QMessageBox.No:
            print('No clicked.')
        if buttonReply == QMessageBox.Cancel:
            return
        
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open saved ScriptMaker state", "",\
                                                  "MaxScript Files (*.json);;All Files (*)", options=options)

        # delete all rows
        self.form_widget.view.model.removeRows(0, self.form_widget.view.model.rowCount())

        self.form_widget.view.model.populate(fileName)
        with open(fileName) as json_file:
            data = json.load(json_file)
            #print(len(data['Samples']))
            tableModel = TableModel(data['Samples'], self.form_widget.view.headerLabels_sampTable)
            self.form_widget.view.tableModel.layoutAboutToBeChanged.emit()
            self.form_widget.view.tableModel._data = data['Samples']
            self.form_widget.view.tableModel.layoutChanged.emit()

        rows = self.form_widget.view.model.rowCount()
        for i in range(rows):
            self.form_widget.view.showSummary(self.form_widget.view.model.index(i, 0))
        self.form_widget.parent().setWindowTitle("Ma_xSkript - " + fileName + "[*]")

    def saveScript(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"Save ScriptMaker state...", "",\
                                                  "Ma_xScript Files (*.json);;All Files (*)", options=options)
        if fileName:
            f = open(fileName, "w+")
        else:
            return

        outString = "{\"Samples\": ["
        ## get defined samples from table:
        data = self.form_widget.sampleTable.model().getData()

        for row in data:
            r = str([''.join(x) for x in row])
            r = str(r).replace("\'", "\"")
            outString += r + ",\n"
        outString = outString[:-2] + "],\n"

        outString += "\n\n\"Action\":[\n"
        for row in range(self.form_widget.view.model.invisibleRootItem().rowCount()):
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
        print("Saved.")



def main():
    app = QApplication([])
    app.aboutToQuit.connect(app.deleteLater)
    foo = MyMainWindow()
    foo.resize(700, 800)
    foo.setWindowTitle("Ma_xSkript [*]")
    # foo.setWindowFilePath("fiel C:/Users/ktd43279/Documents/GitHub/PyScriptMaker/ScriptMaker_v0p71.py")
    foo.setWindowIcon(QtGui.QIcon('squareCogs.gif'))

    foo.show()
    app.exec_()


if __name__ == '__main__':
    main()
