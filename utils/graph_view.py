__author__ = 'lijuk'

import copy
from PyQt4 import QtGui
from PyQt4 import QtCore

from node import Node
from connection import Connection
from selection_rect import SelectionRect


class GraphView(QtGui.QGraphicsView):
    """ View for the node graph scene """

    node_added = QtCore.pyqtSignal(Node)
    node_removed = QtCore.pyqtSignal(Node)
    node_name_changed = QtCore.pyqtSignal(str, str)
    selection_changed = QtCore.pyqtSignal(list, list)
    selection_moved = QtCore.pyqtSignal(set, QtCore.QPointF)
    end_selection_moved = QtCore.pyqtSignal(set, QtCore.QPointF)
    begin_node_selection = QtCore.pyqtSignal()
    end_node_selection = QtCore.pyqtSignal()
    connection_added = QtCore.pyqtSignal(Connection)
    connection_removed = QtCore.pyqtSignal(Connection)
    begin_connection_manipulation = QtCore.pyqtSignal()
    end_connection_manipulation = QtCore.pyqtSignal()

    _size = QtCore.QSize(900, 600)
    _grid_size = 30
    _grid_size_course = 300
    _background_color = QtGui.QColor(50, 50, 50)
    _grid_penS = QtGui.QPen(QtGui.QColor(44, 44, 44, 255), 0.5)
    _grid_penL = QtGui.QPen(QtGui.QColor(40, 40, 40, 255), 1.0)

    _mouse_wheel_zoom_rate = 0.0005

    _snap_to_grid = False

    def __init__(self, parent=None):

        super(GraphView, self).__init__(parent)

        self._parent = parent

        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing)

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.resize(self._size)
        self.setSceneRect(-self._size.width() * 0.5, -self._size.height() * 0.5,
                          self._size.width(), self._size.height())

        self.setAcceptDrops(True)
        self.refresh()

    @property
    def grid_size(self):
        """
        Return grid size
        :return: int
        """
        return self._grid_size

    @property
    def snap_to_grid(self):
        """
        get snap to grid stat
        :return: bool
        """
        return self._snap_to_grid

    def refresh(self):
        """
        Refresh Gui with setting all necessary items
        :return: None
        """

        # Set Graphics scene
        self.setScene(QtGui.QGraphicsScene())
        self._connections = set()
        self._nodes = {}
        self._selection = set()
        self._manipulation_mode = 0
        self._selection_rect = None

    def add_node(self, node, emit_signal=True):
        """
        :param node to add:
        :param emit_signal: emit node_add signal
        :return:
        """
        self.scene().addItem(node)
        self._nodes[node.name] = node
        node.name_changed.connect(self._on_node_name_changed)

        if emit_signal:
            self.node_added.emit(node)

        return node

    def select_node(self, node, clear_selection=False, emit_signal=True):
        """
        To highlight the given node
        :param node: node to highlight
        :return: None
        """
        prev_selection = []
        if emit_signal:
            for n in self._selection:
                prev_selection.append(n)

        if clear_selection is True:
            self.clear_selection(emit_signal=False)

        if node in self._selection:
            raise IndexError("Node is already in selection!")

        node.set_selected(True)
        self._selection.add(node)
        if emit_signal:

            new_selection = []
            for n in self._selection:
                new_selection.append(n)
            self.selection_changed.emit(prev_selection, new_selection)

    def deselect_node(self, node, emit_signal=True):
        """
        To deselect the given node
        :param node: node given
        :return: None
        """
        if node not in self._selection:
            raise IndexError("Node is not in selection!")

        prev_selection = []
        if emit_signal:
            for n in self._selection:
                prev_selection.append(n)

        node.set_selected(False)
        self._selection.remove(node)

        if emit_signal:
            new_selection = []
            for n in self._selection:
                new_selection.append(n)

            self.selection_changed.emit(prev_selection, new_selection)

    def clear_selection(self, emit_signal=True):
        """
        Clear nodes selection
        :param emitSignal: emit signal
        :return: None
        """
        prev_selection = []
        if emit_signal:
            for node in self._selection:
                prev_selection.append(node)

        for node in self._selection:
            node.set_selected(False)
        self._selection.clear()

        if emit_signal and len(prev_selection) != 0:
            self.selection_changed.emit(prev_selection, [])

    def get_selected_nodes(self):
        """
        Get all selected node
        :return: None
        """
        return self._selection

    def delete_selected_nodes(self):
        """
        Delete selected nodes
        :return: None
        """
        self.begin_delete_selection.emit()

        selected_nodes = self.get_selected_nodes()
        names = ""
        for node in selected_nodes:
            node.disconnect_all_ports()
            self.remove_node(node)

        self.end_delete_selection.emit()

    def move_selected_nodes(self, delta, emit_signal=True):
        """
        Move all selected nodes to delta provided
        :param delta: delta value
        :param emit_signal: emit signal stat
        :return: None
        """
        for node in self._selection:
            node.translate(delta.x(), delta.y())

        if emit_signal:
            self.selection_moved.emit(self._selection, delta)

    def end_move_selected_nodes(self, delta):
        """
        Report end of moving selected nodes
        :param delta:
        :return: None
        """
        self.end_selection_moved.emit(self._selection, delta)

    def _on_node_name_changed(self, oldname, newname):
        """
        Slot connected on node name changed
        :param oldname: old node name
        :param newname: new node name
        :return: None
        """
        if newname in self._nodes and self._nodes[oldname] != self._nodes[newname]:
            raise Exception("New name collides with existing node.")
        node = self._nodes[oldname]
        self._nodes[newname] = node
        del self.__nodes[oldname]
        self.node_name_changed.emit(oldname, newname)

    def drawBackground(self, painter, rect):
        """
        override to drawBackground method to draw custom background
        :param painter: painter object
        :param rect: view rectangle
        :return: None
        """
        painter.fillRect(rect, self._background_color)

        left = int(rect.left()) - (int(rect.left()) % self._grid_size)
        top = int(rect.top()) - (int(rect.top()) % self._grid_size)

        # Draw horizontal fine lines
        grid_lines = []
        painter.setPen(self._grid_penS)
        y = float(top)
        while y < float(rect.bottom()):
            grid_lines.append(QtCore.QLineF(rect.left(), y, rect.right(), y))
            y += self._grid_size
        painter.drawLines(grid_lines)

        # Draw vertical lines
        grid_lines = []
        painter.setPen(self._grid_penL)
        x = float(left)
        while x < float(rect.right()):
            grid_lines.append(QtCore.QLineF(x, rect.top(), x, rect.bottom()))
            x += self._grid_size
        painter.drawLines(grid_lines)

        # Draw thick grid
        left = int(rect.left()) - (int(rect.left()) % self._grid_size_course)
        top = int(rect.top()) - (int(rect.top()) % self._grid_size_course)

        # Draw vertical thick lines
        grid_lines = []
        painter.setPen(self._grid_penL)
        x = left
        while x < rect.right():
            grid_lines.append(QtCore.QLineF(x, rect.top(), x, rect.bottom()))
            x += self._grid_size_course
        painter.drawLines(grid_lines)

        # Draw horizontal thick lines
        grid_lines = []
        painter.setPen(self._grid_penL)
        y = top
        while y < rect.bottom():
            grid_lines.append(QtCore.QLineF(rect.left(), y, rect.right(), y))
            y += self._grid_size_course
        painter.drawLines(grid_lines)

        return super(GraphView, self).drawBackground(painter, rect)

    # ------------------------
    # Connections
    # ------------------------

    def emit_begin_connection_manipulation_signal(self):
        self.begin_connection_manipulation.emit()

    def emit_end_connection_manipulation_signal(self):
        self.end_connection_manipulation.emit()

    def add_connection(self, connection, emit_signal=True):
        """
        to add new connection
        :param connection: new connection
        :param emit_signal: emit signal
        :return: connection
        """
        self._connections.add(connection)
        self.scene().addItem(connection)
        if emit_signal:
            self.connection_added.emit(connection)
        return connection

    def remove_connection(self, connection, emit_signal=True):
        """
        Remove existing connection
        :param connection: connection to remove
        :param emit_signal: emit signal ?
        :return:None
        """

        connection.disconnect()
        self._connections.remove(connection)
        self.scene().removeItem(connection)
        if emit_signal:
            self.connection_removed.emit(connection)

    def get_node(self, name):
        """
        Get node from node list
        :param name: name of the node
        :return: Node else None
        """
        if name in self._nodes:
            return self._nodes[name]
        return None

    def connect_ports(self, src_node, output_name, tgt_node, input_name):
        """
        Connect between ports
        :param src_node: source node
        :param output_name: outut name
        :param tgt_node: target node
        :param input_name: input name
        :return: Connection object
        """

        if isinstance(src_node, Node):
            source_node = src_node
        elif isinstance(src_node, basestring):
            source_node = self.get_node(src_node)
            if not source_node:
                raise Exception("Node not found:" + str(src_node))
        else:
            raise Exception("Invalid src_node:" + str(src_node))

        source_port = source_node.get_port(output_name)
        if not source_port:
            raise Exception("Node '" + source_node.getName() + "' does not have output:" + output_name)

        if isinstance(tgt_node, Node):
            target_node = tgt_node
        elif isinstance(tgt_node, basestring):
            target_node = self.get_node(tgt_node)
            if not target_node:
                raise Exception("Node not found:" + str(tgt_node))
        else:
            raise Exception("Invalid tgt_node:" + str(tgt_node))

        target_port = target_node.getPort(input_name)
        if not target_port:
            raise Exception("Node '" + target_node.name() + "' does not have input:" + input_name)

        connection = Connection(self, source_port.out_circle, target_port.in_circle)
        self.add_connection(connection, emitSignal=False)

        return connection

    # --------------------------
    # Events
    # --------------------------

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.itemAt(event.pos()) is None:
            self.begin_node_selection.emit()
            self._manipulation_mode = 1
            self._mouse_down_selection = copy.copy(self.get_selected_nodes())
            self.clear_selection(emit_signal=False)
            self._selection_rect = SelectionRect(graph=self, mouse_down_pos=self.mapToScene(event.pos()))
        elif event.button() is QtCore.Qt.MidButton:
            self.setCursor(QtCore.Qt.OpenHandCursor)
            self._manipulation_mode = 2
            self._last_pan_point = self.mapToScene(event.pos())
        else:
            super(GraphView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._manipulation_mode == 1:
            drag_point = self.mapToScene(event.pos())
            self._selection_rect.set_drag_point(drag_point)
            for name, node in self._nodes.iteritems():
                if not node.is_selected() and self._selection_rect.collidesWithItem(node):
                    self.select_node(node, emit_signal=False)

        elif self._manipulation_mode == 2:
            delta = self.mapToScene(event.pos()) - self._last_pan_point

            rect = self.sceneRect()
            rect.translate(-delta.x(), -delta.y())
            self.setSceneRect(rect)

            self._last_pan_point = self.mapToScene(event.pos())

        elif self._manipulation_mode == 3:

            new_pos = self.mapToScene(event.pos())
            delta = new_pos - self._last_drag_point
            self._last_drag_point = new_pos

            selected_nodes = self.get_selected_nodes()

            # Apply the delta to each selected node
            for node in selected_nodes:
                node.translate(delta.x(), delta.y())

        else:
            super(GraphView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._manipulation_mode == 1:
            self._selection_rect.destroy()
            self._selection_rect = None
            self._manipulation_mode = 0

            selection = self.get_selected_nodes()

            deselected_nodes = []
            selected_nodes = []

            for node in self._mouse_down_selection:
                if node not in selection:
                    deselected_nodes.append(node)

            for node in selection:
                if node not in self._mouse_down_selection:
                    selected_nodes.append(node)

            if selected_nodes != deselected_nodes:
                self.selection_changed.emit(deselected_nodes, selected_nodes)

            self.end_node_selection.emit()

        elif self._manipulation_mode == 2:
            self.setCursor(QtCore.Qt.ArrowCursor)
            self._manipulation_mode = 0
        else:
            super(GraphView, self).mouseReleaseEvent(event)

    def wheelEvent(self, event):

        (xfo, inv_res) = self.transform().inverted()
        top_left = xfo.map(self.rect().topLeft())
        bottom_right = xfo.map(self.rect().bottomRight())
        center = (top_left + bottom_right) * 0.5

        zoom_factor = 1.0 + event.delta() * self._mouse_wheel_zoom_rate

        transform = self.transform()

        # Limit zoom to 3x
        if transform.m22() * zoom_factor >= 2.0:
            return

        self.scale(zoom_factor, zoom_factor)

        # Call udpate to redraw background
        self.update()


