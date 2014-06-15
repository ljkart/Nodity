__author__ = 'liju.kunnummal'

from PyQt4 import QtCore, QtGui
import nodityOps


class NodeListWindow(QtGui.QWidget):

    def __init__(self, pos, size):
        super(NodeListWindow, self).__init__()

        print "position - ", pos

        self.resize(243, 26)

        # TODO : set position inside the parent window
        # print "-->", QtGui.QWidget.mapToParent(self, pos)
        #
        # newPos = pos
        # if pos.x() > size[0]:
        #     newPos = QtCore.QPoint(size[0] - 100, newPos.y())
        # if pos.y > size[1]:
        #     newPos = QtCore.QPoint(newPos.x(), size[1] - 100)

        # Window
        self.move(pos)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        gridLayout = QtGui.QGridLayout()
        gridLayout.setSpacing(0)
        gridLayout.setMargin(0)

        self.nodeListLE = QtGui.QLineEdit()
        gridLayout.addWidget(self.nodeListLE)

        self.setLayout(gridLayout)

        # Do stuff now!
        self.stat = 'open'
        self.completor = QtGui.QCompleter(nodityOps.NODE_LIST)
        self.nodeListLE.setCompleter(self.completor)


    def keyPressEvent(self, event):
        """
        Catch all tab key press to open node lister.
        :param event: event driven
        :return: None
        """

        if event.key() == QtCore.Qt.Key_Escape:
            if self.stat == "open":
                self.stat = "closed"
                self.close()



