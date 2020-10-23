import random
from tkinter import *

try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *


class OrderedArray(VisualizationApp):
    CELL_SIZE = 50
    CELL_BORDER = 2
    CELL_BORDER_COLOR = 'black'
    ARRAY_X0 = 100
    ARRAY_Y0 = 100
    FOUND_COLOR = 'brown4'
    nextColor = 0

    def __init__(self, size=10, title="Ordered Array", **kwargs):
        super().__init__(title=title, **kwargs)
        self.size = size
        self.title = title
        self.list = []
        self.buttons = self.makeButtons()
        self.nItems = 0

        #Fill in initial array values with random integers
        # The display items representing these array cells are created later
        a = [random.randrange(90) for i in range(size-1)]
        a.sort()
                
        # Append and draw them to the list and draw them
        for i in a:
            self.list.append(drawable(i))
        
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

    insertCode = """
def insert(self, item):    # Insert item into the correct position
    if self.__nItems >= len(self.__a): # If array is full,
       raise Exception("Array overflow") # raise exception
    
    j = self.__nItems       # Start at right (larger) end and loop
    while 0 < j and self.__a[j - 1] > item: # over items
       self.__a[j] = self.__a[j-1] # Move larger item to right
       j -= 1               # Advance left among items
       
    self.__a[j] = item      # Insert the item
    self.__nItems += 1      # Increment the number of items                 
"""
    insertCodeSnippets = {
        'full_array': ('1.4','1.23'),
        'start': ('4.04', '4.end'),
        'while_loop':('6.01','6.end'),
        'make_room': ('7.04','7.end'),
        'decrement_count': ('8.8','8.end'),
        'insert_item': ('10.12','10.end'),
        'increment_items': ('11.01','11.end')
    }

    def insert(self, val):
        self.startAnimations()
        
        callEnviron = self.createCallEnvironment(
            self.insertCode.strip(), self.insertCodeSnippets)         

        k=len(self.list)

        self.list.append(drawable(None))
        
        indexK = self.createIndex(len(self.list) -1, 'k', level=-2) # create "k" arrow
        callEnviron |= set(indexK)  

       # for k in range(len(self.list) - 1, j, -1):  # Move bigger items right
        self.highlightCodeTags('while_loop', callEnviron)
        self.wait(0.2)      
        while 0 < k and self.list[k-1].val > val: # over items             

            self.moveItemsBy(indexK, (-self.CELL_SIZE, 0), sleepTime=0.1)  # Move "k" arrow
            self.highlightCodeTags('make_room', callEnviron)
            self.wait(0.2)  
            self.list[k].val = self.list[k - 1].val # Move larger item to right            
            self.assignElement(k - 1, k, callEnviron)          
            k -= 1  # Advance left among items    
            self.highlightCodeTags('decrement_count', callEnviron)
            self.wait(0.2)                
        # Location of the new cell in the array
        toPositions = (self.cellCoords(k),
                       self.cellCenter(k))

        self.highlightCodeTags('insert_item', callEnviron)
        self.wait(0.2)
        
        # Animate arrival of new value from operations panel area
        canvasDimensions = self.widgetDimensions(self.canvas)
        startPosition = [canvasDimensions[0] // 2, canvasDimensions[1]] * 2
        startPosition = add_vector(startPosition, (0, 0, self.CELL_SIZE, self.CELL_SIZE))
        cellPair = self.createCellValue(startPosition, val)
        callEnviron |= set(cellPair)  # Mark the new items as temporary

        self.moveItemsTo(cellPair, toPositions, steps= self.CELL_SIZE, sleepTime=0.01)

        self.canvas.delete(self.list[k].display_shape)  # These are now covered by the temporary items
        self.canvas.delete(self.list[k].display_val)
        self.list[k]= (drawable(
            val, self.canvas.itemconfigure(cellPair[0], 'fill')[-1], *cellPair))
        callEnviron ^= set(cellPair)  # New item is no longer temporary
        
        
        self.highlightCodeTags('increment_items', callEnviron)
        self.wait(0.2)              
        
        # Move nItems pointer
        self.moveItemsBy(self.nItems, (self.CELL_SIZE, 0))
        self.wait(0.1)        

        #self.window.update()  
        #self.stopAnimations()
        self.cleanUp(callEnviron) 
        
    def insertBinarySearch(self,val):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()
        j = self.search(val)  # Find where item should go

        self.list.append(drawable(None))

        indexK = self.createIndex(len(self.list) - 1, 'k', level=-1)  # create "k" arrow
        callEnviron |= set(indexK)

        for k in range(len(self.list) - 1, j, -1):  # Move bigger items right

            self.moveItemsBy(indexK, (-self.CELL_SIZE, 0), sleepTime=0.1)  # Move "k" arrow

            self.list[k].val = self.list[k - 1].val
            self.assignElement(k - 1, k, callEnviron)

            # Location of the new cell in the array
        toPositions = (self.cellCoords(j),
                       self.cellCenter(j))

        # Animate arrival of new value from operations panel area
        canvasDimensions = self.widgetDimensions(self.canvas)
        startPosition = [canvasDimensions[0] // 2, canvasDimensions[1]] * 2
        startPosition = add_vector(startPosition, (0, 0, self.CELL_SIZE, self.CELL_SIZE))
        cellPair = self.createCellValue(startPosition, val)
        self.moveItemsTo(cellPair, toPositions, steps=self.CELL_SIZE, sleepTime=0.01)
        self.list[j] = (drawable(
            val, self.canvas.itemconfigure(cellPair[0], 'fill')[-1], *cellPair))

        self.cleanUp(callEnviron)

    def removeFromEnd(self):
        callEnviron = self.createCallEnvironment()  
        # pop a Drawable from the list
        if len(self.list) == 0:
            self.setMessage('Array is empty!')
            return
        callEnviron = self.createCallEnvironment()         
        
        self.startAnimations()  
   
        #move nItems pointer
        self.moveItemsBy(self.nItems, (-self.CELL_SIZE, 0))
        
        n = self.list.pop()

        # delete the associated display objects

        items = (n.display_shape, n.display_val)
        callEnviron |= set(items)
        self.moveItemsOffCanvas(items, N, sleepTime=0.02)

        # update window
        self.window.update()
        self.stopAnimations()

        # Clean up animations
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
            color = drawable.palette[OrderedArray.nextColor]
            OrderedArray.nextColor = (OrderedArray.nextColor + 1) % len(drawable.palette)

        cell_rect = self.canvas.create_rectangle(
            *rectPos, fill=color, outline='', width=0)
        cell_val = self.canvas.create_text(
            *valPos, text=str(key), font=self.VALUE_FONT, fill=self.VALUE_COLOR)
        handler = lambda e: self.setArgument(str(key))
        for item in (cell_rect, cell_val):
            self.canvas.tag_bind(item, '<Button>', handler)

        return cell_rect, cell_val

    def display(self):
        callEnviron = self.createCallEnvironment()
        self.canvas.delete("all")

        for i in range(self.size):  # Draw grid of cells
            self.createArrayCell(i)
        
        # draw an index pointing to the last item in the list
        self.nItems = self.createIndex(len(self.list), "nItems", level = -1, color = 'black')

        # go through each Drawable in the list
        for i, n in enumerate(self.list):
            # create display objects for the associated Drawables
            n.display_shape, n.display_val = self.createCellValue(
                i, n.val, n.color)

            n.color = self.canvas.itemconfigure(n.display_shape, 'fill')[-1]


        self.window.update()
        self.cleanUp(callEnviron)

    def randomFill(self):
        callEnviron = self.createCallEnvironment()        
        # Clear the list so new values can be entered
        self.list=[] 
        size = self.size       
        
        # Create a list of random numbers and sort them
        a = [random.randrange(90) for i in range(size)]
        a.sort()
        
        # Append and draw them to the list and draw them
        for i in a:
            self.list.append(drawable(i))
        self.display()            
        self.cleanUp(callEnviron)
        
    def newArraySize(self, val):
        callEnviron = self.createCallEnvironment()  
        # Clear Array and reset size and list
        self.canvas.delete("all")
        self.size = val
        self.list = []
        self.display()
        
        for i in range(val):  # Draw new grid of cells
            self.createArrayCell(i) 
        self.cleanUp(callEnviron)

    findCode = """
def find(self, item):            # Find index at or just below
      lo = 0                        # item in ordered list
      hi = self.__nItems-1          # Look between lo and hi
      
      while lo <= hi:
         mid = (lo + hi) // 2       # Select the midpoint
         if self.__a[mid] == item:  # Did we find it at midpoint?
            return mid              # Return location of item
         elif self.__a[mid] < item: # Is item in upper half?
            lo = mid + 1            # Yes, raise the lo boundary
         else: 
            hi = mid - 1            # No, but could be in lower half
            
      return lo   # Item not found, return insertion point instead                    
"""
    findCodeSnippets = {
        'initialize_lo': ('2.4','2.end'),
        'initialize_hi': ('3.04', '3.end'),
        'while_loop': ('5.04','5.end'),
        'initialize_mid': ('6.8','6.end'),
        'found_mid': ('7.8','7.end'),
        'success': ('8.10','8.end'),
        'upper_half': ('9.8','9.end'),
        'move_lo': ('10.8', '10.end'),
        'lower_half': ('11.8','11.end'),
        'move_hi': ('12.8','12.end'),
        'return_lo': ('14.04','14.end'),      
    }


    def search(self, val):
        callEnviron = self.createCallEnvironment(
            self.findCode.strip(), self.findCodeSnippets)     
        self.startAnimations()
        self.highlightCodeTags('initialize_lo', callEnviron)
        self.wait(0.3)
        self.highlightCodeTags('initialize_hi', callEnviron)
        self.wait(0.3)
        lo = 0                             #Point to lo
        indexLo = self.createIndex(lo, 'lo',level= 1)
        callEnviron |= set(indexLo)
        hi = len(self.list)-1              # Point to hi
        indexHi = self.createIndex(hi, 'hi', level = 3)
        callEnviron |= set(indexHi)
        mid = (lo + hi) // 2               # Point to the midpoint
        indexMid = self.createIndex(mid, 'mid', level = 2)
        callEnviron |= set(indexMid)  
        self.highlightCodeTags('while_loop', callEnviron)
        self.wait(0.3)
        while lo <= hi:
            self.highlightCodeTags('initialize_mid', callEnviron)
            self.wait(0.3)
            mid = (lo + hi) // 2           # Select the midpoint
            self.highlightCodeTags('found_mid', callEnviron)
            self.wait(0.3)            
            if self.list[mid].val == val:  # Did we find it at midpoint?  
                posShape = self.canvas.coords(self.list[mid].display_shape)

                # Highlight the found element with a circle
                foundCircle = self.canvas.create_oval(
                    *add_vector(
                        posShape,
                        (self.CELL_BORDER, self.CELL_BORDER, -self.CELL_BORDER, -self.CELL_BORDER)),
                    outline=self.FOUND_COLOR)
                callEnviron.add(foundCircle) 
                
                self.wait(0.3)

                self.cleanUp(callEnviron)
                self.highlightCodeTags('success', callEnviron)
                self.wait(0.3)                
                return mid                 # Return the value found 
            
            elif self.list[mid].val < val: # Is item in upper half?
                self.highlightCodeTags('upper_half', callEnviron)
                self.wait(0.3) 
                self.highlightCodeTags('move_lo', callEnviron)
                self.wait(0.3)                
                deltaXLo = (mid - lo) + 1
                self.moveItemsBy(indexLo, (self.CELL_SIZE*deltaXLo, 0))
                lo = mid + 1               # Yes, raise the lo boundary
                deltaXMid = ((hi - lo) // 2) + 1
                self.moveItemsBy(indexMid, (self.CELL_SIZE*deltaXMid, 0))
               
            else:                         # Is item in lower half? 
                self.highlightCodeTags('lower_half', callEnviron)
                self.wait(0.3)          
                self.highlightCodeTags('move_hi', callEnviron)
                self.wait(0.3)                
                deltaXHi = (mid -hi) - 1 
                self.moveItemsBy(indexHi, (self.CELL_SIZE*deltaXHi, 0))
                hi = mid - 1              # Yes, lower the hi boundary 
                deltaXMid = ((lo- hi) //2) -1
                self.moveItemsBy(indexMid, (self.CELL_SIZE* deltaXMid, 0))
        self.highlightCodeTags('return_lo', callEnviron)
        self.wait(0.3)        
        self.window.update()
        self.stopAnimations()
        self.cleanUp(callEnviron)
        return lo                       #val not found 
    
    removeCode = """
def delete(self, item):            
    j = self.find(item)             
    if j < self.__nItems and self.__a[j] == item: 
        self.__nItems -= 1           
        for k in range(j, self.__nItems): 
            self.__a[k] = self.__a[k+1]
        return True                  
"""
    removeCodeSnippets = {
        'finding_val': ('2.4','2.23'),
        'key_comparison': ('3.04', '3.end'),
        'decrement_count': ('4.8','4.26'),
        'shift_loop_increment': ('5.8','5.44'),
        'shift_items': ('6.12','6.end'),
        'success': ('7.8','7.end')
    }
        
    def remove(self, val):
        self.startAnimations()
        
        callEnviron = self.createCallEnvironment(
            self.removeCode.strip(), self.removeCodeSnippets)  
        
        self.highlightCodeTags('finding_val', callEnviron)

        index = self.search(val)
        
        found = self.list[index].val == val
        if found:    # Record if value was found
          
            self.wait(0.2)

            n = self.list[index]
            # if the value is found
            self.highlightCodeTags('key_comparison', callEnviron)
            self.wait(0.2)            
            
            # Slide value rectangle up and off screen
            items = (n.display_shape, n.display_val)
            self.moveItemsOffCanvas(items, N, sleepTime=0.02)
            callEnviron |= set(items)            
            
            # decrement nItems
            self.highlightCodeTags('decrement_count', callEnviron)
            self.wait(0.2)       

            #decrement nItems pointer  
            self.moveItemsBy(self.nItems, (-self.CELL_SIZE, 0), sleepTime=0.01)
            
            self.highlightCodeTags('shift_loop_increment', callEnviron)
            self.wait(0.2)              
            
            # Create an index for shifting the cells
            kIndex = self.createIndex(index, 'k', level = -2)
            callEnviron |= set(kIndex)
            # Slide values from right to left to fill gap
            for i in range(index+1, len(self.list)):
                self.assignElement(i, i - 1, callEnviron)
                self.highlightCodeTags('shift_items', callEnviron)
                self.wait(0.2)                   
                self.moveItemsBy(kIndex, (self.CELL_SIZE, 0), sleepTime=0.01) 
                self.highlightCodeTags('shift_loop_increment', callEnviron)
                self.wait(0.2)                   
            self.moveItemsBy(self.nItems, (-self.CELL_SIZE, 0), sleepTime=0.01)
            self.highlightCodeTags('success', callEnviron)
            # delete the last cell from the list and as a drawable 
            n = self.list.pop()  
            self.canvas.delete(n.display_shape)
            self.canvas.delete(n.display_val)     
            # update window
            self.wait(0.2)
        # Animation stops
        self.highlightCodeTags([], callEnviron)

        self.cleanUp(callEnviron)
        self.stopAnimations()
        return found
        
    def fixCells(self):       # Move canvas display items to exact cell coords
        for i, drawItem in enumerate(self.list):
            self.canvas.coords(drawItem.display_shape, *self.cellCoords(i))
            self.canvas.coords(drawItem.display_val, *self.cellCenter(i))
        self.window.update()

    def cleanUp(self, *args, **kwargs): # Customize clean up for sorting
        super().cleanUp(*args, **kwargs) # Do the VisualizationApp clean up
        self.fixCells()       # Restore cells to their coordinates in array


    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        newSizeArrayButton = self.addOperation(
            "New", lambda: self.clickNew(), numArguments=1, validationCmd=vcmd)        
        searchButton = self.addOperation(
            "Search", lambda: self.clickSearch(), numArguments=1, validationCmd=vcmd)
        randomFillButton = self.addOperation(
            "Random Fill", lambda: self.randomFill())        
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1, validationCmd=vcmd)
        deleteValueButton = self.addOperation(
            "Delete", lambda: self.clickDelete(), numArguments=1, validationCmd=vcmd)
        deleteRightmostButton = self.addOperation(
            "Delete Rightmost", lambda: self.removeFromEnd())
        #this makes the pause, play and stop buttons 
        self.addAnimationButtons()
        return [searchButton, insertButton, deleteValueButton, newSizeArrayButton, randomFillButton,
                deleteRightmostButton]

    def validArgument(self):
        entered_text = self.getArgument()
        if entered_text and entered_text.isdigit():
            val = int(entered_text)
            if val < 100:
                return val
            
    # Button functions
    def clickSearch(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        elif len(self.list) == 0: 
            self.setMessage("The array is empty.")
        else:
            result = self.search(val)
            if self.list[result].val == val:
                msg = "Found {}!".format(val)
            else:
                msg = "Value {} not found".format(val)
            self.setMessage(msg)
        self.clearArgument()

    def clickInsert(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            if len(self.list) >= self.size:
                self.setMessage("Error! Array is already full.")
            else:
                self.insert(val)
                self.setMessage("Value {} inserted".format(val))
        self.clearArgument()

    def clickDelete(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input value must be an integer from 0 to 99.")
        else:
            result = self.remove(val)
            if result:
                msg = "Value {} deleted!".format(val)
            else:
                msg = "Value {} not found".format(val)
            self.setMessage(msg)
        self.clearArgument()
    
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
    random.seed(3.14159)  # Use fixed seed for testing consistency
    array = OrderedArray()

    array.runVisualization()

