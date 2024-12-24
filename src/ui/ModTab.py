import io
import os
import traceback
import re

from PySide2.QtCore import QObject, Qt
from PySide2.QtWidgets import QWidget, QScrollArea, QHBoxLayout, QVBoxLayout, QGroupBox, QPushButton, QFileDialog, \
    QMessageBox, QInputDialog, QLineEdit, QComboBox, QCheckBox, QAbstractItemView, QTableView
from PySide2.QtGui import QStandardItemModel
from typing import List

import logic.dd_stuff as dd_stuff
from ui.modManagement.ModItem import ModItem
from ui.modManagement.ModDisplayArea import ModDisplayArea
from ui.modInfo.ModInfoPanel import ModInfoScreen
from logic.ModDB import ModDB
from constants.paths import *
from ui.modManagement.CheckableComboBox import generateModTagsFilter
from ui.popups.LoadingModsDialog import LoadingModsDialog
from shared.logger import logger
from ui.threads.ModLoadingThread import ModLoadingThread
from shared.signals import signal_manager


class SortOptions:
    NONE = "*Sort*"
    ALPHABETICAL = "Name"
    ID = "ID"

    ALL = [NONE, ALPHABETICAL, ID]


class ModTab(QWidget):
    def __init__(self):
        super().__init__()

        self.__initialize()

    def __initialize(self):
        self.modItems: List[ModItem] = []

        everythingLayout = QVBoxLayout()

        # List options

        modListOptionsGroup = QGroupBox()
        modListOptionsLayout = QHBoxLayout()

        self.searchBar = QLineEdit(modListOptionsGroup)
        self.searchBar.setPlaceholderText("Search")
        self.searchBar.setMaximumWidth(150)
        modListOptionsLayout.addWidget(self.searchBar)

        self.tagsCombo = generateModTagsFilter(modListOptionsGroup)
        modListOptionsLayout.addWidget(self.tagsCombo)
        self.reloadModTagsFilter()

        self.sortCombo = QComboBox(modListOptionsGroup)
        self.sortCombo.addItems(SortOptions.ALL)
        modListOptionsLayout.addWidget(self.sortCombo)

        self.sortReverseToggle = QCheckBox("Desc", modListOptionsGroup)
        modListOptionsLayout.addWidget(self.sortReverseToggle)

        btn = QPushButton("Apply", modListOptionsGroup)
        btn.clicked.connect(self._applyModListOptions)
        modListOptionsLayout.addWidget(btn)

        btn = QPushButton("Reset", modListOptionsGroup)
        btn.clicked.connect(self._resetModListOptions)
        modListOptionsLayout.addWidget(btn)

        modListOptionsLayout.addStretch(0)
        modListOptionsGroup.setLayout(modListOptionsLayout)

        signal_manager.s_set_name_filter.connect(self.filterByName)

        everythingLayout.addWidget(modListOptionsGroup)

        # Mod OPs

        modsOpWidget = QWidget()
        modsOpLayout = QHBoxLayout()

        self.modInfoTab = ModInfoScreen()
        signal_manager.s_dlcs_reloaded.connect(self.modInfoTab.reloadMod)

        disabledScroll = QScrollArea(self)
        disabledScroll.setWidgetResizable(True)
        self.disabledModsWidget = ModDisplayArea()

        enabledScroll = QScrollArea(self)
        enabledScroll.setWidgetResizable(True)
        self.enabledModsWidget = ModDisplayArea()

        self.loading_mods_dialog = LoadingModsDialog()
        signal_manager.s_loading_mods.connect(self.loading_mods_dialog.update_status)

        self.mod_loading_thread = ModLoadingThread()
        self.mod_loading_thread.mod_loading_finished.connect(self._reload)
        # self.reload()

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

    def reload(self) -> None:
        logger.debug("Reloading mod tab")
        self.loading_mods_dialog.show()
        if self.mod_loading_thread.isFinished():
            self.mod_loading_thread = ModLoadingThread()
            self.mod_loading_thread.mod_loading_finished.connect(self._reload)
            self.mod_loading_thread.start()
        elif not self.mod_loading_thread.isRunning():
            self.mod_loading_thread.start()

    def _reload(self) -> None:
        logger.debug("Real reloading mod tab")
        for modItem in self.modItems:
            modItem.deleteLater()
        self.modItems.clear()

        for mod in ModDB.allMods:
            self.modItems.append(ModItem(mod))

        self.reloadModTagsFilter()
        self.refresh()

        self.modInfoTab.clean()

        self.loading_mods_dialog.close()

    def refresh(self) -> None:
        self.disabledModsWidget.clear()
        self.enabledModsWidget.clear()

        for modItem in self.modItems:
            if modItem.mod.active:
                self.enabledModsWidget.add_item(modItem)
            else:
                self.disabledModsWidget.add_item(modItem)

    def reloadModTagsFilter(self):
        self.tagsCombo.clear()

        self.tagsCombo.addClearItem("*Tags*")
        self.tagsCombo.addItems(ModDB.getAllTags())
        self.tagsCombo.clearChecks()

        self.tagsCombo.view().resizeColumnsToContents()
        self.tagsCombo.view().setFixedWidth(self.tagsCombo.view().columnWidth(0))

    # Might want to change order in ModDB too, otherwise it is changed only in the ui
    def _handleOrderChange(self, widget: ModItem, index: int, moved: bool) -> None:
        if self.disabledModsWidget == widget.parent():
            column = 'disabled'
        elif self.enabledModsWidget == widget.parent():
            column = 'enabled'
        else:
            column = 'unknown'

        logger.debug(f"Moved to {column} column at index {index}. {'Changed' if moved else 'Unchanged'} column.")
        ModDB.moveMod(widget.mod.id, column, moved, index)
        self.modInfoTab.reloadMod()

    def _handleItemClicked(self, modItem: ModItem) -> None:
        logger.debug(f"Clicked {modItem.mod.toString()}")
        self.modInfoTab.loadMod(modItem.mod)

    # Btn event functions
    def _startGame(self) -> None:
        logger.debug("Start game")
        res = QMessageBox.question(self, "Launch game", "Are you sure?", QMessageBox.Yes | QMessageBox.No)
        if res == QMessageBox.Yes:
            if "GAME_FOLDER" in os.environ and os.path.exists(f'{os.environ["GAME_FOLDER"]}/_windows/Darkest.exe'):
                logger.info("Starting game")
                os.chdir(os.environ["GAME_FOLDER"])
                os.popen(f'{os.environ["GAME_FOLDER"]}/_windows/Darkest.exe')
                os.chdir(os.environ["APP_PATH"])
                self.window().close()
            else:
                logger.error("Path error")

    def _saveChanges(self) -> None:
        logger.debug("Save mod changes")
        try:
            dd_stuff.writeModsAndSave(self.enabledModsWidget.getItemsData())
            ModDB.reload()
            self.reload()
            QMessageBox(QMessageBox.Icon.Information, "Success", "Successfully enabled the mods").exec_()
        except FileNotFoundError:
            QMessageBox(QMessageBox.Icon.Critical, "Error", "Decrypted game file is missing").exec_()
        except io.UnsupportedOperation:
            QMessageBox(QMessageBox.Icon.Critical, "Error", "Could not read or write decrypted game file").exec_()
        except Exception as err:
            QMessageBox(QMessageBox.Icon.Critical, "Error", str(err)).exec_()

    def _exportModlist(self) -> None:
        logger.debug("Export modlist")
        path, _ = QFileDialog.getSaveFileName(self, QObject.tr(self, "File to export"),
                                              f"{MODLISTS_FOLDER}/modlist.csv", QObject.tr(self, "CSV files (*.csv)"))

        if path:
            dd_stuff.exportModlist(path, self.enabledModsWidget.getItemsData())

            QMessageBox(QMessageBox.Icon.NoIcon, "Success", f"Successfully exported modlist to:\n{path}").exec_()

    def _importCsvModlist(self) -> None:
        logger.debug("Import csv modlist")
        path, _ = QFileDialog.getOpenFileName(self, QObject.tr(self, "Modlist to import"), MODLISTS_FOLDER,
                                              QObject.tr(self, "CSV files (*.csv)"))

        if path:
            ModDB.loadCsvModlist(path)
            self.reload()

            QMessageBox(QMessageBox.Icon.NoIcon, "Success", f"Successfully imported modlist from:\n{path}").exec_()

    def _importUrlModlist(self) -> None:
        logger.debug("Import url modlist")
        text, ok = QInputDialog.getText(self, "Import modlist URL", "URL:", QLineEdit.Normal)
        logger.debug(f"Url: {text}")
        if ok:
            try:
                ModDB.loadURLModlist(text)
                self.reload()
            except Exception as e:
                traceback.print_exc()
                QMessageBox(QMessageBox.Icon.Critical, "Error",
                            f"Failed to load the modlist from the URL:\n{e}").exec_()

    def filterByName(self, name: str) -> None:
        self._resetModListOptions()
        self.searchBar.setText(name)
        self._applyModListOptions()

    def _applyModListOptions(self) -> None:
        self._applyFilterOptions()
        self._applySortOptions()

    def _applySortOptions(self) -> None:
        sortBy = self.sortCombo.currentText()
        reverse = self.sortReverseToggle.isChecked()

        if sortBy == SortOptions.NONE:
            self.disabledModsWidget.sort(lambda modItem: modItem.filtered)
            return
        elif sortBy == SortOptions.ALPHABETICAL:
            self.disabledModsWidget.sort(lambda modItem: (modItem.filtered if not reverse else not modItem.filtered,
                                                          re.sub("^\s+", "", modItem.mod.name.lower())),
                                         reverse)
            return
        elif sortBy == SortOptions.ID:
            self.disabledModsWidget.sort(lambda modItem: (modItem.filtered, modItem.mod.id), reverse)
            return

    def _applyFilterOptions(self) -> None:
        searchText = self.searchBar.text().lower()
        tags = self.tagsCombo.getCheckedItems()

        for modItem in self.disabledModsWidget.getWidgets():
            if (searchText and not re.search(searchText,  modItem.mod.name.lower())) or \
                    (tags and not any(tag in modItem.mod.tags for tag in tags)):
                modItem.setFiltered(True)
            else:
                modItem.setFiltered(False)

        for modItem in self.enabledModsWidget.getWidgets():
            if searchText and not re.search(searchText,  modItem.mod.name.lower()) or \
                    (tags and not any(tag in modItem.mod.tags for tag in tags)):
                modItem.setFiltered(True)
            else:
                modItem.setFiltered(False)

    def _resetModListOptions(self) -> None:
        self.sortCombo.setCurrentIndex(0)
        self.sortReverseToggle.setCheckState(Qt.Unchecked)
        self.searchBar.clear()
        self.tagsCombo.clearChecks()

        self._applyModListOptions()
