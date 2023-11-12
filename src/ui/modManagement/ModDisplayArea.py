from PySide2.QtWidgets import QWidget, QVBoxLayout
from PySide2.QtCore import Signal, Qt
from PySide2.QtGui import QDragEnterEvent, QDropEvent
from typing import List, Callable, Any

from ui.modManagement.ModItem import ModItem
from logic.Mod import Mod

import re


class ModDisplayArea(QWidget):
    orderChanged = Signal((object, bool))
    itemClicked = Signal(object)

    def __init__(self):
        super().__init__()

        self.setAcceptDrops(True)
        self.blayout = QVBoxLayout()
        self.blayout.setSpacing(10)
        self.blayout.setAlignment(Qt.AlignTop)
        self.setLayout(self.blayout)

    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        e.accept()

    def dropEvent(self, e: QDropEvent) -> None:
        pos = e.pos()
        widget = e.source()

        compensate = 0
        moved = widget.parent() != self
        for n in range(self.blayout.count()):
            w = self.blayout.itemAt(n).widget()

            # If this is inside we want to "compensate" by ignoring the next gap and offsetting the sweet spot
            if w == widget:
                compensate = w.size().height()

            drop_here = pos.y() < w.y() + w.size().height() // 2 + compensate

            if drop_here:
                self.blayout.insertWidget(n, widget)
                self.orderChanged.emit(widget, moved)
                break
        else:
            self.blayout.insertWidget(self.blayout.count(), widget)
            self.orderChanged.emit(widget, moved)

        e.accept()

    def add_item(self, item: ModItem) -> None:
        self.blayout.addWidget(item)
        item.clicked.connect(self.itemClicked.emit)

    def clear(self) -> None:
        for i in reversed(range(self.blayout.count())):
            self.blayout.removeWidget(self.blayout.takeAt(i).widget())

    def getItemsData(self) -> List[Mod]:
        data = []
        for i in range(self.blayout.count()):
            w = self.blayout.itemAt(i).widget()
            data.append(w.getData())
        return data

    def getWidgets(self) -> List[ModItem]:
        widgets = []
        for i in range(self.blayout.count()):
            widgets.append(self.blayout.itemAt(i).widget())
        return widgets

    def sort(self, sort_key: Callable[[ModItem], Any], reverse: bool = False) -> None:
        widgets = self.getWidgets()
        widgets.sort(key=sort_key, reverse=reverse)

        self.clear()
        for widget in widgets:
            self.blayout.addWidget(widget)
