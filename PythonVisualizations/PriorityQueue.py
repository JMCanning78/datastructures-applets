import random
from tkinter import *

try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *


class PriorityQueue(VisualizationApp):
    CELL_SIZE = 50
    CELL_BORDER = 2
    CELL_BORDER_COLOR = 'black'
    ARRAY_X0 = 100
    ARRAY_Y0 = 100

    nextColor = 0

    def __init__(self, size=12, title="Priority Queue", **kwargs):
        super().__init__(title=title, **kwargs)
        self.size = size
        self.title = title
        self.list = [None]*self.size
        self.nItems = 0
        self.index = None
        self.buttons = self.makeButtons()
        
        self.display()

    def __str__(self):
        return str(self.list)

    # ARRAY FUNCTIONALITY

    def createIndex(self, index,  # cell
                    name=None,  # with an optional name label
                    level=1,  # at a particular level away from the cells
                    color=None):  # (negative are below)
        if not color: color = self.VARIABLE_COLOR

        cell_coords = self.cellCoords(index)
        cell_center = self.cellCenter(index)
        level_spacing = abs(self.VARIABLE_FONT[1])
        x = cell_center[0]
        if level > 0:
            y0 = cell_coords[1] - self.CELL_SIZE * 3 // 5 - level * level_spacing
            y1 = cell_coords[1] - self.CELL_SIZE * 3 // 10
        else:
            y0 = cell_coords[3] + self.CELL_SIZE * 3 // 5 - level * level_spacing
            y1 = cell_coords[3] + self.CELL_SIZE * 3 // 10
        arrow = self.canvas.create_line(
            x, y0, x, y1, arrow="last", fill=color)
        if name:
            label = self.canvas.create_text(
                x + 2, y0, text=name, anchor=SW if level > 0 else NW,
                font=self.VARIABLE_FONT, fill=color)
        return (arrow, label) if name else (arrow,)

    def insert(self, val):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()
        j = self.nItems - 1  # Start at front

        indexJ = self.createIndex(j, 'j', level=-2)
        callEnviron |= set(indexJ)

        #self.list[j] = drawable(None)
        self.list[self.nItems] = drawable(None)
        
        self.wait(1)
            
        while j >= 0 and val >= self.list[j].val:  # Move bigger items right

            self.assignElement(j, j+1, callEnviron)
            self.list[j+1].val = self.list[j].val
            j -= 1
            self.moveItemsBy(indexJ, (-self.CELL_SIZE, 0), sleepTime=0.1)  # Move "j" arrow
            self.wait(1)
            
        # Location of the new cell in the array
        toPositions = (self.cellCoords(j+1),
                       self.cellCenter(j+1))

        # Animate arrival of new value from operations panel area
        canvasDimensions = self.widgetDimensions(self.canvas)
        startPosition = [canvasDimensions[0] // 2, canvasDimensions[1]] * 2
        startPosition = add_vector(startPosition, (0, 0, self.CELL_SIZE, self.CELL_SIZE))
        cellPair = self.createCellValue(startPosition, val)
        callEnviron |= set(cellPair)  # Mark new cell as temporary
        self.moveItemsTo(cellPair, toPositions, steps=self.CELL_SIZE, sleepTime=0.01)
        self.list[j+1] = drawable(
            val, self.canvas.itemconfigure(cellPair[0], 'fill')[-1], *cellPair)
        callEnviron -= set(cellPair)  # New cell is no longer temporary

        self.nItems += 1
        self.moveItemsBy(self.index, (self.CELL_SIZE, 0), sleepTime=0.01)

        self.window.update()  
        self.cleanUp(callEnviron) 
        self.stopAnimations()


    def peek(self):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        # draw output box
        canvasDimensions = self.widgetDimensions(self.canvas)
        spacing = self.CELL_SIZE * 3 // 4
        padding = 10
        outputBox = self.canvas.create_rectangle(
            (canvasDimensions[0] - self.nItems * spacing - padding) // 2,
            canvasDimensions[1] - self.CELL_SIZE - padding,
            (canvasDimensions[0] + self.nItems * spacing + padding) // 2,
            canvasDimensions[1] - padding,
            fill=self.OPERATIONS_BG)
        callEnviron.add(outputBox)

        self.wait(0.3)

        # calculate where the value will need to move to
        outputBoxCoords = self.canvas.coords(outputBox)
        midOutputBox = (outputBoxCoords[3] + outputBoxCoords[1]) // 2

        # create the value to move to output box
        valueOutput = self.copyCanvasItem(self.list[self.nItems-1].display_val)
        valueList = (valueOutput,)
        callEnviron.add(valueOutput)

        # move value to output box
        toPositions = (outputBoxCoords[0] + padding / 2 + (1 / 2) * spacing,
                       midOutputBox)
        self.moveItemsTo(valueList, (toPositions,), sleepTime=.02)

        # make the value 25% smaller
        newSize = (self.VALUE_FONT[0], int(self.VALUE_FONT[1] * .75))
        self.canvas.itemconfig(valueOutput, font=newSize)

        self.wait(0.3)
        self.cleanUp(callEnviron)

    def assignElement(
            self, fromIndex, toIndex, callEnviron,
            steps=CELL_SIZE // 2, sleepTime=0.01):
        fromDrawable = self.list[fromIndex]

        # get positions of "to" cell in array
        toPositions = (self.cellCoords(toIndex), self.cellCenter(toIndex))

        # create new display objects as copies of the "from" cell and value
        newCell = self.copyCanvasItem(fromDrawable.display_shape)
        newCellVal = self.copyCanvasItem(fromDrawable.display_val)
        callEnviron |= set([newCell, newCellVal])

        # Move copies to the desired location
        self.moveItemsTo((newCell, newCellVal), toPositions, steps=steps,
                         sleepTime=sleepTime)

        # delete the original "to" display value and the new display shape
        self.canvas.delete(self.list[toIndex].display_val)
        self.canvas.delete(self.list[toIndex].display_shape)

        # update value and display value in "to" position in the list
        self.list[toIndex].display_val = newCellVal
        self.list[toIndex].val = self.list[fromIndex].val
        self.list[toIndex].display_shape = newCell
        self.list[toIndex].color = self.list[fromIndex].color
        callEnviron ^= set([newCell, newCellVal])

        # update the window
        self.window.update()

    def cellCoords(self, cell_index):  # Get bounding rectangle for array cell
        return (self.ARRAY_X0 + self.CELL_SIZE * cell_index, self.ARRAY_Y0,  # at index
                self.ARRAY_X0 + self.CELL_SIZE * (cell_index + 1) - self.CELL_BORDER,
                self.ARRAY_Y0 + self.CELL_SIZE - self.CELL_BORDER)

    def cellCenter(self, index):  # Center point for array cell at index
        half_cell = (self.CELL_SIZE - self.CELL_BORDER) // 2
        return add_vector(self.cellCoords(index), (half_cell, half_cell))

    def createArrayCell(self, index):  # Create a box representing an array cell
        cell_coords = self.cellCoords(index)
        half_border = self.CELL_BORDER // 2
        rect = self.canvas.create_rectangle(
            *add_vector(cell_coords,
                        (-half_border, -half_border,
                         self.CELL_BORDER - half_border, self.CELL_BORDER - half_border)),
            fill=None, outline=self.CELL_BORDER_COLOR, width=self.CELL_BORDER)
        self.canvas.lower(rect)
        return rect

    def createCellValue(self, indexOrCoords, key, color=None):
        """Create new canvas items to represent a cell value.  A square
        is created filled with a particular color with an text key centered
        inside.  The position of the cell can either be an integer index in
        the Array or the bounding box coordinates of the square.  If color
        is not supplied, the next color in the palette is used.
        An event handler is set up to update the VisualizationApp argument
        with the cell's value if clicked with any button.
        Returns the tuple, (square, text), of canvas items
        """
        # Determine position and color of cell
        if isinstance(indexOrCoords, int):
            rectPos = self.cellCoords(indexOrCoords)
            valPos = self.cellCenter(indexOrCoords)
        else:
            rectPos = indexOrCoords
            valPos = divide_vector(add_vector(rectPos[:2], rectPos[2:]), 2)
        if color is None:
            # Take the next color from the palette
            color = drawable.palette[self.nextColor]
            self.nextColor = (self.nextColor + 1) % len(drawable.palette)

        cell_rect = self.canvas.create_rectangle(
            *rectPos, fill=color, outline='', width=0)
        cell_val = self.canvas.create_text(
            *valPos, text=str(key), font=self.VALUE_FONT, fill=self.VALUE_COLOR)
        handler = lambda e: self.setArgument(str(key))
        for item in (cell_rect, cell_val):
            self.canvas.tag_bind(item, '<Button>', handler)

        return cell_rect, cell_val

    def display(self):
        self.canvas.delete("all")

        self.index = self.createIndex(self.nItems, 'nItems', level=-1) # indicate priority        

        for i in range(self.size):  # Draw grid of cells
            self.createArrayCell(i)

        # go through each Drawable in the list
        for i in range(self.nItems):
            drawItem = self.list[i]
            if drawItem:
                self.canvas.coords(drawItem.display_shape, *self.cellCoords(i))
                self.canvas.coords(drawItem.display_val, *self.cellCenter(i))            

        self.window.update()
        
    def newArraySize(self, val):
        callEnviron = self.createCallEnvironment()                
        # Clear Array and reset size and list
        self.size = val
        self.list = [None]*self.size
        self.nItems = 0
        
        self.display()
        self.cleanUp(callEnviron)

    # delete the last element of the queue, or None if empty
    def remove(self):
        callEnviron = self.createCallEnvironment()
        if self.nItems == 0:
            self.setMessage('Array is empty!')
            return
        self.startAnimations()
        self.wait(0.3)

        n = self.list[self.nItems - 1]

        # Slide value rectangle up and off screen
        items = (n.display_shape, n.display_val)
        self.moveItemsOffCanvas(items, N, sleepTime=0.02)

        self.nItems -= 1
        self.moveItemsBy(self.index, (-self.CELL_SIZE, 0))  # move priority arrow

        n = self.list.pop()

        self.cleanUp(callEnviron)

    def fixPositions(self):     # Move canvas display items to exact coords
        for i in range(self.nItems):
            drawItem = self.list[i]
            if drawItem:    # if i contains a cell...move the cells
                self.canvas.coords(drawItem.display_shape, *self.cellCoords(i))
                self.canvas.coords(drawItem.display_val, *self.cellCenter(i))

        # Move nItems index to position in array
        x = self.cellCenter(self.nItems)[0]
        # Use y coord from nItems index but x value from target location
        for item in self.index:
            coords = [x if i%2 == 0 else c
                      for i, c in enumerate(self.canvas.coords(item))]
            self.canvas.coords(item, *coords)
        
        self.window.update()

    def cleanUp(self, *args, **kwargs): # Customize clean up for sorting
        super().cleanUp(*args, **kwargs) # Do the VisualizationApp clean up
        if ((len(args) == 0 or args[0] is None) and # When cleaning up entire 
            kwargs.get('callEnviron', None) is None): # call stack,
            self.fixPositions()   # Restore cells to their coordinates in array

    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        newSizeArrayButton = self.addOperation(
            "New", lambda: self.clickNew(), numArguments=1, validationCmd=vcmd)
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1, validationCmd=vcmd)
        deleteButton = self.addOperation(
            "Remove", lambda: self.clickRemove(), numArguments=0)
        peekButton = self.addOperation(
            "Peek", lambda: self.clickPeek(), numArguments=0)
        self.addAnimationButtons()
        return [insertButton, deleteButton, peekButton]

    def validArgument(self):
        entered_text = self.getArgument()
        if entered_text and entered_text.isdigit():
            val = int(entered_text)
            if val < 100:
                return val
    
    def clickInsert(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            if self.nItems >= self.size:
                self.setMessage("Error! Queue is already full.")
            else:
                self.insert(val)
                self.setMessage("Value {} inserted".format(val))
        self.clearArgument()
    
    def clickRemove(self):
        result = self.remove()
        self.clearArgument()

    def clickPeek(self):
        if self.nItems <= 0: self.setMessage("Error! Queue is empty.")
        else:
            self.peek()
            self.setMessage("Value at front is {}".format(self.list[self.nItems-1].val))

    def clickNew(self):
        val = self.validArgument()
        # If the number of cells desired wouldn't fit on the screen, error message
        if val is None or self.window.winfo_width() <= self.ARRAY_X0 + (val+1) * self.CELL_SIZE:
            self.setMessage("This array size is too big to display")
        elif val == 0:
            self.setMessage("This array size is too small")
        else:
            self.newArraySize(val)
        self.clearArgument()



if __name__ == '__main__':
    queue = PriorityQueue()
    queue.runVisualization()
