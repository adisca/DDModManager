import io
import os
import traceback

from PySide2.QtCore import QObject
from PySide2.QtWidgets import QWidget, QScrollArea, QHBoxLayout, QVBoxLayout, QGroupBox, QPushButton, QFileDialog, \
    QMessageBox, QInputDialog, QLineEdit

import logic.dd_stuff as dd_stuff
from ui.modManagement.ModItem import ModItem
from ui.modManagement.ModDisplayArea import ModDisplayArea
from ui.modInfo.ModInfoPanel import ModInfoScreen
from logic.ModDB import ModDB
from constants.paths import *


class ModTab(QWidget):
    def __init__(self):
        super().__init__()

        self.__initialize()

    def __initialize(self):
        everythingLayout = QVBoxLayout()

        # Mod OPs

        modsOpWidget = QWidget()
        modsOpLayout = QHBoxLayout()

        self.modInfoTab = ModInfoScreen()

        disabledScroll = QScrollArea(self)
        disabledScroll.setWidgetResizable(True)
        self.disabledModsWidget = ModDisplayArea()

        enabledScroll = QScrollArea(self)
        enabledScroll.setWidgetResizable(True)
        self.enabledModsWidget = ModDisplayArea()

        self.refresh()

        disabledScroll.setWidget(self.disabledModsWidget)
        enabledScroll.setWidget(self.enabledModsWidget)

        self.disabledModsWidget.orderChanged.connect(self._handleOrderChange)
        self.disabledModsWidget.itemClicked.connect(self._handleItemClicked)
        self.enabledModsWidget.orderChanged.connect(self._handleOrderChange)
        self.enabledModsWidget.itemClicked.connect(self._handleItemClicked)

        modsOpLayout.addWidget(disabledScroll)
        modsOpLayout.addWidget(enabledScroll)
        modsOpLayout.addWidget(self.modInfoTab)

        modsOpWidget.setLayout(modsOpLayout)

        everythingLayout.addWidget(modsOpWidget)

        # Action Btns

        actionBtnsGroup = QGroupBox()
        actionBtnsLayout = QHBoxLayout()

        actionBtnsLayout.addStretch(0)

        btn = QPushButton("Play", actionBtnsGroup)
        btn.clicked.connect(self._startGame)
        actionBtnsLayout.addWidget(btn)

        btn = QPushButton("Save", actionBtnsGroup)
        btn.clicked.connect(self._saveChanges)
        actionBtnsLayout.addWidget(btn)

        btn = QPushButton("Export", actionBtnsGroup)
        btn.clicked.connect(self._exportModlist)
        actionBtnsLayout.addWidget(btn)

        btn = QPushButton("Import CSV", actionBtnsGroup)
        btn.clicked.connect(self._importCsvModlist)
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
        self.disabledModsWidget.clear()
        self.enabledModsWidget.clear()

        for mod in ModDB.disabledMods:
            self.disabledModsWidget.add_item(ModItem(mod))
        for mod in ModDB.enabledMods:
            self.enabledModsWidget.add_item(ModItem(mod))

    # Might want to change order in ModDB too, otherwise it is changed only in the ui
    def _handleOrderChange(self, container, moved):
        if self.disabledModsWidget == container:
            print(f"Moved to disabled column. {'Changed' if moved else 'Unchanged'} column.")
        elif self.enabledModsWidget == container:
            print(f"Moved to enabled column. {'Changed' if moved else 'Unchanged'} column.")
        else:
            print("Unrecognised column.")

    def _handleItemClicked(self, modItem):
        print(modItem.mod.toString())
        self.modInfoTab.loadMod(modItem.mod)

    # Btn event functions
    def _startGame(self):
        if "GAME_FOLDER" in os.environ and os.path.exists(f'{os.environ["GAME_FOLDER"]}/_windows/Darkest.exe'):
            print("Starting game")
            os.chdir(os.environ["GAME_FOLDER"])
            os.popen(f'{os.environ["GAME_FOLDER"]}/_windows/Darkest.exe')
            os.chdir(os.environ["APP_PATH"])
            self.window().close()

    def _saveChanges(self):
        print("Save changes")
        try:
            dd_stuff.writeModsAndSave(self.enabledModsWidget.getItemsData())
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
        path, _ = QFileDialog.getSaveFileName(self, QObject.tr(self, "File to export"),
                                              f"{MODLISTS_FOLDER}/modlist.csv", QObject.tr(self, "CSV files (*.csv)"))

        if path:
            dd_stuff.exportModlist(path, self.enabledModsWidget.getItemsData())

            QMessageBox(QMessageBox.Icon.NoIcon, "Success", f"Successfully exported modlist to:\n{path}").exec_()

    def _importCsvModlist(self):
        print("Import modlist")
        path, _ = QFileDialog.getOpenFileName(self, QObject.tr(self, "Modlist to import"), MODLISTS_FOLDER,
                                              QObject.tr(self, "CSV files (*.csv)"))

        if path:
            ModDB.loadCsvModlist(path)
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
                QMessageBox(QMessageBox.Icon.Critical, "Error",
                            f"Failed to load the modlist from the URL:\n{e}").exec_()
