__author__ = 'lijuk'

from PyQt4 import QtGui
from PyQt4 import QtCore

from ports import PortCircle
from ports import PortLabel
from connection import Connection


class MouseGrabber(PortCircle):
    """docstring for MouseGrabber"""

    def __init__(self, graph, pos, other_port_circle, connection_point_type):
        super(MouseGrabber, self).__init__(None,
                                           graph,
                                           0,
                                           other_port_circle.port.get_color(),
                                           connection_point_type)

        self._ellipse_item.setPos(0, 0)
        self._ellipse_item.setStartAngle(0)
        self._ellipse_item.setSpanAngle(360 * 16)

        self._other_port_item = other_port_circle

        self._mouse_over_port_circle = None
        self._graph.scene().addItem(self)

        self.setZValue(-1)
        self.setTransform(QtGui.QTransform.fromTranslate(pos.x(), pos.y()), False)
        self.grabMouse()

        if self.connection_point_type() == 'Out':
            self._connection = Connection(self._graph, self, other_port_circle)
        elif self.connection_point_type() == 'In':
            self._connection = Connection(self._graph, other_port_circle, self)
        # Do not emit a notification for this temporary connection.
        self._graph.add_connection(self._connection, emit_signal=False)
        self._graph.emit_begin_connection_manipulation_signal()

    def get_color(self):
        return self._color

    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.pos())

        for connection in self.get_connections():
            connection.prepareGeometryChange()

        self.setTransform(QtGui.QTransform.fromTranslate(scene_pos.x(),
                                                         scene_pos.y()), False)
        colliding_items = self.collidingItems(QtCore.Qt.IntersectsItemBoundingRect)
        colliding_port_items = filter(lambda item: isinstance(item, (PortCircle, PortLabel)), colliding_items)

        def can_connect(item):
            if isinstance(item, PortCircle):
                mouse_over_port_circle = item
            else:
                if self.connection_point_type() == 'In':
                    mouse_over_port_circle = item.port.in_circle
                else:
                    mouse_over_port_circle = item.port.out_circle

                if mouse_over_port_circle is None:
                    return False

            return mouse_over_port_circle.can_connect_to(self._other_port_item)

        colliding_port_items = filter(lambda port: can_connect(port), colliding_port_items)
        if len(colliding_port_items) > 0:

            if isinstance(colliding_port_items[0], PortCircle):
                self.set_mouse_over_port_circle(colliding_port_items[0])
            else:
                if self.connection_point_type() == 'In':
                    self.set_mouse_over_port_circle(colliding_port_items[0].port.in_circle)
                else:
                    self.set_mouse_over_port_circle(colliding_port_items[0].port.out_circle)

        elif self._mouse_over_port_circle is not None:
            self.set_mouse_over_port_circle(None)

    def mouseReleaseEvent(self, event):

        # Destroy the temporary connection.
        self._graph.remove_connection(self._connection, emit_signal=False)
        self._connection = None

        if self._mouse_over_port_circle is not None:
            try:
                if self.connection_point_type() == 'In':
                    source_port_circle = self._other_port_item
                    target_port_circle = self._mouse_over_port_circle
                elif self.connection_point_type() == 'Out':
                    source_port_circle = self._mouse_over_port_circle
                    target_port_circle = self._other_port_item

                connection = Connection(self._graph, source_port_circle, target_port_circle)
                self._graph.add_connection(connection)
                self._graph.emit_end_connection_manipulation_signal()

            except Exception as e:
                print "Exception in MouseGrabber.mouseReleaseEvent: " + str(e)

            self.set_mouse_over_port_circle(None)

        self.destroy()

    def set_mouse_over_port_circle(self, portCircle):

        if self._mouse_over_port_circle != portCircle:
            if self._mouse_over_port_circle is not None:
                self._mouse_over_port_circle.unhighlight()
                self._mouse_over_port_circle.port.label_item.unhighlight()

            self._mouse_over_port_circle = portCircle

            if self._mouse_over_port_circle is not None:
                self._mouse_over_port_circle.highlight()
                self._mouse_over_port_circle.port.label_item.highlight()

    def destroy(self):
        self.ungrabMouse()
        scene = self.scene()
        if self._connection is not None:
            self._graph.remove_connection(self._connection, emit_signal=False)
        # Destroy the grabber.
        scene.removeItem(self)

