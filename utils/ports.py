__author__ = 'lijuk'

from PyQt4 import QtGui
from PyQt4 import QtCore


class PortLabel(QtGui.QGraphicsWidget):
    _font = QtGui.QFont('Consolas', 12)

    def __init__(self, port, text, h_offset, color, highlight_color):
        super(PortLabel, self).__init__(port)
        self._port = port
        self._text = text
        self._color = color
        self._textItem = QtGui.QGraphicsTextItem(text, self)
        self._label_color = color
        self._highlight_color = highlight_color
        self._textItem.setDefaultTextColor(self._label_color)
        self._textItem.setFont(self._font)
        self._textItem.translate(0, self._font.pointSizeF() * -0.5)
        option = self._textItem.document().defaultTextOption()
        option.setWrapMode(QtGui.QTextOption.NoWrap)
        self._textItem.document().setDefaultTextOption(option)
        self._textItem.adjustSize()

        self.setPreferredSize(self.text_size())
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
        self.setWindowFrameMargins(0, 0, 0, 0)
        self.set_h_offset(h_offset)

        self.setAcceptHoverEvents(True)
        self._mouse_down_pos = None

    @property
    def text(self):
        return self._text

    @property
    def port(self):
        return self._port

    def set_h_offset(self, h_offset):
        self.translate(h_offset, 0)

    def get_color(self):
        return self._color

    def set_color(self, color):
        self._textItem.setDefaultTextColor(color)
        self.update()

    def text_size(self):
        return QtCore.QSizeF(
            self._textItem.textWidth(),
            self._font.pointSizeF()
        )

    def highlight(self):
        self.set_color(self._highlight_color)

    def unhighlight(self):
        self.set_color(self._label_color)

    def hoverEnterEvent(self, event):
        self.highlight()
        super(PortLabel, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.unhighlight()
        super(PortLabel, self).hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        self._mouse_down_pos = self.mapToScene(event.pos())

    def mouseMoveEvent(self, event):
        self.unhighlight()
        scene_pos = self.mapToScene(event.pos())

        # activate the port which user mouser hover
        delta = scene_pos - self._mouse_down_pos
        if delta.x() < 0:
            if self._port.in_circle is not None:
                self._port.in_circle.mousePressEvent(event)
        else:
            if self._port.out_circle is not None:
                self._port.out_circle.mousePressEvent(event)


class PortCircle(QtGui.QGraphicsWidget):

    _radius = 4.5
    _diameter = 2 * _radius

    def __init__(self, port, graph, h_offset, color, connection_point_type):
        super(PortCircle, self).__init__(port)

        self._graph = graph
        self._port = port
        self._color = color
        self._connections = set()
        self._connection_point_type = connection_point_type
        self._support_only_single_connection = connection_point_type == 'In'

        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
        size = QtCore.QSizeF(self._diameter, self._diameter)
        self.setPreferredSize(size)
        self.setWindowFrameMargins(0, 0, 0, 0)

        self.translate(self._radius * h_offset, 0)

        self._defaultPen = QtGui.QPen(QtGui.QColor(25, 25, 25), 1.0)
        self._hoverPen = QtGui.QPen(QtGui.QColor(255, 255, 100), 1.5)

        self._ellipse_item = QtGui.QGraphicsEllipseItem(self)
        self._ellipse_item.setPen(self._defaultPen)
        self._ellipse_item.setPos(size.width()/2, size.height()/2)
        self._ellipse_item.setRect(
            -self._radius,
            -self._radius,
            self._diameter,
            self._diameter,
            )
        if connection_point_type == 'In':
            self._ellipse_item.setStartAngle(270 * 16)
            self._ellipse_item.setSpanAngle(180 * 16)

        self.set_color(color)
        self.setAcceptHoverEvents(True)

    @property
    def port(self):
        return self._port

    def get_color(self):
        return self.port.get_color()

    def set_color(self, color):
        self._color = color
        self._ellipse_item.setBrush(QtGui.QBrush(self._color))

    def center_in_scene_coords(self):
        return self._ellipse_item.mapToScene(0, 0)

    def set_default_pen(self, pen):
        self._default_pen = pen
        self._ellipse_item.setPen(self._defaultPen)

    def set_hover_pen(self, pen):
        self._hoverPen = pen

    def highlight(self):
        self._ellipse_item.setBrush(QtGui.QBrush(self._color.lighter()))
        # make the port bigger to highlight it can accept the connection.
        self._ellipse_item.setRect(
            -self._radius * 1.3,
            -self._radius * 1.3,
            self._diameter * 1.3,
            self._diameter * 1.3,
            )

    def unhighlight(self):
        self._ellipse_item.setBrush(QtGui.QBrush(self._color))
        self._ellipse_item.setRect(
            -self._radius,
            -self._radius,
            self._diameter,
            self._diameter,
            )

    def connection_point_type(self):
        return self._connection_point_type

    def is_in_connection_point(self):
        return self._connection_point_type == 'In'

    def is_out_connection_point(self):
        return self._connection_point_type == 'Out'

    def supports_only_single_connections(self):
        return self._support_only_single_connection

    def set_supports_only_single_connections(self, value):
        self._support_only_single_connection = value

    def can_connect_to(self, other_port_circle):

        if self.connection_point_type == other_port_circle.connection_point_type:
            return False

        if self.port.data_type != other_port_circle.port.data_type:
            return False

        # Check if you're trying to connect to a port on the same node.
        # TODO: Do propper cycle checking..
        other_port = other_port_circle.port
        port = self.port
        if other_port.node == port.node:
            return False

        return True

    def add_connection(self, connection):
        """
        Adds connection to the list
        :param connection: Connection to add
        :return: bool
        """
        if self._support_only_single_connection and len(self._connections) != 0:
            # gather all the connections into a list, and then remove them from the graph.
            # This is because we can't remove connections from ports while
            # iterating over the set.
            connections = []
            for c in self._connections:
                connections.append(c)
            for c in connections:
                self._graph.remove_connection(c)

        self._connections.add(connection)

        return True

    def remove_connection(self, connection):
        """
        Removes a connection to the list.
        :param connection: connection to remove
        :return: bool
        """
        self._connections.remove(connection)
        return True

    def get_connections(self):
        """
        Gets the ports connections list.
        :return: list
        """
        return self._connections

    # -------------------------
    # Events
    # -------------------------
    def hoverEnterEvent(self, event):
        self.highlight()
        super(PortCircle, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.unhighlight()
        super(PortCircle, self).hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        self.unhighlight()
        scene_pos = self.mapToScene(event.pos())

        from mouse_grabber import MouseGrabber
        if self.is_in_connection_point():
            MouseGrabber(self._graph, scene_pos, self, 'Out')
        elif self.is_out_connection_point():
            MouseGrabber(self._graph, scene_pos, self, 'In')


class ItemHolder(QtGui.QGraphicsWidget):
    """docstring for ItemHolder"""
    def __init__(self, parent):
        super(ItemHolder, self).__init__(parent)

        layout = QtGui.QGraphicsLinearLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def set_item(self, item):
        item.setParentItem(self)
        self.layout().addItem(item)


class BasePort(QtGui.QGraphicsWidget):

    _label_color = QtGui.QColor(255, 200, 100)
    _label_highlight_color = QtGui.QColor(225, 225, 225, 255)

    def __init__(self, parent, graph, name, color, data_type, connection_point_type):
        super(BasePort, self).__init__(parent)

        self._node = parent
        self._graph = graph
        self._name = name
        self._data_type = data_type
        self._connection_point_type = connection_point_type
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                             QtGui.QSizePolicy.Fixed))

        layout = QtGui.QGraphicsLinearLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self._color = color

        self._in_circle = None
        self._out_circle = None
        self._label_item = None

        self._in_circle_holder = ItemHolder(self)
        self._out_circle_holder = ItemHolder(self)
        self._label_item_holder = ItemHolder(self)

        self.layout().addItem(self._in_circle_holder)
        self.layout().setAlignment(self._in_circle_holder,
                                   QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        self.layout().addItem(self._label_item_holder)
        self.layout().setAlignment(self._label_item_holder,
                                   QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        self.layout().addItem(self._out_circle_holder)
        self.layout().setAlignment(self._out_circle_holder,
                                   QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    @property
    def name(self):
        return self._name

    @property
    def data_type(self):
        return self._data_type

    @property
    def node(self):
        return self._node

    @property
    def graph(self):
        return self._graph

    def get_color(self):
        return self._color

    def set_color(self, color):
        if self._in_circle is not None:
            self._in_circle.set_color(color)
        if self._out_circle is not None:
            self._out_circle.set_color(color)
        self._color = color
    
    @property
    def in_circle(self):
        return self._in_circle

    @in_circle.setter
    def in_circle(self, in_circle):
        self._in_circle_holder.set_item(in_circle)
        self._in_circle = in_circle
        self.layout().insertStretch(2, 2)
        self.update_content_margins()
    
    @property
    def out_circle(self):
        return self._out_circle

    @out_circle.setter
    def out_circle(self, out_circle):
        self._out_circle_holder.set_item(out_circle)
        self._out_circle = out_circle
        self.layout().insertStretch(1, 2)
        self.update_content_margins()

    @property
    def label_item(self):
        return self._label_item

    @label_item.setter
    def label_item(self, label_item):
        self._label_item_holder.set_item(label_item)
        self._label_item = label_item

    @property
    def connection_point_type(self):
        return self._connection_point_type

    def update_content_margins(self):
        left = 0
        right = 0
        if self._in_circle is None:
            left = 30
        if self._out_circle is None:
            right = 30
        self.layout().setContentsMargins(left, 0, right, 0)


class InputPort(BasePort):

    def __init__(self, parent, graph, name, color, data_type):
        super(InputPort, self).__init__(parent, graph, name, color, data_type, 'In')

        self.in_circle = PortCircle(self, graph, -2, color, 'In')
        self.label_item = PortLabel(self, name, -10,
                                  self._label_color,
                                  self._label_highlight_color)


class OutputPort(BasePort):

    def __init__(self, parent, graph, name, color, data_type):
        super(OutputPort, self).__init__(parent, graph, name, color, data_type, 'Out')

        self.label_item = PortLabel(self,
                                    self._name,
                                    10, self._label_color,
                                    self._label_highlight_color)
        self.out_circle = PortCircle(self,
                                     graph,
                                     2,
                                     color,
                                     'Out')

