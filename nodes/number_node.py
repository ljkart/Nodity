__author__ = 'lijuk'

from PyQt4 import QtGui
from utils.node import Node
from utils.ports import OutputPort


class CustomNode(Node):
    _input_port_color = QtGui.QColor(128, 170, 170, 255)
    _output_port_color = QtGui.QColor(128, 170, 170, 255)

    def __init__(self, graph):
        self._name = "Number"
        super(CustomNode, self).__init__(graph, self._name)
        self._graph = graph
        self.add_port(OutputPort(self, self._graph, "Output", self._output_port_color, data_type="Number"))

