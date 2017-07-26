__author__ = 'lijuk'


from PyQt4 import QtGui
from PyQt4 import QtCore

from utils import node_finder


class NodeBrowser(QtGui.QWidget):

    def __init__(self, pos, parent=None):
        super(NodeBrowser, self).__init__(parent)
        self.resize(243, 26)
        self.move(self.parent().mapFromGlobal(QtGui.QCursor.pos()))
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        # layout
        self._layout = QtGui.QGridLayout()
        self._layout.setSpacing(0)
        self._layout.setMargin(0)
        # line edit
        self._node_browser_widget = QtGui.QLineEdit(self)
        self._node_browser_widget.setStyleSheet(self._style_sheet)
        self._node_browser_widget.setFocus(True)
        self._layout.addWidget(self._node_browser_widget)
        # set auto-completer
        self._node_dict = node_finder.get_node_list()
        self._completer = QtGui.QCompleter(self._node_dict.keys())
        self._node_browser_widget.setCompleter(self._completer)

        self.setLayout(self._layout)

    @property
    def node_browser_widget(self):
        return self._node_browser_widget

    @property
    def _style_sheet(self):
        style = """ QLineEdit:!focus
                    {
                      border: 2px solid grey;
                      background: transparent;
                      color: rgb(220, 220, 220);
                      border-radius: 4px;
                      font-size: 20px;
                      height: 60px;
                    }
                    QLineEdit:focus
                    {
                      border: 2px solid grey;
                      background: transparent;
                      color: rgb(220, 220, 220);
                      border-radius: 4px;
                      height: 60px;
                      font-size: 20px;
                    }
                """
        return  style

    def get_node_module(self, node):
        """
        Get node module from node name
        :param node: node name
        :return: str
        """
        module_path = "nodes.{0}_node".format(node)
        try:
            node_module = __import__(module_path,  globals(), locals(), ['object'])
        except ImportError:
            print "No node named {0} exists".format(node)
            return False
        return node_module





if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ui = NodeBrowser()
    ui.show()
    sys.exit(app.exec_())