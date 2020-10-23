from tkinter import *
try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *

class Queue(VisualizationApp):
    WIDTH = 800
    HEIGHT = 400
    CELL_SIZE = 50
    ARRAY_X0 = 100
    ARRAY_Y0 = 100
    nextColor = 0
    CELL_BORDER = 2
    CELL_BORDER_COLOR = 'black'
    MAX_CELLS = 12

    def __init__(              # Create a circular Queue visualization
            self, center=None, # centered at these coords (or canvas center)
            outerRadius=0.9,   # w/ outer and inner radius specified as either
            innerRadius=0.5,   # a fraction of the height or in pixels
            size=10,           # with a particular number of cells
            maxArgWidth=6,     # Maximum width of keys/values to show
            frontIndexColor='blue', # Colors for index displays or '' for none
            rearIndexColor='dark green',
            valueColor='black', 
            valueFont=('Helvetica', 16),
            variableColor='brown3',
            variableFont=('Courier', 14),
            numericIndexColor='gray40', # Color and font for numeric indices in
            numericIndexFont=('Courier', 11), # in cells and covered by values 
            title="Queue",
            **kwargs):
        kwargs['title'] = title
        kwargs['maxArgWidth'] = maxArgWidth
        super().__init__(**kwargs)
        self.list = [None]*size
        self.size = size
        self.nItems = 0
        self.front = 1  # when Queue is empty, front is one more than rear
        self.rear = 0
        self.frontIndexColor = frontIndexColor
        self.rearIndexColor = rearIndexColor
        self.valueColor = valueColor
        self.valueFont = valueFont
        self.variableColor = variableColor
        self.variableFont = variableFont
        self.numericIndexColor = numericIndexColor
        self.numericIndexFont = numericIndexFont
        if center is None:
            center = divide_vector(self.widgetDimensions(self.canvas), 2)
        self.center = tuple(map(int, center))
        minDimension = min(*self.center)
        self.innerRadius = (innerRadius * minDimension if innerRadius <= 1 else
                            innerRadus)
        self.outerRadius = (outerRadius * minDimension if outerRadius <= 1 else
                            outerRadus)
        self.textRadius = (self.innerRadius + self.outerRadius) / 2
        self.makeButtons()
        self.display()

    def __str__(self):
        return str(self.list)    
    # ANIMATION METHODS
    def createIndex(  # Create an arrow to point at a particuar cell
            self,     # cell with an optional name label
            index=-1,
            name=None,
            color=None,
            level=1): # Level controls arrow length to avoid overlapping labels
        if color == '':  # No color means no index created
            return tuple()
        elif color is None:
            color = self.variableColor
        arrow_coords = self.arrowCoords(index, level)
        arrow = self.canvas.create_line(
            *arrow_coords, arrow="last", fill=color)
        if name:
            label = self.canvas.create_text(
                arrow_coords[0], arrow_coords[1], text=name, 
                anchor=self.labelAnchor(arrow_coords, level),
                font=self.variableFont, fill=color)
        return (arrow, label) if name else (arrow,)

    # Arrow endpoint coordinates to point at cell
    # Level 1 is nearest inside inner radius, Level 2 is close to center
    # Negative levels are inside the array cell and is used for positioning the
    # numeric indices
    def arrowCoords(self, cellIndex, level=1):
        angle = (cellIndex + 0.5) * -self.sliceAngle
        tip = rotate_vector((self.innerRadius * 0.95, 0), angle)
        back = rotate_vector(
            (self.innerRadius - self.variableFont[1] * level * 2.8, 0),
            angle)
        return add_vector(self.center, back) + add_vector(self.center, tip)

    # Anchor for index label indexed on horizontal-vertical (0 or 1), then
    # (xSign, ySign, level % 2)
    anchors = [
        {(+1, +1, 0): SE, (-1, +1, 0): SW,
         (+1, +1, 1): NE, (-1, +1, 1): NW,
         (+1, -1, 0): SE, (-1, -1, 0): SW,
         (+1, -1, 1): NE, (-1, -1, 1): NW,
        },
        {(+1, +1, 0): SW, (-1, +1, 0): SW,
         (+1, +1, 1): SE, (-1, +1, 1): SE,
         (+1, -1, 0): NW, (-1, -1, 0): NW,
         (+1, -1, 1): NE, (-1, -1, 1): NE,
        },
        ]
    
    def labelAnchor(self, arrowCoords, level):
        return 'center'
        # vert = 1 if (abs(arrowCoords[1] - arrowCoords[3]) > 
        #              abs(arrowCoords[0] - arrowCoords[2])) else 0
        # ySign = +1 if arrowCoords[3] > arrowCoords[1] else -1
        # xSign = +1 if arrowCoords[2] > arrowCoords[0] else -1
        # return self.anchors[vert][(xSign, ySign, level % 2)]
    
    def moveIndexTo(
            self, indexItems, cellIndex, level, steps=10, sleepTime=0.02):
        '''Move an index arrow and optional label to the point at the cell
        indexed by cellIndex from its current position'''
        newArrowCoords = self.arrowCoords(cellIndex, level)
        self.moveItemsLinearly(indexItems, [newArrowCoords, newArrowCoords[:2]],
                         steps=steps, sleepTime=sleepTime)
        # if len(indexItems) > 1:
        #     newAnchor = self.labelAnchor(newArrowCoords, level)
        #     self.canvas.itemconfigure(indexItems[1], anchor=newAnchor)

    def sliceRange(self, index):
        index %= self.size
        return (self.sliceAngle * index, self.sliceAngle)
    
    def newCellValue(self, index, value, color=None):
        if color is None:
            color = drawable.palette[self.nextColor]
            # increment nextColor
            self.nextColor = (self.nextColor + 1) % len(drawable.palette)

        sliceRange = self.sliceRange(index)
        outerDelta = (self.outerRadius, self.outerRadius)
        arc = self.canvas.create_arc(
                *subtract_vector(self.center, outerDelta),
                *add_vector(self.center, outerDelta),
                start=sliceRange[0], extent = sliceRange[1],
                fill=color, width=0, outline='',
                style=PIESLICE, tags='value background')
        self.canvas.tag_lower(arc, 'cell')
        textDelta = rotate_vector(
            ((self.innerRadius + self.outerRadius) / 2, 0),
            (index + 0.5) * -self.sliceAngle)
        text = self.canvas.create_text(
            *add_vector(self.center, textDelta), text=value,
            font=self.valueFont, fill=self.valueColor)
        return (arc, text)
            
    # insert item at rear of queue   
    def insertRear(self, val):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        # increment rear
        self.rear += 1
        # deal with wraparound
        self.rear %= self.size

        # create new cell and cell value display objects
        # Start drawing new one at rear
        cellValue = self.newCellValue(self.rear, val)

       # insert the item
        self.list[self.rear] = drawable(val, 'color?', *cellValue)
        #increment number of items
        self.updateNItems(self.nItems + 1)
        if self.rearArrow:
            self.moveIndexTo(self.rearArrow, self.rear, self.rearLevel)

        # update window
        self.cleanUp(callEnviron)

    # remove the left element of the queue, or None if empty
    def removeFront(self):
        # if the queue is empty, exit
        if self.nItems == 0:
            self.setMessage('Queue is empty!')
            return None
        
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        #get the value at front
        n = self.list[self.front]

        # set front value to None so it will be garbage collected
        self.list[self.front] = None
        # delete the associated display objects
        self.canvas.delete(n.display_shape)
        self.canvas.delete(n.display_val)
        
        #increment front
        self.front += 1
        self.front %= self.size
        
        # decrement number of items
        self.updateNItems(self.nItems - 1)

        #move arrow
        if self.frontArrow:
            self.moveIndexTo(self.frontArrow, self.front, self.frontLevel)

        self.cleanUp(callEnviron)

    def display(self):
        self.canvas.delete("all")

        self.nItemsDisplay = self.canvas.create_text(
            self.center[0] - self.outerRadius, 
            self.center[1] - self.outerRadius,
            text='nItems: {}'.format(self.nItems), anchor=NW,
            font=self.variableFont, fill=self.variableColor)

        self.createCells(self.size)  # Draw grid of cells

        self.rearLevel = 1
        self.rearArrow = self.createIndex(
            self.rear, "rear", level=self.rearLevel, color=self.rearIndexColor)
        self.frontLevel = 2
        self.frontArrow = self.createIndex(
            self.front, "front", level=self.frontLevel, color=self.frontIndexColor)

    def updateNItems(self, newNItems):
        self.nItems = newNItems
        self.canvas.itemconfigure(
            self.nItemsDisplay, text='nItems: {}'.format(self.nItems))

    #disable insert if queue if full, disable delete if empty
    #enable everything else without overriding queue/deque functionality
    def onOffButtons(self):

        #disable buttons as necessary
        if self.nItems == self.size:
            self.insertButton.config(state = DISABLED)
        elif self.nItems==0:
            self.deleteButton.config(state = DISABLED)


# Button functions
    def clickNew(self):
        entered_text = self.getArgument()
        if not (entered_text.isdigit() and 1 < int(entered_text) and
                int(entered_text) <= self.MAX_CELLS):
            self.setMessage('New queue must have 2 - {} cells'.format(
                self.MAX_CELLS))
            return
        self.size = int(entered_text)
        self.list = [None] * self.size
        self.front = 1
        self.rear = 0
        self.nItems = 0
        self.display()
        
    def clickInsertRear(self):
        entered_text = self.getArgument()
        if self.nItems == self.size:
            self.setMessage('Queue is full!')
            self.clearArgument()
        elif entered_text:
            self.insertRear(entered_text)
            self.clearArgument()

    def startAnimations(self):
        self.onOffButtons()
        super().startAnimations()

    def makeButtons(self):
        vcmd = (self.window.register(makeWidthValidate(self.maxArgWidth)), '%P')
        self.insertButton = self.addOperation(
            "New", lambda: self.clickNew(), numArguments=1, validationCmd=vcmd)

        self.insertButton = self.addOperation(
            "Insert", lambda: self.clickInsertRear(), numArguments=1,
            validationCmd=vcmd)

        self.deleteButton = self.addOperation(
            "Delete", lambda: self.removeFront())
        self.addAnimationButtons()

    def createCells(self, nCells):  # Create a set of array cells in a circle
        self.sliceAngle = 360 / nCells
        outerDelta = (self.outerRadius, self.outerRadius)
        self.slices = [
            self.canvas.create_arc(
                *subtract_vector(self.center, outerDelta),
                *add_vector(self.center, outerDelta),
                start=self.sliceAngle * sliceI, extent = self.sliceAngle,
                fill='', width=self.CELL_BORDER, outline=self.CELL_BORDER_COLOR,
                style=PIESLICE, tags='cell')
            for sliceI in range(nCells)]
        if self.numericIndexColor and self.numericIndexFont:
            self.numericIndices = [
                self.canvas.create_text(
                    *self.arrowCoords(sliceI, -0.3)[:2], text=sliceI,
                    font=self.numericIndexFont, fill=self.numericIndexColor)
                for sliceI in range(nCells)]
                    
        innerDelta = (self.innerRadius, self.innerRadius)
        self.sliceCover = self.canvas.create_oval(
            *subtract_vector(self.center, innerDelta),
            *add_vector(self.center, innerDelta), fill='white', 
            width=self.CELL_BORDER, outline=self.CELL_BORDER_COLOR)

    def restoreIndices(self):
        if self.frontArrow:
            arrowCoords = self.arrowCoords(self.front, self.frontLevel)
            self.canvas.coords(self.frontArrow[0], *arrowCoords)
            self.canvas.coords(self.frontArrow[1], *arrowCoords[:2])
        if self.rearArrow:
            arrowCoords = self.arrowCoords(self.rear, self.rearLevel)
            self.canvas.coords(self.rearArrow[0], *arrowCoords)
            self.canvas.coords(self.rearArrow[1], *arrowCoords[:2])
        self.updateNItems(self.nItems)
        
    def cleanUp(self, *args, **kwargs): # Customize clean up for sorting
        super().cleanUp(*args, **kwargs) # Do the VisualizationApp clean up
        if len(self.callStack) == 0:
            self.restoreIndices()
        self.onOffButtons()       # disable buttons as necessary

if __name__ == '__main__':
    queue = Queue()

    try:
        queue.startAnimations()
        for item in sys.argv[1:]:
            queue.insertRear(item)
        queue.stopAnimations()
    except UserStop:
        queue.cleanUp()
        
    queue.runVisualization()
