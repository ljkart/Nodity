__author__ = 'liju.kunnummal'

import os
from PyQt4 import QtCore, QtGui
from PyQt4 import QtSvg


ROOT = os.path.dirname(os.path.dirname(__file__))
IMAGE_DIR = "%s/src/images" % ROOT

NODE_LIST = ["add", "subtract", "multiply", "divide"]

class MyNode(QtSvg.QGraphicsSvgItem):

    def __init__(self, nodeType=''):
        '''
        initializor
        :param nodeType: type of node, like add, subtract, divide etc.
        :return: None
        '''

        # Create the type of node from selection
        if nodeType == "add":
            self.operator = Add()
        elif nodeType == "subtract":
            self.operator = Subtract()
        elif nodeType == "multiply":
            self.operator = Multiply()
        elif nodeType == "divide":
            self.operator = Divide()


        super(MyNode, self).__init__(self.operator.image)

        self.setElementId("normal")

        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable | QtGui.QGraphicsItem.ItemIsMovable | QtGui.QGraphicsItem.ItemIsFocusable )
        self.addText()

    def __str__(self):
        '''
        Node name
        :return: None
        '''
        return self.node_name

    def addText(self):
        '''
        Function to display text on node item.
        :return: None
        '''
        print "Adding Text"
        font = QtGui.QFont("SansSerif", 17)
        font.setStyleHint(QtGui.QFont.Helvetica)
        font.setStretch(100)
        self.displayText = QtGui.QGraphicsTextItem(self.operator.displayText, self)
        self.displayText.setFont(font)
        self.displayText.setDefaultTextColor(QtGui.QColor(QtCore.Qt.black))
        # self.displayText.setPos(self.boundingRect().width(), self.sceneBoundingRect().height())
        self.displayText.setPos(self.boundingRect().x(), self.sceneBoundingRect().height())
        self.displayText.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)

    # def mousePressEvent(self, event):
    #     '''
    #     Track all mouse press events
    #     :param event: event object.
    #     :return: None
    #     '''
    #     if event.button() == QtCore.Qt.LeftButton:
    #         print "mouse clicked"

    # def hoverMoveEvent(self,event):
    #     self.setElementId("hover")

    # def hoverLeaveEvent(self, event):
    #     self.setElementId("regular")

    # def mouseReleaseEvent(self, event):
    #     self.setElementId("regular")

    # def paint(self, painter, option, widget):

    #     selected = False

    #     # Bitwise operations. These 2 if statements are checking to see if the current state of the item is selected or has focus.
    #     # If it is either, it sets them to false. Then, we set OUR selected flag to True so we can make our own selection graphic.
    #     # In essence, this "catches" the selected state and turns it off so the default BAD dotted line doesn't appear around the icon.
    #     if option.state & QtGui.QStyle.State_HasFocus:
    #         option.state ^= QtGui.QStyle.State_HasFocus
    #         selected = True

    #     if option.state & QtGui.QStyle.State_Selected:
    #         option.state ^= QtGui.QStyle.State_Selected
    #         selected = True

    #     super(MyNode, self).paint(painter, option, widget)

    #     # Since we turned off the default selection state, below we will make our own "selection" graphic.
    #     if selected:
    #         # Do special painting for selected state
    #         print "hover"
    #         self.setElementId("hover")

    #     else:
    #         print "regular"
    #         self.setElementId("regular")




class OperatorBase(object):
    """
        Base class for every operator node.
    """
    def __init__(self):
        self.image = ""
        self.displayText = ""
        self.description = ""
        self.nodeColor = ""


    def doIt(self, *args, **kwargs):
        pass


class Add(OperatorBase):

    def __init__(self):
        super(Add, self).__init__()
        self.image = "%s/button01.svg" % IMAGE_DIR
        self.displayText = "add"


class Subtract(OperatorBase):

    def __init__(self):
        super(Subtract, self).__init__()
        self.image = "%s/button01.svg" % IMAGE_DIR
        self.displayText = "subtract"


class Multiply(OperatorBase):

    def __init__(self):
        super(Multiply, self).__init__()
        self.image = "%s/button01.svg" % IMAGE_DIR
        self.displayText = "multiply"


class Divide(OperatorBase):

    def __init__(self):
        super(Divide, self).__init__()
        self.image = "%s/button01.svg" % IMAGE_DIR
        self.displayText = "divide"



