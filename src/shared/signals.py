from PySide2.QtCore import QObject, Signal


class _SignalManager(QObject):
    s_changed_settings = Signal()
    s_loading_mods = Signal(str)
    s_dlcs_reloaded = Signal()
    s_set_name_filter = Signal(str)


signal_manager = _SignalManager()
