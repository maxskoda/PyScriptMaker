from PyQt5.QtCore import QMimeData
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5 import QtCore, QtWidgets



class SceneTreeModel(QStandardItemModel):

    def mimeData(self, indexes):

        name = indexes[0].data()
        print('called mimeData on ' + name)
        mimedata = QMimeData()
        mimedata.setText(name)
        return mimedata

    def supportedDropActions(self):
        return QtCore.Qt.MoveAction

    def canDropMimeData(self, data, action, row, column, parent):
        print('can drop called on')
        print(parent.data())
        return True

    def dropMimeData(self, data, action, row, column, parent):
        parent_name = parent.data()
        node_name = data.text()
        print("Dropped {} onto {}".format(node_name, parent_name))
        return True

def give_model():
    model = SceneTreeModel()
    # create a tree item
    item1 = QStandardItem('item1')
    item2 = QStandardItem('item2')
    item3 = QStandardItem('item3')

    model.invisibleRootItem().appendRow(item1)
    item1.appendRow(item2)
    model.invisibleRootItem().appendRow(item3)

    return model

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(200, 400)
        MainWindow.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))

        self.treeView = QtWidgets.QTreeView(MainWindow)
        self.treeView.setRootIsDecorated(False)
        self.treeView.setObjectName("treeView")
        self.treeView.header().setVisible(False)

        MainWindow.setCentralWidget(self.treeView)

        self.treeView.setModel(give_model())
        self.treeView.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.treeView.expandAll()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())