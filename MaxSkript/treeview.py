from functools import partial

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut
import importlib

from MaxSkript.sampletable import TableModel
from MaxSkript.treeitems import MyStandardItemModel, ComboBoxDelegate, ProgressDelegate

myActions = "Actions.NRActions_Python"

NRActions = __import__('Actions.NRActions_Python', globals(), locals(), ['NRActions_Python'], 0)


class Tree(QtWidgets.QTreeView):
    def __init__(self, parent=None):
        super(Tree, self).__init__(parent)

        self.model = MyStandardItemModel()
        self.setModel(self.model)

        # DATA
        # sampleTable = np.array([["S12345", "11", "12", "13", "14"],
        #                         ["S2", "21", "22", "23", "24"],
        #                         ["S3", "31", "32", "33", "34"], ])

        self.sampleTable = [["S1", "100", "1", "1", "1", "1", "1", "1", "1"],
                            ["S2", "200", "2", "2", "2", "2", "2", "2", "2"],
                            ["S3", "300", "3", "3", "3", "3", "3", "3", "3"],
                            ["S4", "400", "4", "4", "4", "4", "4", "4", "4"],
                            ["", "", " ", " ", " ", " ", " ", " ", " "],
                            ["", "", " ", " ", " ", " ", " ", " ", " "],
                            ["", "", " ", " ", " ", " ", " ", " ", " "]]

        self.headerLabels_sampTable = ["Sample/Title", "Trans", "Height", "Phi Offset", \
                                       "Psi", "Footprint", "Resolution", "Coarse_noMirror", "Switch"]

        try:
            SampleClass = getattr(importlib.import_module(myActions), 'NRsample')
            # Instantiate the class (pass arguments to the constructor, if needed)
            NRSample = SampleClass()
            print([sample_attribute for sample_attribute in dir(NRSample) if '_' not in sample_attribute[0]])
        except AttributeError:
            print("NRsample class not found in myActions module.")

        self.tableModel = TableModel(self, self.sampleTable, self.headerLabels_sampTable)

        self.delegate = ComboBoxDelegate(self, self.sampleTable)
        self.setItemDelegateForColumn(1, self.delegate)
        self.tableModel.dataChanged.connect(self.delegate.updateCombo)
        self.tableModel.layoutChanged.connect(self.delegate.updateCombo)
        self.tableModel.dataChanged.connect(self.update_summary)
        self.model.dataChanged.connect(self.update_runtime)

        self.dur_delegate = ProgressDelegate(self)
        self.setItemDelegateForColumn(4, self.dur_delegate)

        # self.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)#CurrentChanged)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove | QtWidgets.QAbstractItemView.DragDrop)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)

        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.resizeColumnToContents(0)
        self.setAlternatingRowColors(True)
        font = QtGui.QFont("Verdana", 10)
        font.setWeight(QtGui.QFont.Bold)
        self.header().setFont(font)
        self.resize(self.sizeHint().height(), self.minimumHeight())

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_menu)

        self.collapsed.connect(self.show_summary)
        self.expanded.connect(self.remove_summary)

        self.shortcut = QShortcut(QKeySequence("Del"), self)
        self.shortcut.activated.connect(self.del_action)

        self.update_summary()

        # define shortcuts
        self.menu = QtWidgets.QMenu()
        self.sub_menu = QtWidgets.QMenu("Insert Action")
        self.menu.addMenu(self.sub_menu)
        # actions = NRActions.actions
        actions = [cls.__name__ for cls in NRActions.ScriptActionClass.ActionClass.__subclasses__()]
        for name in actions:
            shortcut = "Ctrl+" + name[0].lower()
            action = self.sub_menu.addAction(name)
            # action.setShortcut(QtGui.QKeySequence(shortcut))
            short = QtWidgets.QShortcut(QtGui.QKeySequence(shortcut), self)
            short.activated.connect(partial(self.menu_action, action))
            action.triggered.connect(partial(self.menu_action, action))

    def update_sample_table(self):
        self.tableModel.update_model(self.sampleTable)

    def update_runtime(self):
        try: ### it seems the first call finds noparent object!?
            # old_time = self.parent().parent().parent().runTime.text()
            # hmin = old_time.split('h ')
            # h = hmin[0]
            # mins = hmin[1].split('min')[0]
            # old_minutes = int(h)*60 + int(mins)

            self.totalTime = 0.0
            global myActions
            for row in range(self.model.rowCount()):
                try:
                    it = self.model.getRootItem(row, 0)
                    clName = it.text()
                    MyClass = getattr(importlib.import_module(myActions), clName)
                    # Instantiate the class (pass arguments to the constructor, if needed)
                    tempAction = MyClass()
                    tempAction.makeAction(it)
                    it.setToolTip(tempAction.toolTip())  #
                    self.model.item(row, 3).setText(str(row + 1))

                except AttributeError as err:
                    # logging.warning("makeAction method undefined in "+tempAction.__repr__)
                    print("makeAction method undefined in ", tempAction, err)
                try:
                    self.rtime = tempAction.calcTime(self.parent().parent().parent().instrumentSelector.currentText())
                    # if old_minutes > 0:
                    #     time_percent = float(self.rtime)/(old_minutes+float(self.rtime)) * 100
                    # else:
                    #     time_percent = 0
                    self.model.item(row, 4).setData(self.rtime, QtCore.Qt.UserRole + 1000)
                    # self.model.item(row, 4).setData("red", QtCore.Qt.BackgroundColorRole)
                    # self.model.item(row, 4).setText(str(self.rtime))
                    # print("Time: ", self.totalTime)
                    self.totalTime += self.rtime
                except AttributeError:
                    pass
            self.parent().parent().parent().runTime.setText("{:02d}h {:02d}min".format(int(divmod(self.totalTime, 60)[0]), int(divmod(self.totalTime, 60)[1])))
            # update window title to indicate unsaved changes:
            self.parent().parent().setWindowModified(True)
        except:
            pass

    def update_summary(self):
        # print(self.model.rowCount())
        self.update_runtime()
        for row in range(self.model.rowCount()):
            self.show_summary(self.model.index(row, 0))

    def show_summary(self, index):
        self.update_runtime()
        it = self.model.getRootItem(index.row(), index.column())
        global NRActions
        global myActions
        importlib.reload(NRActions)

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
            self.model.invisibleRootItem().child(index.row(), 1). \
                setForeground(QtGui.QColor(QtGui.QColor(colors[colorIndex])))

        self.model.invisibleRootItem().child(index.row(), 1).setText(tempAction.summary())
        self.resizeColumnToContents(1)
        try:
            self.rtime = tempAction.calcTime(self.parent().parent().parent().instrumentSelector.currentText())
            self.model.item(index.row(), 4).setData(self.rtime, QtCore.Qt.UserRole + 1000)
        except AttributeError:
            pass

        try:
            if tempAction.isValid()[0]:
                self.model.invisibleRootItem().child(index.row(), 2). \
                    setBackground(QtGui.QColor(QtGui.QColor("green")))
                item = self.model.getRootItem(index.row(), 2)
                item.setToolTip("")
                # self.update_runtime()
            else:
                self.model.invisibleRootItem().child(index.row(), 2). \
                    setBackground(QtGui.QColor(QtGui.QColor("red")))
                item = self.model.getRootItem(index.row(), 2)
                item.setToolTip(tempAction.isValid()[1])

        except AttributeError as err:
            print("isValid method undefined in ", tempAction)

        # return self.rtime, tempAction.summary()  # shortText
        # self.update_runtime()
        del tempAction

    def remove_summary(self, index):
        self.model.invisibleRootItem().child(index.row(), 1).setText("")

    def open_menu(self, position):
        # self.menu = QtWidgets.QMenu()
        index = self.indexAt(position)

        # self.sub_menu = QtWidgets.QMenu("Insert Action")
        # self.menu.addMenu(self.sub_menu)

        deleteAction = QtWidgets.QAction(QtGui.QIcon('exit.png'), '&Delete row(s)', )
        # deleteAction = self.menu.addAction("Delete Row(s)", self.del_action)
        deleteAction.setShortcut(QKeySequence("Del"))
        deleteAction.triggered.connect(self.del_action)
        self.menu.addAction(deleteAction)
        action = self.menu.exec_(self.viewport().mapToGlobal(position))

        if action == deleteAction:
            pass
            # for items in self.selectionModel().selectedRows():
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

    def menu_action(self, action):
        global myActions, countRate
        item2 = QtGui.QStandardItem("")
        item = QtGui.QStandardItem(action.text())
        itemCheck = QtGui.QStandardItem("")
        rowNumberItem = QtGui.QStandardItem("")
        durationItem = QtGui.QStandardItem(0)
        durationItem.setData(self.rtime, QtCore.Qt.UserRole + 1000)
        # override index temporarily test
        selection = self.selectedIndexes()
        if selection:
            index = self.selectedIndexes()[0]
            row = index.row()
        else:
            row = -1

        clName = item.text()
        MyClass = getattr(importlib.import_module(myActions), clName)
        # Instantiate the class (pass arguments to the constructor, if needed)
        actionItem = MyClass()

        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable \
                      & ~QtCore.Qt.ItemIsDropEnabled \
                      & ~QtCore.Qt.ItemIsDragEnabled)

        # need to echek how best to do this...
        # if 'set_countrate' in dir(actionItem):
        #     actionItem.set_countrate(countRate)

        if 'get_icon' in dir(actionItem):
            item.setIcon(QtGui.QIcon(actionItem.get_icon()))

        root = self.model.invisibleRootItem()
        root.insertRow(row + 1, [item, item2, itemCheck, rowNumberItem, durationItem])
        newRow = self.model.item(row + 1)
        for key in actionItem.__dict__:
            par = QtGui.QStandardItem(key)
            par.setFlags(newRow.flags() & QtCore.Qt.ItemIsEditable & ~QtCore.Qt.ItemIsDragEnabled)
            if isinstance(actionItem.__dict__[key], list):
                values = str(actionItem.__dict__[key]).strip('[]')
            else:
                values = str(actionItem.__dict__[key])

            val = QtGui.QStandardItem(values)
            newRow.appendRow([par, val])
            self.resizeColumnToContents(0)
        del actionItem

    def on_context_menu_factions(self, pos):
        self.menu.exec_(QtGui.QCursor.pos())

