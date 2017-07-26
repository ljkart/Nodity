__author__ = 'lijuk'

import math

from PyQt4 import QtCore
from PyQt4 import QtGui
from ports import InputPort
from ports import OutputPort


class NodeTitle(QtGui.QGraphicsWidget):
    _color = QtGui.QColor(200, 200, 10)
    _font = QtGui.QFont("Consolas", 20)
    # _font.setLetterSpacing(QtGui.QFont.PercentageSpacing, 200)
    _label_bottom_spacing = 15

    def __init__(self, text, parent=None):
        super(NodeTitle, self).__init__(parent)

        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
                                             QtGui.QSizePolicy.Fixed))

        self._textItem = QtGui.QGraphicsTextItem(text, self)
        self._textItem.setDefaultTextColor(NodeTitle._color)
        self._textItem.setFont(NodeTitle._font)
        self._textItem.setPos(0, -2)
        option = self._textItem.document().defaultTextOption()
        option.setWrapMode(QtGui.QTextOption.NoWrap)
        self._textItem.document().setDefaultTextOption(option)
        self._textItem.adjustSize()

        self.setPreferredSize(self.textSize())

    def setText(self, text):
        self._textItem.setPlainText(text)
        self._textItem.adjustSize()
        self.setPreferredSize(self.textSize())

    def textSize(self):
        return QtCore.QSizeF(self._textItem.textWidth(),
                             self._font.pointSizeF() + NodeTitle._label_bottom_spacing)


class NodeHeader(QtGui.QGraphicsWidget):

    def __init__(self, text, parent=None):
        super(NodeHeader, self).__init__(parent)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                             QtGui.QSizePolicy.Expanding))

        layout = QtGui.QGraphicsLinearLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        layout.setOrientation(QtCore.Qt.Horizontal)
        self.setLayout(layout)

        self._titleWidget = NodeTitle(text, self)
        layout.addItem(self._titleWidget)
        layout.setAlignment(self._titleWidget, QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)

    def setText(self, text):
        self._titleWidget.setText(text)


class PortList(QtGui.QGraphicsWidget):
    def __init__(self, parent):
        super(PortList, self).__init__(parent)
        layout = QtGui.QGraphicsLinearLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(7)
        layout.setOrientation(QtCore.Qt.Vertical)
        self.setLayout(layout)

    def addPort(self, port, alignment):
        layout = self.layout()
        layout.addItem(port)
        layout.setAlignment(port, alignment)
        self.adjustSize()
        return port


class Node(QtGui.QGraphicsWidget):
    name_changed = QtCore.pyqtSignal(str, str)
    node_selected = QtCore.pyqtSignal()

    _defaultColor = QtGui.QColor(100, 10, 100, 255)
    _unselectedColor = QtGui.QColor(25, 25, 25)
    _selectedColor = QtGui.QColor(100, 150, 150, 255)
    _unselectedPen = QtGui.QPen(_unselectedColor, 1.6)
    _selectedPen = QtGui.QPen(_selectedColor, 1.6)
    _linePen = QtGui.QPen(QtGui.QColor(25, 25, 25, 255), 1.25)

    def __init__(self, graph, name):
        super(Node, self).__init__()

        self._name = name
        self._graph = graph
        self._color = self._defaultColor

        # Set size
        self.setMinimumWidth(60)
        self.setMinimumHeight(20)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                             QtGui.QSizePolicy.Expanding))

        # shadow effect
        shdw_effect = QtGui.QGraphicsDropShadowEffect()
        shdw_effect.setBlurRadius(25)
        shdw_effect.setOffset(3)
        shdw_effect.setColor(QtGui.QColor(10, 10, 10, 100))
        self.setGraphicsEffect(shdw_effect)

        layout = QtGui.QGraphicsLinearLayout()
        layout.setContentsMargins(5, 0, 5, 7)
        layout.setSpacing(7)
        layout.setOrientation(QtCore.Qt.Vertical)
        self.setLayout(layout)

        self._headerItem = NodeHeader(self._name, self)
        layout.addItem(self._headerItem)
        layout.setAlignment(self._headerItem, QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)

        self._ports = []
        self._input_ports_holder = PortList(self)
        self._output_ports_holder = PortList(self)

        layout.addItem(self._input_ports_holder)
        layout.addItem(self._output_ports_holder)

        self._selected = False
        self._dragging = False
        self._attributes = []

    # ------------------------
    # Properties
    # -----------------------

    @property
    def name(self):
        """
        node name
        :return: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Setter method for name
        :param name: new name for node
        :return: None
        """
        if name != self._name and name:
            old_name = self._name
            self._name = name
            self._headerItem.setText(name)
            self.name_changed.emit(old_name, name)
            self.adjustSize()

    @property
    def graph_pos(self):
        """
        to get the node position in the graph
        :return:
        """
        transform = self.transform()
        size = self.size()
        return QtCore.QPointF(transform.dx()+(size.width()*0.5), transform.dy()+(size.height()*0.5))

    @graph_pos.setter
    def graph_pos(self, pos):
        """
        to set graph pos
        :param pos: position
        :return: None
        """
        self.prepare_connection_geometry_change()
        size = self.size()
        self.setTransform(QtGui.QTransform.fromTranslate(pos.x()-(size.width()*0.5),
                                                         pos.y()-(size.height()*0.5)),
                          False)

    @property
    def graph(self):
        """
        Return graph
        :return: Graph object
        """
        return self._graph

    def get_color(self):
        """
        get node current color
        :return: QColor
        """
        return self._color

    def set_color(self, color):
        """
        New QColor to set to node
        :param color: QColor
        :return: None
        """
        self._color = color
        self.update()

    def translate(self, x, y):
        self.prepare_connection_geometry_change()
        super(Node, self).translate(x, y)

    def prepare_connection_geometry_change(self):
        for port in self._ports:
            if port.in_circle:
                for connection in port.in_circle.get_connections():
                    connection.prepareGeometryChange()
            if port.out_circle:
                for connection in port.out_circle.get_connections():
                    connection.prepareGeometryChange()

    def paint(self, painter, option, widget):
        rect = self.windowFrameRect()
        painter.setBrush(self._color)

        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 0))

        roundingY = 10
        roundingX = rect.height() / rect.width() * roundingY

        painter.drawRoundRect(rect, roundingX, roundingY)

        # Title BG
        title_height = self._headerItem.size().height() - 3

        painter.setBrush(self._color.darker(125))
        roundingY = rect.width() * roundingX / title_height
        painter.drawRoundRect(0, 0, rect.width(), title_height, roundingX, roundingY)
        painter.drawRect(0, title_height * 0.5 + 2, rect.width(), title_height * 0.5)

        painter.setBrush(QtGui.QColor(0, 0, 0, 0))
        if self._selected:
            painter.setPen(self._selectedPen)
        else:
            painter.setPen(self._unselectedPen)

        roundingY = 10
        roundingX = rect.height() / rect.width() * roundingY
        painter.drawRoundRect(rect, roundingX, roundingY)

    # --------------------
    # Selection
    # --------------------
    def is_selected(self):
        return self._selected

    def set_selected(self, selected=True):
        self.setZValue(10.0 if selected else 0.0)
        self._selected = selected
        self.update()

    # -----------------------
    # Ports
    # -----------------------
    def add_port(self, port):
        if isinstance(port, InputPort):
            self._input_ports_holder.addPort(port,
                                             QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        elif isinstance(port, OutputPort):
            self._output_ports_holder.addPort(port,
                                             QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        self._ports.append(port)
        self.adjustSize()
        return port

    def get_port(self, name):
        for port in self._ports:
            if port.name == name:
                return port
        return None

    def add_attribute(self, attribute):
        self._attributes.append(attribute)

    def get_attribute(self, name):
        for each_attribute in self._attributes:
            if each_attribute.name == name:
                return each_attribute

    def get_all_attributes(self):
        return self._attributes


    # --------------------
    # Events
    # --------------------

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            modifiers = event.modifiers()
            if modifiers == QtCore.Qt.ControlModifier:
                if not self.is_selected():
                    self._graph.select_node(self, clear_selection=False)
                else:
                    self._graph.deselect_node(self)

            elif modifiers == QtCore.Qt.ShiftModifier:
                if not self.is_selected():
                    self._graph.select_node(self, clear_selection=False)
            else:
                if not self.is_selected():
                    self._graph.select_node(self, clear_selection=True)

                self._dragging = True
                self._mouse_down_point = self.mapToScene(event.pos())
                self._mouse_delta = self._mouse_down_point - self.graph_pos
                self._last_drag_point = self._mouse_down_point
                self._nodes_moved = False

        else:
            super(Node, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging:
            new_pos = self.mapToScene(event.pos())

            graph = self.graph
            if graph.snap_to_grid is True:
                grid_size = graph.grid_size

                new_node_pos = new_pos - self._mouse_delta

                snap_posX = math.floor(new_node_pos.x() / grid_size) * grid_size
                snap_posY = math.floor(new_node_pos.y() / grid_size) * grid_size
                snap_pos = QtCore.QPointF(snap_posX, snap_posY)

                new_pos_offset = snap_pos - new_node_pos

                new_pos = new_pos + new_pos_offset

            delta = new_pos - self._last_drag_point
            self._graph.move_selected_nodes(delta)
            self._last_drag_point = new_pos
            self._nodes_moved = True
        else:
            super(Node, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._dragging:
            if self._nodes_moved:

                new_pos = self.mapToScene(event.pos())

                delta = new_pos - self._mouse_down_point
                self._graph.end_move_selected_nodes(delta)

            self.setCursor(QtCore.Qt.ArrowCursor)
            self._dragging = False
        else:
            super(Node, self).mouseReleaseEvent(event)

