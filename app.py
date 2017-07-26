__author__ = 'lijuk'


import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

from utils.graph_view import GraphView
from utils import node_browser


class AppWindow(QtGui.QMainWindow):

    on_browser_closed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        """
        initiator
        :param parent: parent window, if any
        :return: None
        """
        super(AppWindow, self).__init__(parent)
        self._graph = None
        self._attribute_editor = None
        self._init_ui()
        
    def _init_ui(self):
        """
        initialize ui
        :return: None
        """
        # window minimum size
        self.setMinimumSize(400, 240)

        # Central widget and layout
        self._app_widget = QtGui.QFrame()
        self.setCentralWidget(self._app_widget)
        self._app_layout = QtGui.QHBoxLayout(self._app_widget)

        # setup graph
        self._setup_graph()

        # setup attribute editor
        self._setup_attribute_editor()

    def _setup_graph(self):
        """
        Setup graph view
        :return:
        """
        # Setup Graph
        self._graph = GraphView(self)
        self._graph.selection_changed.connect(self.show_node_attributes)
        self._app_layout.addWidget(self._graph)

    def _setup_attribute_editor(self):
        """
        Setup attribute editor
        :return: None
        """
        # Setup Attribute Editor
        self._attribute_editor = QtGui.QFrame()
        attr_editor_layout = QtGui.QGridLayout()
        self._attr_group_box = QtGui.QGroupBox()
        self._attr_group_box.setTitle("Attributes")
        gbox_layout = QtGui.QVBoxLayout()
        self._attr_group_box.setLayout(gbox_layout)
        attr_editor_layout.addWidget(self._attr_group_box)
        self._attribute_editor.setLayout(attr_editor_layout)
        self._attribute_editor.setMinimumWidth(200)
        self._app_layout.addWidget(self._attribute_editor)

    def keyPressEvent(self, event):
        """
        Event to gather tab key press to open command browser
        :param event: keyboard events
        :return: None
        """
        if event.key() == QtCore.Qt.Key_Tab:
            self.open_node_browser()

        if event.key() == QtCore.Qt.Key_Escape:
            self.on_browser_closed.emit()

    def open_node_browser(self):
        """
        this opens node browser
        :return: None
        """
        pos = QtGui.QCursor.pos()

        browser_gui = node_browser.NodeBrowser(pos, self)
        browser_gui.node_browser_widget.returnPressed.connect(lambda: self.add_new_node(browser_gui))
        self.on_browser_closed.connect(browser_gui.close)
        browser_gui.show()

    def add_new_node(self, browser_gui):
        """
        This will add new node to the scene
        :param browser_gui: browser gui
        :return: None
        """
        node_name = browser_gui.node_browser_widget.text()
        module = browser_gui.get_node_module(node_name)
        if module:
            new_node = module.CustomNode(self._graph)
            self._graph.add_node(new_node)
        self.on_browser_closed.emit()


def run():
    app = QtGui.QApplication(sys.argv)
    ui = AppWindow()
    ui.show()
    sys.exit(app.exec_())
