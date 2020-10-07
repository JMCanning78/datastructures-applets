import math
import random
from time import sleep
from tkinter import *
try:
    from VisualizationApp import *
except ModuleNotFoundError:
    from .VisualizationApp import *

class Link():
    
    def __init__(self, levels, k):
        self.key     = k
        self.levels  = levels
        self.forward = [None] * levels
        self.rects   = [None] * levels
        self.arrows  = [None] * levels
        self.rect    = None
        self.text    = None 
        self.y       = None    # x and y coords represent 
        self.x       = None    # the bottom left corner 
        
            
class SkipList(VisualizationApp):
    
    def __init__(self, maxKeys=20, title="Skip List", **kwargs):
        
        # VisualizationApp code
        kwargs['title'] = title
        super().__init__(**kwargs)
        
        self.makeButtons()
        
        # Specs for GUI's. 
        self.CELL_WIDTH = 22
        self.CELL_HEIGHT = 22
        self.CELL_GAP = 28
        self.INIT_X = 30                           # x coord where SkipList/header will start
        self.INIT_Y = 175                          # Y coord/line SkipList will sit on
        self.LINK_WIDTH \
            = self.CELL_WIDTH*2 + self.CELL_GAP    # Tot dx coords a cell takes up
        self.ARROW_X1 = self.CELL_WIDTH*(3/2)      # x1 arrow position within Link
        self.ARROW_Y1 = self.CELL_HEIGHT//2        # y1 arrow position within Link
        self.arrowX1 = lambda n : n.x +  self.ARROW_X1
        self.arrowY1 = lambda n, i : n.y - self.CELL_HEIGHT*i - self.ARROW_Y1
        self.arrowX2 = lambda to: to.x
        self.arrowY2 = lambda to, i: to.y - self.CELL_HEIGHT*i - self.ARROW_Y1 
        # The - 2 takes into acount the header and end
        self.maxInserts = lambda : ((self.widgetDimensions(self.canvas)[0] // self.LINK_WIDTH) - 2)
        self.__numLinks = 0
        
        # Skip List code
        self.__level = 0  
        self.__maxLevel = math.ceil(math.log2(maxKeys))
        self.__header = Link(self.__maxLevel, None) 
        self.__end = Link(self.__maxLevel, None)        

        self.fill(5)        

    def insert(self, insertKey):
        
        if self.__numLinks == self.maxInserts(): return False
        
        self.startAnimations()
        callEnviron = self.createCallEnvironment()
        
        update = [None] * self.__maxLevel
        x = self.__header
        
        self.highlightNode(x)   
        
        # start at the top level and work downward
        for i in range(self.__level-1, -1, -1): 
            
            # move as far forward as possible at level i
            self.highlightArrow(x, i)
            
            while x.forward[i] and x.forward[i].key < insertKey:                
                self.highlightNode(x.forward[i])
                self.unHighlightNode(x)
                self.unHighlightArrow(x, i)
                self.highlightArrow(x.forward[i], i)

                x = x.forward[i]
            
            self.unHighlightArrow(x, i)
                
            # don't allow duplicates
            if x.forward[i] and insertKey == x.forward[i].key:
                self.unHighlightNode(x)
                self.cleanUp(callEnviron)
                return False 
            
            update[i] = x     
        
        self.unHighlightNode(x)
        
        newLevel = self.__randomLevel()  # select a level for this node
        if newLevel > self.__level:  
            for i in range(self.__level, newLevel): update[i] = self.__header   
            self.__level = newLevel
            
        # Create link
        x = Link(newLevel, insertKey)
        self.createVisualNode(x, update)
        
        # Draw arrows
        for i in range(newLevel):
            x.forward[i] = update[i].forward[i]
            self.drawArrow(x, i, update[i].forward[i], highlight="blue")
            update[i].forward[i] = x
            self.rePositionArrow(update[i], i, x, highlight="red")
        
        # Complete draw of the Link onto canvas if animation
        self.completeDraw(x, update)
           
        self.__numLinks += 1
        
        # Finish animation
        self.cleanUp(callEnviron) 
        return True
    
     
    def search(self, key):
        self.startAnimations()
        callEnviron = self.createCallEnvironment()
        
        x = self.__header
        
        self.highlightNode(x)   
        
        # start at the top level and work downward
        for i in range(self.__level-1, -1, -1): 
            
            # move as far forward as possible at level i
            self.highlightArrow(x, i)
            
            while x.forward[i] and x.forward[i].key < key:                
                self.highlightNode(x.forward[i])
                self.unHighlightNode(x)
                self.unHighlightArrow(x, i)
                self.highlightArrow(x.forward[i], i)

                x = x.forward[i]
                
            # don't allow duplicates
            if x.forward[i] and key == x.forward[i].key:
                self.highlightNode(x.forward[i], color="blue")
                self.unHighlightNode(x)
                self.unHighlightArrow(x, i)
                self.blink(x.forward[i], "blue")
                self.cleanUp(callEnviron)
                return True 
           
            self.unHighlightArrow(x, i)
        
        self.unHighlightNode(x) 
        
        # Finish animation
        self.cleanUp(callEnviron)
        return False
    
    def delete(self, key):
        self.startAnimations()
        callEnviron = self.createCallEnvironment()  
        
        found = False
        x = self.__header
        
        self.highlightNode(x)    
        # start at the top level and work downward
        for i in range(self.__level-1, -1, -1):
            # move as far forward as possible at level i
            self.highlightArrow(x, i)
            while x.forward[i] and x.forward[i].key < key:
                self.highlightNode(x.forward[i])
                self.unHighlightNode(x)
                self.unHighlightArrow(x, i)
                self.highlightArrow(x.forward[i], i)

                x = x.forward[i]
                
            # if found
            if x.forward[i] and key == x.forward[i].key:
                if not found:
                    self.highlightNode(x.forward[i], arrows=True, color="blue")
                    self.moveNodeVertically(x.forward[i], direction="down")
                    found = x.forward[i]
                
                # Note this is not to=x.forward[i].forward[i] because we have already reset forward
                self.rePositionArrow(x, i, x.forward[i].forward[i], highlight="red") 
                x.forward[i] = x.forward[i].forward[i]
            
            if not found: self.unHighlightArrow(x, i)
            
        self.unHighlightNode(x)
        if found: self.deleteVisualNode(found)
        if found: self.__numLinks -= 1
        
        # Finish animation
        self.cleanUp(callEnviron) 
        
        return found != False
        
    def fill(self, num):
        self.startAnimations()
        callEnviron = self.createCallEnvironment()
        
        if num > self.maxInserts(): num = self.maxInserts()
        self.__numLinks = 0
        
        self.setAnimationState(False)

        self.__header.forward = [None] * self.__maxLevel
        self.__level = 0
        self.wipeCanvas()   
            
        for i in range(num):
            
            # Ensure fills up to num,
            # even if same random num 2x+
            while True:
                r = random.randint(1, 99)
                if self.insert(r): break
                
        # Finish animation
        self.cleanUp(callEnviron) 
        
    def __randomLevel(self):
        level = 1
        while random.random() < 0.5 and \
              level < self.__maxLevel:
            level += 1
        return level
    
    
    ##################
    ##  Animations  ##
    ##################
   
    def setNodeCoords(self, n, prev):
        if self.isAnimated(): 
            n.y = self.INIT_Y + n.levels*self.CELL_HEIGHT  
        else: n.y = self.INIT_Y
        n.x = prev.x + self.LINK_WIDTH

    def setupHeaderAndEnd(self):
        n = self.__header
        
        # set coords
        n.x = self.INIT_X
        n.y = self.INIT_Y
        
        self.drawEnd()
        
        x1 = n.x + self.CELL_WIDTH
        x2 = n.x + self.CELL_WIDTH*2
        
        for i in range(self.__maxLevel):
            coords = (x1, n.y - self.CELL_HEIGHT*i,\
                      x2, n.y - self.CELL_HEIGHT*(i+1))
            n.rects[i] = self.canvas.create_rectangle(coords)
            self.drawArrow(n, i) 
    
    def createVisualNode(self, n, update):
        # Complete update. 
        # As of now it is only set up to level
        for i in range (self.__level, self.__maxLevel):
            update[i] = self.__header
        
        self.setNodeCoords(n, update[0])
        self.moveLinksAfter(n, update, direction="right")
        self.drawNode(n)
           
    def drawNode(self, n):     
        # create visual structure
        coords = (n.x, n.y, \
                  n.x + self.CELL_WIDTH, n.y - self.CELL_HEIGHT*n.levels)
        n.rect = self.canvas.create_rectangle(coords)
        coords = (n.x + self.CELL_WIDTH/2, \
                  n.y - (self.CELL_HEIGHT*n.levels)/2)
        n.text = self.canvas.create_text(coords, text=str(n.key))
        
        x1 = n.x + self.CELL_WIDTH
        x2 = n.x + self.CELL_WIDTH*2
        # Create forward[] boxes    
        for i in range(n.levels):
            coords = (x1, n.y - self.CELL_HEIGHT*i,\
                x2, n.y - self.CELL_HEIGHT*(i+1))
            n.rects[i] = self.canvas.create_rectangle(coords)          
                     
        self.wait(0.01)

    # Creates an arrow
    # If animation, draws in a shooting-out motion
    def drawArrow(self, n, i=0, to=None, highlight="black"):
        
        if not to: to = self.__end
        
        if not self.isAnimated(): highlight ="black"
        
        x = self.arrowX1(n)
        y = self.arrowY1(n, i)
        coords = (x, y, x, y)
        n.arrows[i] = self.canvas.create_line(coords, arrow="last", fill=highlight) 
        self.rePositionArrow(n, i, to, highlight)      
    
    # This can only move in one x direc and one y direc at a time (for now)
    def rePositionArrow(self, n, i=0, to=None, highlight="black"):

        if not to: to = self.__end
        
        # vars not totally appropriately named,
        # but a dx represents how much
        # arrow will grow per sleepTime,
        # not total distance
        dx1 = dy1 = dx2 = dy2 = 0   
        # total distance to be changed
        d = 0
        # placeholder for change in x
        x_change = 0
        
        # Coords where arrow currently is
        # self.arrow coords are where we want the arrow to be
        x1, y1, x2, y2 = self.canvas.coords(n.arrows[i])
        
        if self.arrowX2(to) != x2:
            d = self.arrowX2(to) - x2
            dx2 = 1
            if d < 0: 
                dx2 = dx2 * (-1)
            
        # Will probs never use
        elif self.arrowX1(n) != x1:
            d = self.arrowX1(n) - x1
            dx1 = 1
            if d < 0: dx1 *= -1

        # store d so can calc y_change
        if d: x_change = d 
        
        if self.arrowY2(to, i) != y2:
            d = self.arrowY2(to, i) - y2
            dy2 = 1
            if d < 0: dy2 *= -1
        elif self.arrowY1(n, i) != y1:
            d = self.arrowY1(n, i) - y1
            dy1 = 1
            if d < 0: dy1 *= -1
                
        if x_change != 0 and x_change != d:
            # MUST BE abs() else - will cancel
            dif = abs(x_change/d)
            dx1 *= dif
            dx2 *= dif
        d = abs(d)
        
        self.highlightArrow(n, i, color=highlight)
            
        for move in range(abs(int(d))):
            x1, y1, x2, y2 = self.canvas.coords(n.arrows[i])
            coords = (x1 + dx1, y1 + dy1, x2 + dx2, y2 + dy2)
            self.canvas.coords(n.arrows[i], coords)
            
            self.wait(0.002)           
    
    # Fill the update array
    def fillUpdate(self, key):
        x = self.__header
        update = [None] * self.__maxLevel
        for i in range(self.__maxLevel-1, -1, -1):
            while x.forward[i] and x.forward[i].key < key:
                x = x.forward[i]
            
            update[i] = x        
           
        return update
        
    # Move all links after n one spot over 
    # It doesn't totally make sense 
    # to pass n in instead of the link where
    # move-chain will start,
    # but we need it to determine levels
    # direction: right or left
    def moveLinksAfter(self, n, update, direction="right"):
        
        # animation. less move_x -> smoother animation
        if self.isAnimated(): move_x = 1
        else: move_x = self.LINK_WIDTH        
        if direction == "right":
            lower = 0
            upper = self.LINK_WIDTH
            lowerArrow = len(n.forward)
        elif direction == "left":
            lower=self.LINK_WIDTH
            upper=0
            move_x *= -1
            lowerArrow = 0            
        
        for step in range(lower, upper, move_x):
        # Loop through everything to be moved
            cur = update[0].forward[0]
            
            while cur:
            
                # update their x coord (y coord stays the same)
                cur.x = cur.x + move_x
            
                # move everything, but switch to use of tags?
                self.moveLink(cur, x=move_x)
                       
                # next item to move
                cur = cur.forward[0]
            
            # move end/none arrows
            self.canvas.move("none", move_x, 0)
            self.__end.x += move_x
            
            # extend those arrows that float over n
            for i in range(lowerArrow, self.__maxLevel):
                x1, y1, x2, y2 = self.canvas.coords(update[i].arrows[i])
                coords = (x1, y1, x2 + move_x, y2)
                self.canvas.coords(update[i].arrows[i], coords)
                
            # correct the in-arrows of n
            # count is finding how many links
            # each arrow passes over to smoothly animate
            for i in range(1, lowerArrow): 
                x1, y1, x2, y2 = self.canvas.coords(update[i].arrows[i])
                cur = update[0]
                count = 0
                while cur.forward[0] != update[i].forward[i]: 
                    cur = cur.forward[0]
                    count += 1
                    
                coords = (x1, y1, x2 - abs(move_x)*count, y2)    
                self.canvas.coords(update[i].arrows[i], coords)     
                
            self.wait(0.001)
        
    def moveLink(self, link, x=0, y=0):
        shapes = [link.rect, link.text] + link.rects + link.arrows
        self.moveShapes(shapes, x, y)
    
    # Move over a collection of shapes/canvas items        
    def moveShapes(self, shapes, x=0, y=0):
        for shape in shapes:
            self.canvas.move(shape, x, y)        
        
    def completeDraw(self, n, update):
        
        # MOVE EVERYTHING UPWARDS ONLY IF BENEATH Y
        # Returns if inserted at end or no animation
      
        # Currently not neccessary,
        # but neccessary in prev versions
        if n.y != self.INIT_Y: 
            self.moveNodeVertically(n, update, direction="up")
            
        for i in range(n.levels):
            self.unHighlightArrow(n, i)
            self.unHighlightArrow(update[i], i)
    
    def moveNodeVertically(self, n, update=None, direction="up"):
        
        if not update: 
            update = self.fillUpdate(n.key)
        
        if direction=="up": 
            upper = n.y - self.INIT_Y
            lower = 0
            move_y = -1
        elif direction=="down": 
            upper = 0
            lower = self.CELL_HEIGHT*n.levels
            move_y = 1
        
        self.wait(0.1)
        
        for dy in range(upper, lower, move_y):
     
            # Change y coord to reg position
            # But just do once?
            n.y = n.y + move_y
        
            # Move structure into place
            self.moveShapes(([n.rect, n.text] + n.rects), y=move_y)
            
            # Move arrows
            for i in range(0, len(n.forward)):            
                # REDRAW ARROWS/move arrows so now horizontal
                x1, y1, x2, y2 = self.canvas.coords(n.arrows[i])
                coords = (x1, y1 + move_y, x2, y2)
                self.canvas.coords(n.arrows[i], coords)
                x1, y1, x2, y2 = self.canvas.coords(update[i].arrows[i])
                coords = (x1, y1, x2, y2 + move_y)
                self.canvas.coords(update[i].arrows[i], coords)                  
             
            self.wait(0.001)
                        
    def deleteVisualNode(self, n):
        
        update = self.fillUpdate(n.key)
        
        self.canvas.delete(n.rect)
        self.canvas.delete(n.text)
        for i in range(n.levels):
            self.canvas.delete(n.rects[i])
            self.canvas.delete(n.arrows[i])
        
        self.wait(0.2)
        self.moveLinksAfter(n, update, direction="left")
        
        for i in range(n.levels):
            self.unHighlightArrow(update[i], i) 
    
    # Delete e/t on canvas
    # And re-draw header and end
    def wipeCanvas(self):
        self.canvas.delete("all")
        self.setupHeaderAndEnd()
     
    # Draw arrows at end
    # that represent none
    def drawEnd(self):
        n = self.__end
        n.x = self.__header.x + self.LINK_WIDTH
        n.y = self.INIT_Y
        dy = self.CELL_HEIGHT//7
        dx = self.CELL_WIDTH//6
        
        for i in range(self.__maxLevel):
            y = n.y - self.CELL_HEIGHT*i
            x = n.x + 3
            for j in range(1, self.CELL_HEIGHT//7 + 1):
                coords = (x + dx*j, y - dy*j, \
                          x + dx*j, y - (self.CELL_HEIGHT - dy*j))
                self.canvas.create_line(coords, tag="none")    
    
    #######################
    ## HIGHLIGHTING CODE ## 
    #######################
    
    # Option to highlight out-arrows
    # of node
    def highlightNode(self, n, arrows=False, color="red", sleepTime=0.01):
        if not self.isAnimated(): return
        if not n.key: objects = n.rects  # header check
        else: objects = [n.rect] + n.rects
        for item in objects:
            self.canvas.itemconfig(item, outline=color)
        if arrows:
            for arrow in n.arrows:
                self.canvas.itemconfig(arrow, fill=color)
        self.wait(sleepTime)        
        
    def highlightArrow(self, n, i, color="red", sleepTime=0.01):
        if self.isAnimated():
            self.canvas.itemconfig(n.arrows[i], fill=color)
            self.wait(sleepTime)
      
    def unHighlightNode(self, n, arrows=False, sleepTime=0.0):
        if n.key: objects = [n.rect] + n.rects
        else: objects = n.rects
        for item in objects:
            self.canvas.itemconfig(item, outline="black")
        if arrows:
            for arrow in n.arrows:
                self.canvas.itemconfig(arrow, fill="black")

        self.wait(sleepTime)     
        
    def unHighlightArrow(self, n, i, sleepTime=0.0):
        self.canvas.itemconfig(n.arrows[i], fill="black")  
        self.wait(sleepTime)  
    
    # Disapear and reapear border
    # in blinking motion
    def blink(self, n, color="blue"):
        items = [n.rect] + n.rects
        for item in items:
            self.canvas.itemconfig(item, outline=color)        
        for w in [0, 1, 0, 1]:
            for item in items:
                self.canvas.itemconfig(item, width=w)
            self.wait(0.4)
        for item in items:
            self.canvas.itemconfig(item, outline="black")
        self.wait(0.0)       
            
        ########################
        ## Control Panel Code ##
        ########################
        
    def makeButtons(self):
        vcmd = (self.window.register(numericValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        searchButton = self.addOperation(
            "Search", lambda: self.clickSearch(), numArguments=1,
            validationCmd=vcmd, helpText="Click to enter number")
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1,
            validationCmd=vcmd)        
        deleteButton = self.addOperation(
            "Delete", lambda: self.clickDelete(), numArguments=1,
            validationCmd=vcmd)
        fillButton = self.addOperation(
            "Fill", lambda: self.clickFill(), numArguments=1, 
            validationCmd=vcmd)
        # this makes the play, pause, and stop buttons 
        self.addAnimationButtons()
        return [searchButton, insertButton, deleteButton, fillButton]  
    
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
            self.setMessage("Input must be an integer from 0 to 99")
        else:
            result = self.search(val)
            if result:
                msg = "Found {}".format(val)
            else:
                msg = "Value {} not found".format(val)
            self.setMessage(msg)
        self.clearArgument()           
        
    def clickInsert(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input must be an integer from 0 to 99")
        else:
            result = self.insert(val)
            if result:
                msg = "Value {} inserted".format(val) 
            else:
                msg = "Error! Unable to insert" 
            self.setMessage(msg)
        self.clearArgument()
     
    def clickDelete(self):
        val = self.validArgument()
        if val is None:
            self.setMessage("Input must be an integer from 0 to 99")
        else:
            result = self.delete(val)
            if result:
                msg = "Value {} deleted".format(val)
            else:
                msg = "Value {} not found".format(val)
            self.setMessage(msg)
        self.clearArgument()    
        
    def clickFill(self):
        val = self.validArgument()
        if val is None: 
            self.setMessage("Input must be an integer from 0 to 99")
        else:
            if val > self.maxInserts():
                msg = "Error! No room to display"
            else:
                self.fill(val)
                msg = "Fill completed"
            self.setMessage(msg)
        self.clearArgument()
        
    def isAnimated(self):
        return self.animationState == self.RUNNING or self.animationState == self.PAUSED

    def setAnimationState(self, animate):
        if animate: self.animationState = self.RUNNING
        else: self.animationState = self.STOPPED
    
    # The super() method freezes
    # if STOP is pressed
    # Adjusted so completes
    # task, but without animation
    def wait(self, sleepTime):    # Sleep for a user-adjusted period
        if self.animationState and sleepTime >= 0:
            self.canvas.update()
            sleep(self.speed(sleepTime))     
    
    #####################
    ## End Of SKIPLIST ##
    #####################

if __name__ == '__main__':
    s = SkipList()
    s.runVisualization()
