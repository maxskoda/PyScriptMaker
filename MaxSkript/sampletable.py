from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDoubleSpinBox, QSpinBox)


class SpinBoxDelegate(QtWidgets.QStyledItemDelegate):
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
            self.dataChanged.emit(index, index)#, [QtCore.Qt.DisplayRole])
            return True
        else:
            return False
        return QtCore.QAbstractTableModel.setData(self, index, value, role)# True

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
                self.view.update_summary()

    def update_model(self, newdata):
        self.beginResetModel()
        self._data = newdata
        self.view.update_summary()
        self.endResetModel()

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[section]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return str(section+1)
