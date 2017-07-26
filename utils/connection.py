__author__ = 'lijuk'

from PyQt4 import QtGui
from PyQt4 import QtCore


class Connection(QtGui.QGraphicsPathItem):
    __defaultPen = QtGui.QPen(QtGui.QColor(168, 134, 3), 1.5)

    def __init__(self, graph, src_port_circle, dst_port_circle):
        super(Connection, self).__init__()

        self._graph = graph
        self._src_port_circle = src_port_circle
        self._dst_port_circle = dst_port_circle
        pen_style = QtCore.Qt.DashLine

        self._connection_color = QtGui.QColor(0, 0, 0)
        self._connection_color.setRgbF(*self._src_port_circle.get_color().getRgbF())
        self._connection_color.setAlpha(125)

        self._default_pen = QtGui.QPen(self._connection_color, 1.5, style=pen_style)
        self._default_pen.setDashPattern([1, 2, 2, 1])

        self._connection_hover_color = QtGui.QColor(0, 0, 0)
        self._connection_hover_color.setRgbF(*self._src_port_circle.get_color().getRgbF())
        self._connection_hover_color.setAlpha(255)

        self._hover_pen = QtGui.QPen(self._connection_hover_color, 1.5, style=pen_style)
        self._hover_pen.setDashPattern([1, 2, 2, 1])

        self.setPen(self._default_pen)
        self.setZValue(-1)


        self.setAcceptHoverEvents(True)
        self.connect()

    @property
    def src_port_circle(self):
        return self._src_port_circle

    @property
    def dst_port_circle(self):
        return self._dst_port_circle


    @property
    def src_port(self):
        return self._src_port_circle.port

    @property
    def dst_port(self):
        return self._dst_port_circle.port

    def set_pen_style(self, pen_style):
        self._default_pen.setStyle(pen_style)
        self._hover_pen.setStyle(pen_style)
        self.setPen(self._default_pen) # Force a redraw

    def set_pen_width(self, width):
        self._default_pen.setWidthF(width)
        self._hover_pen.setWidthF(width)
        self.setPen(self._default_pen) # Force a redraw

    def boundingRect(self):
        src_point = self.mapFromScene(self._src_port_circle.center_in_scene_coords())
        dst_point = self.mapFromScene(self._dst_port_circle.center_in_scene_coords())
        pen_width = self._default_pen.width()

        return QtCore.QRectF(
            min(src_point.x(), dst_point.x()),
            min(src_point.y(), dst_point.y()),
            abs(dst_point.x() - src_point.x()),
            abs(dst_point.y() - src_point.y()),
            ).adjusted(-pen_width/2, -pen_width/2, +pen_width/2, +pen_width/2)

    def paint(self, painter, option, widget):
        src_point = self.mapFromScene(self._src_port_circle.center_in_scene_coords())
        dst_point = self.mapFromScene(self._dst_port_circle.center_in_scene_coords())

        dist_between = dst_point - src_point

        self._path = QtGui.QPainterPath()
        self._path.moveTo(src_point)
        self._path.cubicTo(
            src_point + QtCore.QPointF(dist_between.x() * 0.4, 0),
            dst_point - QtCore.QPointF(dist_between.x() * 0.4, 0),
            dst_point
            )
        self.setPath(self._path)
        super(Connection, self).paint(painter, option, widget)

    def hoverEnterEvent(self, event):
        self.setPen(self._hover_pen)
        super(Connection, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setPen(self._default_pen)
        super(Connection, self).hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() is QtCore.Qt.MouseButton.LeftButton:
            self._dragging = True
            self._last_drag_point = self.mapToScene(event.pos())
            event.accept()
        else:
            super(Connection, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging:
            pos = self.mapToScene(event.pos())
            delta = pos - self._last_drag_point
            if delta.x() != 0:

                self._graph.removeConnection(self)

                import mouse_grabber
                if delta.x() < 0:
                    mouse_grabber.MouseGrabber(self._graph, pos, self._src_port_circle, 'In')
                else:
                    mouse_grabber.MouseGrabber(self._graph, pos, self._dst_port_circle, 'Out')

        else:
            super(Connection, self).mouseMoveEvent(event)

    def disconnect(self):
        self._src_port_circle.remove_connection(self)
        self._dst_port_circle.remove_connection(self)

    def connect(self):
        self._src_port_circle.add_connection(self)
        self._dst_port_circle.add_connection(self)
