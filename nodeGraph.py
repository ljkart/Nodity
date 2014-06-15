__author__ = 'liju.kunnummal'
import sys

from PyQt4 import QtGui
from PyQt4 import QtCore

from lib import nodityScene
from lib import nodityView
from lib import nodityCustomWidgets
from lib import nodityOps

SIZE = (800, 800)
POS = (100, 100)


class MyGraphicsWindow(QtGui.QWidget):

    def __init__(self):
        super(MyGraphicsWindow, self).__init__()

        # layout
        self.HB_Layout = QtGui.QHBoxLayout(self)
        self.setGeometry(POS[0], POS[1], SIZE[0], SIZE[1])
        self.setWindowTitle("Nodity")

        # View
        self.view = nodityView.MyView(self)
        self.view.connectNodeList.connect(self.openNodeListBox)
        #
        # SceneView
        self.scene = nodityScene.MyScene()
        #
        self.view.setScene(self.scene)
        #
        # Attach Node
        self.HB_Layout.addWidget(self.view)

        self.nodeListBox = None  # Node list box

        # Collect all nodes
        self.allOperatorNodes = []


    def openNodeListBox(self, stat):
        """
        This will open node list menu
        :return: none
        """
        if stat == "open":
            self.nodeListBox = nodityCustomWidgets.NodeListWindow(QtGui.QCursor.pos(), SIZE)
            self.nodeListBox.stat = 'open'
            self.nodeListBox.nodeListLE.returnPressed.connect(self.addNode)
            self.nodeListBox.show()

    def addNode(self):
        """
        Add node to the scene
        :return: none
        """
        askedNode = str(self.nodeListBox.nodeListLE.text())
        print " Creating node ", askedNode
        if not askedNode in nodityOps.NODE_LIST:
            print " %s : node exists " % askedNode
            self.nodeListBox.nodeListLE.setText("")
            return False
        nodeToAdd = nodityOps.MyNode(askedNode)

        #Add to node list
        self.allOperatorNodes.append(nodeToAdd)

        # Add to scene
        self.scene.addItem(nodeToAdd)
        self.nodeListBox.close()




if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    view = MyGraphicsWindow()
    view.show()
    sys.exit(app.exec_())

