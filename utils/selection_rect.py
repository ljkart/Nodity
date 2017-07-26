__author__ = 'lijuk'

from PyQt4 import QtGui
from PyQt4 import QtCore


class SelectionRect(QtGui.QGraphicsWidget):
    _background_color = QtGui.QColor(100, 100, 100, 50)
    _pen = QtGui.QPen(QtGui.QColor(25, 25, 25), 1.0,  QtCore.Qt.DashLine)

    def __init__(self, graph, mouse_down_pos):
        super(SelectionRect, self).__init__()
        self.setZValue(-1)

        self._graph = graph
        self._graph.scene().addItem(self)
        self._mouse_down_pos = mouse_down_pos
        self.setPos(self._mouse_down_pos)
        self.resize(0, 0)

    def set_drag_point(self, drag_point):
        topLeft = QtCore.QPointF(self._mouse_down_pos)
        bottom_right = QtCore.QPointF(drag_point)
        if drag_point.x() < self._mouse_down_pos.x():
            topLeft.setX(drag_point.x())
            bottom_right.setX(self._mouse_down_pos.x())
        if drag_point.y() < self._mouse_down_pos.y():
            topLeft.setY(drag_point.y())
            bottom_right.setY(self._mouse_down_pos.y())
        self.setPos(topLeft)
        self.resize(bottom_right.x() - topLeft.x(), bottom_right.y() - topLeft.y())

    def paint(self, painter, option, widget):
        rect = self.windowFrameRect()
        painter.setBrush(self._background_color)
        painter.setPen(self._pen)
        painter.drawRect(rect)

    def destroy(self):
        self._graph.scene().removeItem(self)
