from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from .q_llm_dialog import QLLMDialog
import os

class QLLM:
    def __init__(self, iface):
        # Store the QGIS interface
        self.iface = iface
        self.action = None
        self.dialog = None

    def initGui(self):
        # Initialize the GUI elements: toolbar icon and plugin menu
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
        self.action = QAction(QIcon(icon_path), "Q-LLM", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Q-LLM", self.action)

    def unload(self):
        # Remove the plugin from the toolbar and menu when unloaded
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu("&Q-LLM", self.action)

    def run(self):
        # Show the plugin dialog window
        if not self.dialog:
            self.dialog = QLLMDialog()
        self.dialog.show()
