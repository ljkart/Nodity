__author__ = 'liju.kunnummal'


from PyQt4 import QtCore, QtGui
import nodityCustomWidgets



class MyView(QtGui.QGraphicsView):

    connectNodeList = QtCore.pyqtSignal(str, name="state")

    def __init__(self, parent=None):
        super(MyView, self).__init__(parent)

    def keyPressEvent(self, event):
        """
        Catch all tab key press to open node lister.
        :param event: event driven
        :return: None
        """

        if event.key() == QtCore.Qt.Key_Tab:
            print "Tab pressed"
            self.connectNodeList.emit("open")
