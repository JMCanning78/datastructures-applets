import time
from tkinter import *
import math
try:
    from drawable import *
    from coordinates import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .coordinates import *
    from .VisualizationApp import *

V = vector

class Node(object):
    
    # create a linked list node
    #id is used to link the different parts of each node visualization
    def __init__(
            self, k, nextNode=None, id='',
            cell=None, value=None, dot=None, nextPointer=None):
        self.key = k
        self.id = id
        self.next = nextNode  # reference to next item in list
        self.cell = cell
        self.value = value
        self.dot = dot
        self.nextPointer = nextPointer

    def items(self):    # Return list of canvas items used to draw Node
        return [i for i in (self.cell, self.value, self.dot, self.nextPointer)
                if i is not None]
        
    def __str__(self):
        return "{" + str(self.key) + "}"

class LinkedList(VisualizationApp):
    nextColor = 0
    WIDTH = 800
    HEIGHT = 400
    CELL_SIZE = 50
    CELL_BORDER = 2 
    CELL_WIDTH = 120
    CELL_HEIGHT = 50
    CELL_GAP = 20
    DOT_SIZE = 10
    LL_X0 = 100
    LL_Y0 = 100
    MAX_SIZE=20
    LEN_ROW = 5
    ROW_GAP = 50  
    MAX_ARG_WIDTH = 8
    
    def __init__(self, title="Linked List", maxArgWidth=MAX_ARG_WIDTH, **kwargs):
        super().__init__(title=title, maxArgWidth = maxArgWidth, **kwargs)
        self.title = title        
        self.first = None   # Canvas ID for first pointer arrow
        self.list = []      # List of Link nodes in linked list
        self.prev_id = -1
        self.buttons = self.makeButtons()
        self.display()
        self.canvas.bind('<Configure>', self.resizeCanvas)

    def __len__(self):
        return len(self.list)

    def isEmpty(self):
        return not self.first
    
    def generateID(self):
        self.prev_id+=1
        return "item" + str(self.prev_id)
    
    # Calculate coordinates of cell parts
    # Position 0 is the LinkedList cell.  The Links start at postiion 1
    # Negative position means above the Linked List node 
    def x_y_offset(self, pos):
        x_offset = self.LL_X0 + max(0, pos) % self.LEN_ROW * (
            self.CELL_WIDTH + self.CELL_GAP)
        y_offset = self.LL_Y0 + max(-1, pos) // self.LEN_ROW * (
            self.CELL_HEIGHT + self.ROW_GAP) 
        return x_offset, y_offset
    
    def indexTip(self, pos): # Compute position of index pointer tip
        if pos == 0:
            nextDotCenter = self.cellNext(pos)
            return V(nextDotCenter) - V((0, self.CELL_HEIGHT // 2))
        return V(self.x_y_offset(pos)) + ( # Goes to middle top for normal
            V((self.CELL_WIDTH // 2, 0)) if pos > 0 else # position, else
            V((0, self.CELL_HEIGHT // 2))) # left middle for pos == -1

    def cellCoords(self, pos):  # Bounding box for a Link node rectangle
        x, y = self.x_y_offset(pos)
        return x, y, x + self.CELL_WIDTH, y + self.CELL_HEIGHT

    # Calculate coordinates for the center of a Link node's text
    def cellText(self, pos):
        x, y = self.x_y_offset(pos)
        return x + self.CELL_HEIGHT, y + self.CELL_HEIGHT // 2

    # Calculate coordinates for the center of a node's next pointer
    def cellNext(self, pos):
        x, y = self.x_y_offset(pos)
        return x + self.CELL_HEIGHT * 2, y + self.CELL_HEIGHT // 2

    def nextDot(self, pos):  # Bounding box for the dot of the next pointer
        x, y = self.cellNext(pos)
        radius = self.DOT_SIZE // 2
        return x - radius, y - radius, x + radius, y + radius
    
    def display(self):      # Set up the permanent canvas items
        self.canvas.delete('all')
        self.linkedListNode()
        if self.first:      # If there was a displayed first pointer, recreate
            self.first = self.linkNext(0)
            
    def resizeCanvas(self, event=None):   # Handle canvas resize events
        if self.canvas and self.canvas.winfo_ismapped():
            width, height = self.widgetDimensions(self.canvas)
            new_row_length = max(2, (width - self.LL_X0 + self.CELL_GAP) // (
                self.CELL_WIDTH + self.CELL_GAP))
            change = self.LEN_ROW != new_row_length
            self.LEN_ROW = new_row_length
            if change:
                self.restorePositions()
    
    # Create a dot for the next pointer of a Link or LinkedList node
    def createDot(self, coordsOrPos, id):
        coords = (coordsOrPos if isinstance(coordsOrPos, (list, tuple))
                  else self.nextDot(coordsOrPos))
        return self.canvas.create_oval(
            *coords, fill="RED", outline="RED", tags=('next dot', id))

    # Compute coordinaes of the link pointer from pos to pos+d (where d is
    # usually 1)
    # When pos is 0, creates the arrow for the LinkedList first pointer
    # and pos -1 creates an arrow for a new node above the LinkedList
    def nextLinkCoords(self, pos, d=1):
        cell0 = self.cellNext(pos)
        cell1 = self.cellNext(max(1, pos + d))
        spansRows = cell1[1] > cell0[1] # Flag if next cell is on next row
        # Determine position for the tip of the arrow
        tip = V(cell1) - V(
            (0, self.CELL_HEIGHT // 2) if spansRows else 
            (self.CELL_HEIGHT * 2, 0))
        delta = V(V(tip) - V(cell0)) * 0.33
        p0 = cell0
        p1 = V(cell0) + (
            V((0, (self.CELL_HEIGHT + self.ROW_GAP) // 2)) if spansRows else
            V(delta))
        p2 = V(tip) - (V((0, self.ROW_GAP // 2)) if spansRows else V(delta))
        return (*p0, *p1, *p2, *tip)

    # Create the arrow linking a Link node to the next Link
    def linkNext(self, pos, d=1, updateInternal=True):
        arrow = self.canvas.create_line(
            *self.nextLinkCoords(pos, d), arrow=LAST, tags=('link pointer', ))
        if updateInternal:
            if pos <= 0:
                self.first = arrow
            else:
                self.list[pos].nextPointer = arrow
        return arrow
    
    #accesses the next color in the pallete
    #used to assign a node's color
    def chooseColor(self):
        color = drawable.palette[self.nextColor]
        self.nextColor = (self.nextColor + 1) % len(drawable.palette)
        return color
    
    def linkCoords(self, pos): # Return coords for cell, text, and dot of a Link
        return [self.cellCoords(pos), self.cellText(pos), self.nextDot(pos)]

    def createLink(           # Create  the canvas items for a Link node
            self,             # This will be placed according to coordinates
            coordsOrPos=-1,   # or list index position (-1 = above position 1)
            val='', id='link', color=None, nextNode=None, updateInternal=False):
        coords = (coords if isinstance(coordsOrPos, (list, tuple)) 
                  else self.linkCoords(coordsOrPos))
        if color == None:
            color = self.chooseColor()
        cell_rect = self.canvas.create_rectangle(
            *coords[0], fill= color, tags=('cell', id))
        cell_text = self.canvas.create_text(
            *coords[1], text=val, font=self.VALUE_FONT, fill=self.VALUE_COLOR,
            tags = ('cell', id))
        cell_dot = self.createDot(coords[2], id)
        self.canvas.tag_bind(id, '<Button>', 
                             lambda e: self.setArgument(str(val)))
        linkPointer = (
            (self.linkNext(coordsOrPos, updateInternal=updateInternal), ) 
            if nextNode and isinstance(coordsOrPos, int) else ())
        return (cell_rect, cell_text, cell_dot) + linkPointer

    # Creates the LinkedList "node" that is the head of the linked list
    def linkedListNode(self):
        x, y = self.x_y_offset(0)
        rect = self.canvas.create_rectangle(
            x + self.CELL_WIDTH * 2 // 3, y,
            x + self.CELL_WIDTH, y + self.CELL_HEIGHT,
            fill="gainsboro", tags=("LinkedList", "cell"))
        oval = self.createDot(0, 'LinkedList')
        ovalCoords = self.canvas.coords(oval)
        text = self.canvas.create_text(
            (ovalCoords[0] + ovalCoords[2]) / 2, (y + ovalCoords[1]) / 2,
            text="first", font=('Courier', '10'))
        
    ### ANIMATION METHODS###
    def indexCoords(self, pos, level=0):
        tip = self.indexTip(pos)
        delta = (0, self.CELL_SIZE // 5) if pos >= 0 else (
            self.CELL_SIZE * 4 // 5, 0)
        offset = V(0, self.VARIABLE_FONT[1]) * level
        start = V(V(tip) - V(delta)) - V(offset)
        return (*start, *tip)
        
    def createIndex(self, pos, name=None, level=0):
        indexCoords = self.indexCoords(pos, level)
        arrow = self.canvas.create_line(
            *indexCoords, arrow="last", fill=self.VARIABLE_COLOR)
        if name:
            name = self.canvas.create_text(
                *indexCoords[:2], text=name, font=self.VARIABLE_FONT, 
                fill=self.VARIABLE_COLOR, anchor=SW if pos >= 0 else SE)
        return (arrow, name) if name else (arrow,)
                
    def getFirst(self):    # returns the value the first link in the list
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        firstIndex = self.createIndex(1, name='first')
        callEnviron |= set(firstIndex)

        peekBoxCoords = self.peekBoxCoords()
        peekBox = self.createPeekBox()
        callEnviron.add(peekBox)
        
        textX = (peekBoxCoords[0] + peekBoxCoords[2]) // 2
        textY = (peekBoxCoords[1] + peekBoxCoords[3]) // 2
        
        firstText = self.canvas.create_text(
            *self.cellText(1), text=self.list[0].key,
            font=self.VALUE_FONT, fill=self.VALUE_COLOR)
        callEnviron.add(firstText)
        self.moveItemsTo(firstText, (textX, textY), sleepTime = 0.05)

        self.cleanUp(callEnviron)        
        return self.list[0].key

    def peekBoxCoords(self):
        return (self.LL_X0 // 2, self.LL_Y0 // 4,
                self.LL_X0 // 2 + self.CELL_WIDTH + self.CELL_GAP,
                self.LL_Y0 // 4 + self.CELL_HEIGHT)
    
    def createPeekBox(self):
        return self.canvas.create_rectangle(
            *self.peekBoxCoords(), fill = self.OPERATIONS_BG)
            
    # Erases old linked list and draws empty list
    def newLinkedList(self):
        self.first = None
        self.list = []
        self.display()
    
    def insertElem(      # Insert a new Link node at the front of the linked
            self, val):   # list with a specific value
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        linkIndex = self.createIndex(-1, 'link')
        callEnviron |= set(linkIndex)

        nodeID = self.generateID()
        newNode = Node(val, self.first, nodeID,
                       *self.createLink(-1, val, nodeID, nextNode=self.first))
        callEnviron |= set(newNode.items())
        toMove = newNode.items()
        for node in self.list:
            toMove.extend(node.items())
        toCoords = [self.canvas.coords(item) for node in self.list
                    for item in node.items()] + self.linkCoords(
                            len(self.list) + 1)
        # When list already contains some items, splice in the target 
        # coordinates for the last link
        if len(self.list) > 0:
            toCoords[-3:-3] = [self.nextLinkCoords(len(self.list))]
        self.moveItemsLinearly(toMove, toCoords, sleepTime=0.02)
        self.list[:0] = [newNode]
        callEnviron -= set(newNode.items())
                       
        if self.first is None:
            self.linkNext(0)
            
        self.cleanUp(callEnviron)
        return val 
    
    #deletes first node in Linked List
    def deleteFirst(self):
        self.delete(self.list[0].key)
    
    # Delete a link from the linked list by finding a matching goal key
    def delete(self, goal):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        previous = 0
        previousIndex = self.createIndex(previous, 'previous', level=1)
        callEnviron |= set(previousIndex)
        link = 1
        linkIndex = self.createIndex(link, 'link')
        callEnviron |= set(linkIndex)

        while previous < len(self.list):

            link = previous + 1
            if link > 1:
                indexCoords = self.indexCoords(link)
                self.moveItemsTo(linkIndex, (indexCoords, indexCoords[:2]),
                                 sleepTime=0.02)
                
            self.wait(0.2)     # Pause for comparison
            if self.list[previous].key == goal:
                foundHighlight = self.createFoundHighlight(link)
                callEnviron.add(foundHighlight)
                                
                # Prepare to update next pointer from previous
                updateFirst = previous == 0
                nextPointer = self.list[previous].nextPointer
                if nextPointer:
                    toMove = (self.first if updateFirst else
                              self.list[previous - 1].nextPointer)
                    toCoords = self.nextLinkCoords(previous, d=2)
                    self.canvas.tag_raise(toMove)
                    self.moveItemsTo(toMove, toCoords, sleepTime=0.04)
                elif updateFirst:
                    self.canvas.delete(self.first)
                    self.first = None
                else:
                    self.canvas.delete(self.list[previous - 1].nextPointer)
                    self.list[previous - 1].nextPointer = None

                # Remove Link with goal key
                self.moveItemsOffCanvas(
                    self.list[previous].items() + [foundHighlight],
                    sleepTime=0.01)
                self.list[previous:link] = []
                callEnviron |= set(self.list[previous].items())

                # Reposition all remaining links
                self.restorePositions()
                self.cleanUp(callEnviron)
                return goal

            # Advance to next Link
            previous = link
            indexCoords = self.indexCoords(previous, level=1)
            self.moveItemsTo(
                previousIndex, (indexCoords, indexCoords[:2]),
                sleepTime = 0.02)
            
        # Failed to find goal key
        self.cleanUp(callEnviron)
        
        # otherwise highlight the found node
        # x_offset, y_offset = self.x_y_offset(pos)
        # cell_outline = self.canvas.create_rectangle(
        #     x_offset-5, y_offset-5,
        #     self.CELL_WIDTH + x_offset+5, self.CELL_HEIGHT+y_offset+5,
        #     outline = "RED", tag=id)
        
    def restorePositions(  # Move all links on the canvas to their correct
            self, sleepTime=0.01): # positions 
        if self.first:
            items = [self.first]
            toCoords = [self.nextLinkCoords(0)]
            for i, node in enumerate(self.list):
                items.extend(node.items())
                toCoords.extend(self.linkCoords(i + 1))
                if node.nextPointer:
                    toCoords.append(self.nextLinkCoords(i + 1))
            if sleepTime > 0:
                try:
                    self.startAnimations()
                    self.moveItemsLinearly(items, toCoords, sleepTime=sleepTime)
                    self.stopAnimations()
                except UserStop:
                    pass
            else:
                for item, coords in zip(items, toCoords):
                    self.canvas.coords(item, coords)
                    
    def cleanUp(self,   # Customize cleanup to restore link positions
                callEnvironment=None, stopAnimations=True):
        super().cleanUp(callEnvironment, stopAnimations)
        if len(self.callStack) == 0:
            self.restorePositions(sleepTime=0)

    def find(self, goal):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        link = 1
        linkIndex = self.createIndex(link, 'link')
        callEnviron |= set(linkIndex)

        while link <= len(self.list):
            if link > 1:
                indexCoords = self.indexCoords(link)
                self.moveItemsTo(linkIndex, (indexCoords, indexCoords[:2]),
                                 sleepTime=0.02)
                
            self.wait(0.2)     # Pause for comparison
            if self.list[link - 1].key == goal:

                self.cleanUp(callEnviron)
                return link

            # Advance to next Link
            link += 1
            
        # Failed to find goal key
        self.cleanUp(callEnviron)
        
    def search(self, goal):
        self.startAnimations()
        callEnviron = self.createCallEnvironment()

        link = self.find(goal)
        linkIndex = self.createIndex(0 if link is None else link, 'link')
        callEnviron |= set(linkIndex)

        if link is not None:
            callEnviron.add(self.createFoundHighlight(link))
            self.wait(0.5)

        self.cleanUp(callEnviron)
        return goal if link else None
            
    def createFoundHighlight(self, pos): # Highlight the Link cell at pos
        bbox = self.cellCoords(pos)
        return self.canvas.create_rectangle(
            *bbox, fill='', outline=self.FOUND_COLOR, width=4,
            tags='found item')
    
    ### BUTTON FUNCTIONS##
    def clickSearch(self):
        val = self.getArgument()
        result = self.search(val)
        if result != None:
            msg = "Found {}!".format(val)
        else:
            msg = "Value {} not found".format(val)
        self.setMessage(msg)
        self.clearArgument()
    
    def clickInsert(self):
        val = self.getArgument()
        if len(self) >= self.MAX_SIZE:
            self.setMessage("Error! Linked List is already full.")
            self.clearArgument()
        else:  
            self.insertElem(val)

    def clickDelete(self):
        val = self.getArgument()
        if not self.first:
            msg = "ERROR: Linked list is empty"
        else:
            result = self.delete(val)
            if result != None:
                msg = "{} Deleted!".format(val)
            else:
                msg = "Value {} not found".format(val)
        self.setMessage(msg)
        self.clearArgument()
        
    def clickDeleteFirst(self):
        if not self.first: 
            msg = "ERROR: Linked list is empty"
        else:
            self.deleteFirst()
            msg = "first node deleted"
        self.setMessage(msg)
        self.clearArgument()
        
    def clickNewLinkedList(self):
        self.newLinkedList()
    
    def clickGetFirst(self):
        if self.isEmpty():
            msg = "ERROR: Linked list is empty!"
        else:
            first = self.getFirst()
            msg = "The first link's data is {}".format(first)
            self.setArgument(first)
        self.setMessage(msg)
    
    def makeButtons(self):
        vcmd = (self.window.register(self.validate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        searchButton = self.addOperation(
            "Search", lambda: self.clickSearch(), numArguments=1,
            validationCmd=vcmd)
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1,
            validationCmd=vcmd)
        deleteButton = self.addOperation(
            "Delete", lambda: self.clickDelete(), numArguments=1,
            validationCmd=vcmd)
        self.addAnimationButtons()
        deleteFirstButton = self.addOperation("Delete First", lambda: self.clickDeleteFirst(), 
                                              numArguments = 0, validationCmd = vcmd, maxRows = 3)
        newLinkedListButton = self.addOperation(
            "New", lambda: self.clickNewLinkedList(), 
            numArguments = 0, validationCmd =vcmd, maxRows = 3)
        getFirstButton = self.addOperation(
            "Get First", lambda: self.clickGetFirst(), numArguments = 0,
            validationCmd=vcmd, maxRows = 3)

    
        return [searchButton, insertButton, deleteButton, deleteFirstButton, newLinkedListButton, getFirstButton]         

            
    ##allow letters or numbers to be typed in                  
    def validate(self, action, index, value_if_allowed,
                             prior_value, text, validation_type, trigger_type, widget_name):
        return len(value_if_allowed)<= self.maxArgWidth
   
if __name__ == '__main__':
    ll = LinkedList()
    for arg in reversed(sys.argv[1:]):
        ll.insertElem(arg)
        ll.cleanUp()
    ll.runVisualization()
    
