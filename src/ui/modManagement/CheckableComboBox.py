from PySide2.QtCore import Qt, QModelIndex
from PySide2.QtWidgets import QComboBox, QAbstractItemView, QTableView, QStyledItemDelegate


class CheckableComboBox(QComboBox):
    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)

        self._changed = False
        self._clearItem = False

    def handleItemPressed(self, index: QModelIndex):
        if self._clearItem and index.row() == 0:
            self.clearChecks()
            return

        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)

        self._changed = True

    def setView(self, itemView: QAbstractItemView) -> None:
        super().setView(itemView)
        self.view().pressed.connect(self.handleItemPressed)

    def hidePopup(self):
        if not self._changed:
            super(CheckableComboBox, self).hidePopup()
        self._changed = False

    def clear(self) -> None:
        self._changed = False
        self._clearItem = False
        super().clear()

    def addClearItem(self, item):
        self.addItem(item)
        self._clearItem = True

    def getCheckedItems(self):
        checked_items = []
        for row in range((1 if self._clearItem else 0), self.model().rowCount()):
            item = self.model().item(row, 0)
            if item and item.checkState() == Qt.Checked:
                checked_items.append(item.text())

        return checked_items

    def clearChecks(self):
        for row in range((1 if self._clearItem else 0), self.model().rowCount()):
            self.model().item(row, 0).setCheckState(Qt.Unchecked)

        self.hidePopup()
        self.setCurrentIndex(0)


def generateModTagsFilter(parent=None):
    tagsCombo = CheckableComboBox(parent)

    view = QTableView(tagsCombo)
    view.verticalHeader().hide()
    view.horizontalHeader().hide()

    tagsCombo.setView(view)

    return tagsCombo
