from tkinter import *
import time, random

try:
    from drawable import *
    from VisualizationApp import *
    from BinaryTreeBase import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *
    from .BinaryTreeBase import *

class BinaryTree(BinaryTreeBase):
    def __init__(self, canvasWidth=800, canvasHeight=400, title="Binary Search Tree", **kwargs):
        super().__init__(0, 0, canvasWidth, canvasHeight, title=title,
                         canvasWidth=canvasWidth, canvasHeight=canvasHeight, 
                         **kwargs)
        self.buttons = self.makeButtons()
        self.title = title

        # populate the tree
        self.fill(20)

    #Fill the tree with n nodes
    def fill(self, n):
        callEnviron = self.createCallEnvironment()

        # empty the tree
        self.emptyTree()

        #randomly generate a tree
        nums = list(range(1, 99))
        random.shuffle(nums)
        while self.size < n and nums:
            num = nums.pop()
            self.insertElem(nums.pop(), animation=False)

        self.cleanUp(callEnviron)


    # find node with given key k
    # return the associated data or None
    def find(self, key, stopAnimations=True):
        if self.size == 0: return None, None

        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        # start at the root
        level = 0
        cur = self.getRoot()
        parent = cur
        arrow = self.createArrow(cur)
        callEnviron |= set(arrow)

        # while we haven't found the key
        while cur:
            # move arrow
            self.moveArrow(arrow, cur)
            self.wait(0.3)

            # did we find the key?
            if cur.getKey() == key:
                callEnviron.add(self.createHighlightedValue(cur))
                self.wait(0.2)
                self.cleanUp(callEnviron, stopAnimations=stopAnimations)
                return cur, parent

            parent = cur
            level += 1
            # go left ?
            if key < cur.getKey():
                cur = self.getLeftChild(cur)
            # go right
            else:
                cur = self.getRightChild(cur)
            
        self.cleanUp(callEnviron, stopAnimations=stopAnimations)
        return None, None

    def insertElem(self, key, animation=True):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        inserted = False

        # if tree is empty, then initialize root to the new node
        if not self.getRoot():
            self.createNode(key, None)
            self.cleanUp(callEnviron)
            return True

        # start at the root
        cur = self.getRoot()
        level = 1

        # create arrow
        if animation:
            arrow = self.createArrow(cur)
            callEnviron |= set(arrow)

        while not inserted:
            # if the key is to the left of current node, follow to the left
            if key < cur.getKey():
                # if no left child, insert on left
                if not self.getLeftChild(cur):
                    if animation:
                        # calculate where new node will be
                        coords = self.calculateCoordinates(cur, level, Child.LEFT)
                        # move arrow to new node
                        self.moveArrow(arrow, coords)
                        self.wait(0.2)

                    self.createNode(key, cur, Child.LEFT)
                    inserted = True
                cur = self.getLeftChild(cur)

            # otherwise, key must be to right of current node
            else:  
                if not self.getRightChild(cur):
                    if animation:
                        # calculate where new node will be
                        coords = self.calculateCoordinates(cur, level, Child.RIGHT)
                        # move arrow to new node
                        self.moveArrow(arrow, coords)
                        self.wait(0.2)

                    self.createNode(key, cur, Child.RIGHT)
                    inserted = True
                cur = self.getRightChild(cur)

            level+=1

            # move arrow
            if animation and not inserted:
                self.moveArrow(arrow, cur)
                self.wait(0.3)

            if level >= self.MAX_LEVEL and not inserted:
                if animation:
                    self.setMessage(
                        "Error! Cannot insert at level " + str(level) + 
                        " or below")
                self.cleanUp(callEnviron)
                return False

        self.cleanUp(callEnviron)
        return True

    def delete(self, key):
        # create a call environment and start the animations
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        # find the node with the key
        cur, parent = self.find(key, stopAnimations=False)

        # node with key does not exist
        if not cur: 
            result = None
            self.stopAnimations()
        else:
            # go through the process of deleting the item
            result = self.__delete(cur, callEnviron)
        self.cleanUp(callEnviron)
        return result
        
    def __delete(self, cur, callEnviron):

        #save the deleted key and its index
        deleted = cur.getKey()
        
        #determine the correct process for removing the node from the tree
        if self.getLeftChild(cur):
            if self.getRightChild(cur):    # cur has left and right child
                self.__promoteSuccessor(cur, callEnviron)
                self.removeNodeDrawing(cur) # Remove deleted node's canvas items
            else:                          # cur only has left child
                self.removeNodeDrawing(cur) # Remove deleted node's canvas items
                # get cur's left child that will be moving up
                curLeft = self.getLeftChild(cur)
                # remove current and promote left child
                self.removeAndReconnectNodes(cur, curLeft)
        else:                        # a right child exists or no children
            self.removeNodeDrawing(cur)  # Remove deleted node's canvas items
            # get cur's right child that will be moving up
            curRight = self.getRightChild(cur)
            # remove current and promote right child
            self.removeAndReconnectNodes(cur, curRight)

        return deleted
        
    def removeAndReconnectNodes(self, cur, curRightOrLeft):
        
        # 1. Note the indices of the current node and the child to move up
        curIndex, childIndex = self.getIndex(cur), self.getIndex(curRightOrLeft)

        # 2. delete the key and line to its parent 
        line = self.getLine(cur)
        if line:
            self.canvas.delete(line)
        elif curRightOrLeft and self.getLine(curRightOrLeft):
            self.canvas.delete(self.getLine(curRightOrLeft))
        self.removeNodeInternal(cur)

        # 3. move child subtree to be rooted at current node
        self.moveSubtree(curIndex, childIndex)

        # 4. move cur's right/left and its children up in the drawing
        #does cur have children?
        if curRightOrLeft:
            moveItems = [curRightOrLeft] + self.getAllDescendants(curRightOrLeft)
            self.restoreNodesPosition(moveItems)

        self.redrawLines()

    def __promoteSuccessor(self, node, callEnviron):
        successor = self.getRightChild(node)
        parent = node

        self.createHighlightedLine(successor, callEnviron=callEnviron)
                
        #hunt for the right child's most left child
        while self.getLeftChild(successor):
            parent = successor
            successor = self.getLeftChild(successor)
            
            self.wait(0.2)
            self.createHighlightedLine(successor, callEnviron=callEnviron)

        self.wait(0.2)
        highlight = self.createHighlightedCircle(
            successor, callEnviron=callEnviron)

        # replace node to delete with successor's key and data
        newSuccessor = self.copyNode(successor)
        callEnviron |= set((newSuccessor.drawable.display_shape,
                            newSuccessor.drawable.display_val))
        
        # a. internal replacement
        newSuccessor.coords = node.coords
        deletedIndex = self.getIndex(node)
        self.nodes[deletedIndex] = newSuccessor
        
        # b. drawing replacement
        self.restoreNodesPosition((newSuccessor,), includeLines=False)
        callEnviron -= set((newSuccessor.drawable.display_shape,
                            newSuccessor.drawable.display_val))
        self.removeNodeDrawing(node)
        self.canvas.delete(highlight)
        callEnviron.discard(highlight)

        # remove successor node
        self.__delete(successor, callEnviron)

    def validArgument(self):
        entered_text = self.getArgument()
        if entered_text and entered_text.isdigit():
            val = int(entered_text)
            if val < 100:
                return val
            else:
                self.setMessage("Input value must be an integer from 0 to 99.")

    def clickInsert(self):
        val = self.validArgument()
        if val:
            self.insertElem(val)
            self.window.update()
        self.clearArgument()

    def clickFind(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            result, parent = self.find(val)
            if result != None:
                msg = "Found {}!".format(val)
            else:
                msg = "Value {} not found".format(val)
            self.setMessage(msg)
        self.clearArgument()

    def clickFill(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            val = int(val)
            if val < 32:
                self.fill(val)
            else:
                self.setMessage("Input value must be an integer from 0 to 31.")
        self.clearArgument()

    def clickDelete(self):
        val = self.validArgument()
        if val < 100:
            deleted = tree.delete(val)
            msg = ("Deleted {}".format(val) if deleted else
                   "Value {} not found".format(val))
        else:
            msg = "Input value must be an integer from 0 to 99."
        self.setMessage(msg)
        self.clearArgument()
        
    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        fillButton = self.addOperation(
            "Fill", lambda: self.clickFill(), numArguments=1,
            validationCmd=vcmd)
        findButton = self.addOperation(
            "Find", lambda: self.clickFind(), numArguments=1,
            validationCmd=vcmd)
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1,
            validationCmd= vcmd)
        deleteButton = self.addOperation(
            "Delete", lambda: self.clickDelete(), numArguments=1,
            validationCmd= vcmd)
        #this makes the pause, play and stop buttons 
        self.addAnimationButtons()
        return [fillButton, findButton, 
                insertButton,deleteButton]

if __name__ == '__main__':
    random.seed(3.14159)  # Use fixed seed for testing consistency
    tree = BinaryTree()

    tree.runVisualization()
