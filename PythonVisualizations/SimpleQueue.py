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

    def __init__(self, size=12, title="Queue", **kwargs):
        super().__init__(title=title, **kwargs)
        self.list = [None]*size
        self.size = size
        self.front = 1  # when Queue is empty, front 
        self.rear = 0   # should be to right of rear.
        self.nItems = 0
        self.rearArrow = (None, None)
        self.frontArrow = (None, None)
        self.insertButton = None
        self.deleteButton=None
        self.display()

    def __str__(self):
        return str(self.list)
    
    # ANIMATION METHODS
    def createIndex(  # Create an index arrow to point at an indexed
            self, index=-1, name=None, high=True):  # cell with an optional name label

        cell_coords = self.cellCoords(index)
        cell_center = self.cellCenter(index)
        x0 = cell_center[0]
        x1 = x0
        y0 = cell_coords[1] - self.CELL_SIZE * 2 // 2
        y1 = cell_coords[1] - self.CELL_SIZE * 1 // 4
        if high:  # changes height of arrow
            y0 -= 20

        arrow = self.canvas.create_line(
            x0, y0, x1, y1, arrow="last", fill=self.VARIABLE_COLOR)
        if name:
            label = self.canvas.create_text(
                x1 + 2, y0, text=name, anchor=SW,
                font=self.VARIABLE_FONT, fill=self.VARIABLE_COLOR)
        return (arrow, label) if name else (arrow,)
        
        
    # insert item at rear of queue   
    def insertRear(self, val):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        #if there's a space to insert into
        color = drawable.palette[self.nextColor]
        # increment nextColor
        self.nextColor = (self.nextColor + 1) % len(drawable.palette)
        # deal with wraparound
        if self.rear == self.size - 1:  # deal with wraparound
            self.rear = -1
            self.moveItemsBy(self.rearArrow, (self.CELL_SIZE * self.size * -1, 0))
        #move arrow
        self.moveItemsBy(self.rearArrow, (self.CELL_SIZE, 0))
        # increment rear
        self.rear += 1

        # create new cell and cell value display objects
        # Start drawing new one at rear
        cell = self.canvas.create_rectangle(self.cellCoords(self.rear), fill=color, outline='')
        cell_val = self.canvas.create_text(self.cellCenter(self.rear), text=val, font=('Helvetica', '20'))

       # insert the item
        self.list[self.rear] = drawable(val, color, cell, cell_val)
        #increment number of items
        self.nItems += 1

        # update window
        self.window.update()
        self.cleanUp(callEnviron)

    # remove the left element of the queue, or None if empty
    def removeFront(self):
        # if the queue is empty, exit
        if self.nItems == 0:
            self.setMessage('Queue is empty!')
            return None
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        #get the value at front, and then set it to None so it will be garbage collected
        n = self.list[self.front]
        self.list[self.front] = None
        
        #increment front
        self.front += 1
        # delete the associated display objects
        self.canvas.delete(n.display_shape)
        self.canvas.delete(n.display_val)
        #deal with wraparound
        if self.front == self.size:
            self.front = 0
            self.moveItemsBy(self.frontArrow, (self.CELL_SIZE * self.size * -1, 0))
        #move arrow
        self.moveItemsBy(self.frontArrow, (self.CELL_SIZE, 0))

        # decrement number of arrows
        self.nItems -= 1
        # update window
        self.window.update()
        self.cleanUp(callEnviron)

    def display(self):

        self.canvas.delete("all")

        self.makeButtons()
        self.onOffButtons()
        xpos = self.ARRAY_X0
        ypos = self.ARRAY_Y0
        for i in range(self.size):  # Draw grid of cells
            self.createArrayCell(i)

        # go through each Element in the list


        self.rearArrow = self.createIndex(self.rear, "rear", high=False)
        self.frontArrow = self.createIndex(self.front, "front", high=True)
        self.window.update()

    #disable insert if queue if full, disable delete if empty
    #enable everything else without overriding queue/deque functionality
    def onOffButtons(self):

        #disable buttons as necessary
        if self.nItems == self.size:
            self.insertButton.config(state = DISABLED)
        elif self.nItems==0:
            self.deleteButton.config(state = DISABLED)


# Button functions

    def clickInsertRear(self):
        entered_text = self.getArgument()
        if self.nItems == self.size:
            self.setMessage('Queue is full!')
            self.clearArgument()
        elif entered_text:
            val = int(entered_text)
            if val < 100:
                # if is full does not insert

                self.insertRear(int(entered_text))

            else:
                self.setMessage("Input value must be an integer from 0 to 99.")
            self.clearArgument()
                
    def close_window(self):
        self.window.destroy()
        self.exit()

    def startAnimations(self):
        self.onOffButtons()
        super().startAnimations()


    def cellCoords(self, cell_index):  # Get bounding rectangle for array cell
        return (self.ARRAY_X0 + self.CELL_SIZE * cell_index, self.ARRAY_Y0,  # at index
                self.ARRAY_X0 + self.CELL_SIZE * (cell_index + 1) - self.CELL_BORDER,
                self.ARRAY_Y0 + self.CELL_SIZE - self.CELL_BORDER)

    def cellCenter(self, index):  # Center point for array cell at index
        half_cell = (self.CELL_SIZE - self.CELL_BORDER) // 2
        return add_vector(self.cellCoords(index), (half_cell, half_cell))

    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.insertButton = self.addOperation("Insert", lambda: self.clickInsertRear(),
                                             numArguments=1, validationCmd=vcmd)

        self.deleteButton = self.addOperation("Delete", lambda: self.removeFront())

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

    def cleanUp(self, *args, **kwargs): # Customize clean up for sorting
        super().cleanUp(*args, **kwargs) # Do the VisualizationApp clean up
        self.onOffButtons()       # disable buttons as necessary

# validate text entry
def validate(action, index, value_if_allowed,
             prior_value, text, validation_type, trigger_type, widget_name):
    if text in '0123456789':
        return True
    else:
        return False

if __name__ == '__main__':
    queue = Queue()

    queue.runVisualization()