import io
import traceback

from PySide2.QtCore import QObject
from PySide2.QtWidgets import QWidget, QScrollArea, QHBoxLayout, QVBoxLayout, QGroupBox, QPushButton, QFileDialog, QMessageBox, QInputDialog, QLineEdit

import src.logic.dd_stuff as dd_stuff
from src.ui.ModItem import ModItem
from src.ui.VDragWidget import VDragWidget
from src.ui.ModInfoTab import ModInfoTab
from src.logic.ModDB import ModDB


class ModTab(QWidget):
    def __init__(self):
        super().__init__()

        self.__initialize()

    def __initialize(self):
        everythingLayout = QVBoxLayout()

        # Mod OPs

        modsOpWidget = QWidget()
        modsOpLayout = QHBoxLayout()

        self.modInfoTab = ModInfoTab()

        activeScroll = QScrollArea(self)
        activeScroll.setWidgetResizable(True)
        self.activeModsWidget = VDragWidget()

        installedScroll = QScrollArea(self)
        installedScroll.setWidgetResizable(True)
        self.installedModsWidget = VDragWidget()

        self.refresh()

        installedScroll.setWidget(self.installedModsWidget)
        activeScroll.setWidget(self.activeModsWidget)

        self.installedModsWidget.orderChanged.connect(self._handleOrderChange)
        self.installedModsWidget.itemClicked.connect(self._handleItemClicked)
        self.activeModsWidget.orderChanged.connect(self._handleOrderChange)
        self.activeModsWidget.itemClicked.connect(self._handleItemClicked)

        modsOpLayout.addWidget(installedScroll)
        modsOpLayout.addWidget(activeScroll)
        modsOpLayout.addWidget(self.modInfoTab)

        modsOpWidget.setLayout(modsOpLayout)

        everythingLayout.addWidget(modsOpWidget)

        # Action Btns

        actionBtnsGroup = QGroupBox()
        actionBtnsLayout = QHBoxLayout()

        actionBtnsLayout.addStretch(0)

        btn = QPushButton("Save", actionBtnsGroup)
        btn.clicked.connect(self._saveChanges)
        actionBtnsLayout.addWidget(btn)

        btn = QPushButton("Export", actionBtnsGroup)
        btn.clicked.connect(self._exportModlist)
        actionBtnsLayout.addWidget(btn)

        btn = QPushButton("Import Local", actionBtnsGroup)
        btn.clicked.connect(self._importLocalModlist)
        actionBtnsLayout.addWidget(btn)

        btn = QPushButton("Import URL", actionBtnsGroup)
        btn.clicked.connect(self._importUrlModlist)
        actionBtnsLayout.addWidget(btn)

        btn = QPushButton("Reload", actionBtnsGroup)
        btn.clicked.connect(self.reload)
        actionBtnsLayout.addWidget(btn)

        actionBtnsGroup.setLayout(actionBtnsLayout)

        everythingLayout.addWidget(actionBtnsGroup)

        self.setLayout(everythingLayout)

    def reload(self):
        ModDB.reload()
        self.refresh()

    def refresh(self):
        self.installedModsWidget.clear()
        self.activeModsWidget.clear()

        # installedMods, uninstalledMods, disabledMods, enabledMods = ModDB.dump()

        for mod in ModDB.disabledMods:
            self.installedModsWidget.add_item(ModItem(mod))
        for mod in ModDB.enabledMods:
            self.activeModsWidget.add_item(ModItem(mod))

        # self.installedModsWidget.adjustSize()
        # self.activeModsWidget.adjustSize()

    def _handleOrderChange(self, container, moved):
        print(container, moved)
        # self.installedModsWidget.adjustSize()
        # self.activeModsWidget.adjustSize()

    def _handleItemClicked(self, modItem):
        print(modItem.mod.toString())
        self.modInfoTab.loadMod(modItem.mod)

    # Btn event functions
    def _saveChanges(self):
        print("Save changes")
        try:
            dd_stuff.writeModsAndSave(self.activeModsWidget.getItemsData())
            self.reload()
            QMessageBox(QMessageBox.Icon.Information, "Success", "Successfully enabled the mods").exec_()
        except FileNotFoundError:
            QMessageBox(QMessageBox.Icon.Critical, "Error", "Decrypted game file is missing").exec_()
        except io.UnsupportedOperation:
            QMessageBox(QMessageBox.Icon.Critical, "Error", "Could not read or write decrypted game file").exec_()
        except Exception as err:
            QMessageBox(QMessageBox.Icon.Critical, "Error", str(err)).exec_()

    def _exportModlist(self):
        print("Export modlist")
        path, _ = QFileDialog.getSaveFileName(self, QObject.tr(self, "File to export"), "./modlists/modlist.csv", QObject.tr(self, "CSV files (*.csv)"))

        if path:
            dd_stuff.exportModlist(path, self.activeModsWidget.getItemsData())

            QMessageBox(QMessageBox.Icon.NoIcon, "Success", f"Successfully exported modlist to:\n{path}").exec_()

    def _importLocalModlist(self):
        print("Import modlist")
        path, _ = QFileDialog.getOpenFileName(self, QObject.tr(self, "Modlist to import"), "./modlists", QObject.tr(self, "CSV files (*.csv)"))

        if path:
            ModDB.loadLocalModlist(path)
            self.refresh()

            QMessageBox(QMessageBox.Icon.NoIcon, "Success", f"Successfully imported modlist from:\n{path}").exec_()

    def _importUrlModlist(self):
        text, ok = QInputDialog.getText(self, "Import modlist URL", "URL:", QLineEdit.Normal)
        print(text, ok)
        if ok:
            try:
                ModDB.loadURLModlist(text)
                self.refresh()
            except Exception as e:
                traceback.print_exc()
                QMessageBox(QMessageBox.Icon.Critical, "Error", f"Failed to load the modlist from the URL:\n{e}").exec_()
