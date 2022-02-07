import importlib

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import (QSortFilterProxyModel, Qt)
import json
import os.path

from MaxSkript.sampletable import TableModel

HORIZONTAL_HEADERS = ("Action", "Parameters", "Ok", "Row", "Action duration / min")

myActions = "Actions.NRActions_Python"  # "NRActions_Python" #"MuonActions"

NRActions = __import__('Actions.NRActions_Python', globals(), locals(), ['NRActions_Python'], 0)


class MyStandardItemModel(QtGui.QStandardItemModel):
    def __init__(self, parent=None):
        super(MyStandardItemModel, self).__init__(parent)

    def canDropMimeData(self, data, action, row, column, parent):
        print('can drop called on')
        print(parent.data())
        print("PARENT: ", parent.parent())
        return True

    def dropEvent(self, e):
        print("Hallo")

    # def dropMimeData(self, data, action, row, column, parent):
    #     parent_name = parent.data()
    #     node_name = data.text()
    #     print("Dropped {} onto {}".format(node_name, parent_name))
    #     return True

    def flags(self, index):
        defaultFlags = QtCore.Qt.ItemIsEnabled | super(MyStandardItemModel, self).flags(index)

        if index.column() == 1:
            return defaultFlags | QtCore.Qt.ItemIsEditable

        if index.isValid():
            return defaultFlags | Qt.ItemIsDragEnabled  # | Qt.ItemIsDropEnabled
        else:
            return defaultFlags | Qt.ItemIsDropEnabled

    def itemList(self, parent=QtCore.QModelIndex()):
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
        return self.item(row, col).text()

    def getRootItem(self, row, col):
        return self.item(row, col)

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
                        MyClass = getattr(importlib.import_module(myActions), key)
                        # Instantiate the class (pass arguments to the constructor, if needed)
                        actionItem = MyClass()
                        item2 = QtGui.QStandardItem("")
                        item = QtGui.QStandardItem(key)
                        itemCheck = QtGui.QStandardItem("")
                        lastItem = QtGui.QStandardItem("")
                        durationItem = QtGui.QStandardItem("")
                        durationItem.setData(0, QtCore.Qt.UserRole + 1000)

                        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable
                                      & ~QtCore.Qt.ItemIsDropEnabled
                                      & ~QtCore.Qt.ItemIsDragEnabled)
                        itemCheck.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable
                                           & ~QtCore.Qt.ItemIsDropEnabled
                                           & ~QtCore.Qt.ItemIsDragEnabled)
                        lastItem.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable
                                          & ~QtCore.Qt.ItemIsDropEnabled
                                          & ~QtCore.Qt.ItemIsDragEnabled)
                        durationItem.setFlags(item.flags() & QtCore.Qt.ItemIsEditable
                                              & ~QtCore.Qt.ItemIsDropEnabled
                                              & ~QtCore.Qt.ItemIsDragEnabled)
                    if 'get_icon' in dir(actionItem):
                        scriptDir = os.path.dirname(os.path.realpath(__file__))
                        ico = actionItem.get_icon()
                        icon_path = scriptDir + os.path.sep + 'Icons' + os.path.sep + ico
                        print(icon_path)
                        item.setIcon(QtGui.QIcon(icon_path))
                    parentItem.appendRow([item, item2, itemCheck, lastItem, durationItem])

                    for it in p.get(next(iter(p))):
                        par = QtGui.QStandardItem(it.get('label'))
                        par.setFlags(item.flags() & QtCore.Qt.ItemIsEditable & ~QtCore.Qt.ItemIsDragEnabled)
                        if isinstance(it.get('value'), list):
                            # print(it.get('value'))
                            li = [float(i) if '.' in i else i for i in it.get('value')]
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
            if item[0] != "":
                list.append(item[0])
        self.items = list

    def commit_editor(self):
        editor = self.sender()
        self.commitData.emit(editor)

    def createEditor(self, parent, option, index):
        # self.updateCombo(index)
        row = index.row()
        hasSample = (self.treeView.model.item(index.parent().row(), 0).child(0, 0).text() == "Sample")
        if row == 0 and index.parent().row() >= 0 and hasSample:  # not the very first row
            editor = QtWidgets.QComboBox(parent)
            self.editor[index] = editor
            ComboBoxDelegate.instances.append(editor)
            editor.addItems(self.items)
            editor.currentTextChanged.connect(self.commit_editor)
            editor.highlighted.connect(self.commit_editor)
            return editor
        else:
            editor = QtWidgets.QStyledItemDelegate.createEditor(self, parent, option, index)
            # editor.model().select()
            return editor

    def paint(self, painter, option, index):
        # self.updateCombo(index)
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
                    # print("oops")
                    indToDelete.append(ind)
                else:
                    pass
                    # print(currentIndex)
            # print(indToDelete)
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


class ProgressDelegate(QtWidgets.QStyledItemDelegate):

    def paint(self, painter, option, index):
        progress = index.data(QtCore.Qt.UserRole + 1000)
        if not progress:
            progress = 0
        opt = QtWidgets.QStyleOptionProgressBar()
        opt.rect = option.rect
        opt.minimum = 0
        opt.maximum = 100
        opt.progress = progress
        opt.text = "{}".format(progress)
        opt.textVisible = True
        QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.CE_ProgressBar, opt, painter)
