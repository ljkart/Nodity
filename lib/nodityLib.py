__author__ = 'liju.kunnummal'




class NodeBase(object):

    def __init__(self, newNode="", **kwargs):
        self.displayText = newNode
        self.imagePath = ""
        self.description = "Foo"
        self.nodeType = ""
        self.nodeColor = ""
        self.widgetMenu = None