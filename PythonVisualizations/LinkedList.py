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
    LL_X0 = 115
    LL_Y0 = 110
    MAX_SIZE=20
    LEN_ROW = 5
    ROW_GAP = 50  
    MAX_ARG_WIDTH = 8
    SORTED_BACKGROUND = 'honeydew3'
    UNSORTED_BACKGROUND = 'powder blue'
    
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
        self.linkedListNode(self.sorted.get())
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
                self.list[pos - 1].nextPointer = arrow
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
        if nextNode in self.list and isinstance(coordsOrPos, int):
            nextNodeIndex = self.list.index(nextNode)
            linkPointer = (self.linkNext(coordsOrPos,
                                         nextNodeIndex - coordsOrPos,
                                         updateInternal=updateInternal), )
        else:
            linkPointer = ()
        return (cell_rect, cell_text, cell_dot) + linkPointer

    # Creates the LinkedList of SortedList "node" that is the head of the list
    def linkedListNode(self, sorted):
        x, y = self.x_y_offset(0)
        rect = self.canvas.create_rectangle(
            x + self.CELL_WIDTH * 2 // 3, y,
            x + self.CELL_WIDTH, y + self.CELL_HEIGHT,
            fill=self.SORTED_BACKGROUND if sorted else self.UNSORTED_BACKGROUND,
            tags=("LinkedList", "cell"))
        oval = self.createDot(0, 'LinkedList')
        ovalCoords = self.canvas.coords(oval)
        firstText = self.canvas.create_text(
            (ovalCoords[0] + ovalCoords[2]) / 2, (y + ovalCoords[1]) / 2,
            text="first", font=('Courier', -10))
        nameText = self.canvas.create_text(
            x, y + self.CELL_HEIGHT // 2, font=('Courier', -14),
            text='SortedList' if sorted else 'LinkedList')
        
    ### ANIMATION METHODS###
    def indexCoords(self, pos, level=0):
        tip = self.indexTip(pos)
        delta = (0, self.CELL_SIZE // 5) if pos >= 0 else (
            self.CELL_SIZE * 4 // 5, 0)
        offset = V(0, abs(self.VARIABLE_FONT[1])) * level
        start = V(V(tip) - V(delta)) - V(offset)
        return (*start, *tip)

    def indexLabelCoords(self, pos, level=0):
        arrowCoords = self.indexCoords(pos, level)
        return arrowCoords[:2]
        
    def createIndex(self, pos, name=None, level=0):
        arrow = self.canvas.create_line(
            *self.indexCoords(pos, level), arrow="last",
            fill=self.VARIABLE_COLOR)
        if name:
            name = self.canvas.create_text(
                *self.indexLabelCoords(pos, level), text=name,
                font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR,
                anchor=SW if pos >= 0 else E)
        return (arrow, name) if name else (arrow,)
                
    def getFirst(self):    # returns the value the first link in the list
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        firstIndex = self.createIndex(1, name='first')
        callEnviron |= set(firstIndex)

        outputBoxCoords = self.outputBoxCoords(full=False)
        callEnviron.add(self.createOutputBox(full=False))
        
        textX = (outputBoxCoords[0] + outputBoxCoords[2]) // 2
        textY = (outputBoxCoords[1] + outputBoxCoords[3]) // 2
        
        firstText = self.canvas.create_text(
            *self.cellText(1), text=self.list[0].key,
            font=self.VALUE_FONT, fill=self.VALUE_COLOR)
        callEnviron.add(firstText)
        self.moveItemsTo(firstText, (textX, textY), sleepTime = 0.05)

        self.cleanUp(callEnviron)        
        return self.list[0].key

    def outputBoxCoords(self, full=False):
        return (self.LL_X0 // 2, self.LL_Y0 // 6,
                self.LL_X0 // 2 + (self.CELL_WIDTH + self.CELL_GAP) *
                (self.LEN_ROW if full else 1),
                self.LL_Y0 // 6 + self.CELL_HEIGHT)
    
    def createOutputBox(self, full=False):
        return self.canvas.create_rectangle(
            *self.outputBoxCoords(full), fill = self.OPERATIONS_BG)

    def traverse(self):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        outputBoxCoords = self.outputBoxCoords(full=True)
        callEnviron.add(self.createOutputBox(full=True))

        link = 1
        linkIndex = self.createIndex(link, name='link')
        callEnviron |= set(linkIndex)

        outputFont = ('Courier', -18)
        outX = outputBoxCoords[0] + abs(outputFont[1])
        outY = outputBoxCoords[1] + abs(outputFont[1])

        sepX = self.textWidth(outputFont, ' ')
        sepY = self.textHeight(outputFont, ' ')
        while link <= len(self.list):
            if link > 1:
                self.moveItemsTo(
                    linkIndex,
                    (self.indexCoords(link), self.indexLabelCoords(link)),
                    sleepTime=0.02)
            linkText = text=self.list[link - 1].key
            tx = self.textWidth(outputFont, linkText)
            textItem = self.canvas.create_text(
                *(V(self.cellText(link)) - V((tx / 2, sepY / 2))),
                text=linkText, font=outputFont, anchor=W)
            callEnviron.add(textItem)
            self.moveItemsTo(textItem, (outX, outY), sleepTime = 0.05)
            outX += tx + sepX
            link += 1

        self.cleanUp(callEnviron)
            
    # Erases old linked list and draws empty list
    def newLinkedList(self):
        self.first = None
        self.list = []
        self.display()
    
    def insertElem(       # Insert a new Link node at the front of the linked
            self, val):   # list with a specific value
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        previous = 0
        if self.sorted.get():  # For sorted lists, find insertion point
            goal = self.createIndex(-1, 'goal')
            coords = V(self.cellCoords(-1)[:2]) + V((0, self.CELL_HEIGHT // 2))
            goal += (self.canvas.create_text(
                *coords, text=val, anchor=W,
                font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR), )
            callEnviron |= set(goal)

            previousIndex = self.createIndex(previous, 'previous')
            callEnviron |= set(previousIndex)
            while (previous < len(self.list) and
                   self.list[previous].key < val):
                self.wait(0.2)     # Pause for comparison
                previous += 1
                self.moveItemsTo(
                    previousIndex, 
                    (self.indexCoords(previous), 
                     self.indexLabelCoords(previous)),
                    sleepTime=0.02)
                
            self.wait(0.2)     # Pause for final comparison
            callEnviron -= set(goal)
            for item in goal:
                self.canvas.delete(item)
            self.wait(0.2)
            
        linkIndex = self.createIndex(
            -1, 'newLink' if self.sorted.get() else 'link')
        callEnviron |= set(linkIndex)

        nodeID = self.generateID()
        newNode = Node(
            val, self.first, nodeID,
            *self.createLink(
                -1, val, nodeID, 
                nextNode=self.list[previous] if previous < len(self.list) else None))
        callEnviron |= set(newNode.items())
        self.wait(0.2)
        
        toMove = newNode.items()
        for node in self.list[previous:]:
            toMove.extend(node.items())
        toCoords = [self.canvas.coords(item) for node in self.list[previous:]
                    for item in node.items()] + self.linkCoords(
                            len(self.list) + 1)
        # When list already contains some items, splice in the target 
        # coordinates for the final next pointer
        if previous < len(self.list):
            toCoords[-3:-3] = [self.nextLinkCoords(len(self.list))]
        self.moveItemsLinearly(toMove, toCoords, sleepTime=0.02)
        self.list[previous:previous] = [newNode]
        callEnviron -= set(newNode.items())
                       
        if self.first is None:   # For first link, add next pointer from head
            self.linkNext(0)
        elif previous >= len(self.list) - 1: # Insertion at end 
            self.linkNext(previous) # requires new pointer from last link
            
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
                self.moveItemsTo(
                    linkIndex, 
                    (self.indexCoords(link), self.indexLabelCoords(link)),
                    sleepTime=0.02)
                
            self.wait(0.2)     # Pause for comparison
            found = self.list[previous].key == goal
            if found or (self.sorted.get() and self.list[previous].key > goal):
                if found:
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
                        self.moveItemsLinearly(toMove, toCoords, sleepTime=0.05)
                        self.wait(0.1)
                    elif updateFirst:
                        self.canvas.delete(self.first)
                        self.first = None
                    else:
                        self.canvas.delete(self.list[previous - 1].nextPointer)
                        self.list[previous - 1].nextPointer = None

                    # Remove Link with goal key and link index
                    self.moveItemsOffCanvas(self.list[previous].items() + 
                                            [foundHighlight] + list(linkIndex),
                                            sleepTime=0.01)
                    callEnviron |= set(self.list[previous].items())
                    self.list[previous:link] = []

                    # Reposition all remaining links
                    self.restorePositions()
                    
                # Exit delete if item found or sorted list passed goal location
                self.cleanUp(callEnviron)
                return goal if found else None

            # Advance to next Link
            previous = link
            self.moveItemsTo(
                previousIndex,
                (self.indexCoords(previous, level=1), 
                 self.indexLabelCoords(previous, level=1)),
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

        sorted = self.sorted.get()
        link = 1
        linkIndex = self.createIndex(link, 'link')
        callEnviron |= set(linkIndex)

        while link <= len(self.list):
            if link > 1:
                self.moveItemsTo(
                    linkIndex, 
                    (self.indexCoords(link), self.indexLabelCoords(link)),
                    sleepTime=0.02)
                
            self.wait(0.2)     # Pause for comparison
            linkKey = self.list[link - 1].key
            if linkKey == goal or (sorted and goal < linkKey):
                self.cleanUp(callEnviron)
                return link if linkKey == goal else None

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

    def clickTraverse(self):
        self.traverse()
        if self.isEmpty():
            self.setMessage('No Links in list to traverse')
    
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
        newLinkedListButton = self.addOperation(
            "New", lambda: self.clickNewLinkedList())
        self.sorted = IntVar()
        self.sorted.set(0)
        sortedButton = self.addOperation(
            "Sorted", lambda: self.clickNewLinkedList(),
            buttonType=Checkbutton, variable=self.sorted)
        deleteFirstButton = self.addOperation(
            "Delete First", lambda: self.clickDeleteFirst())
        getFirstButton = self.addOperation(
            "Get First", lambda: self.clickGetFirst())
        traverseButton = self.addOperation(
            "Traverse", lambda: self.clickTraverse())
        self.addAnimationButtons()
    
        return [searchButton, insertButton, deleteButton, deleteFirstButton,
                newLinkedListButton, sortedButton, getFirstButton,
                traverseButton]
            
    ##allow letters or numbers to be typed in                  
    def validate(self, action, index, value_if_allowed,
                             prior_value, text, validation_type, trigger_type, widget_name):
        return len(value_if_allowed)<= self.maxArgWidth
   
if __name__ == '__main__':
    ll = LinkedList()
    try:
        for arg in reversed(sys.argv[1:]):
            ll.insertElem(arg)
            ll.cleanUp()
    except UserStop:
        ll.cleanUp()
    ll.runVisualization()
    
