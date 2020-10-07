import time
from tkinter import *
import math
try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *



class Node(object):
    
    # create a linked list node
    #id is used to link the different parts of each node visualization
    def __init__(self, k, color, pos = None, n=None, id=None):
        self.key = k
        self.id = id
        self.next = n  # reference to next item in list
        self.color = color
        
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
    ROW_GAP = 40  
    MAX_ARG_WIDTH = 8
    
    def __init__(self, title="Linked List", maxArgWidth=MAX_ARG_WIDTH, **kwargs):
        super().__init__(title=title, maxArgWidth = maxArgWidth, **kwargs)
        self.title = title        
        self.first = None
        self.prev_id = -1
        self.buttons = self.makeButtons()
        self.list = []
        self.arrow = []
        self.dot = []
        rect, oval, text, arrow =self.firstPointer()
        self.firstPointList= [rect, oval, text, arrow]

    def __len__(self):
        return len(self.list)
     

    def isEmpty(self):
        return not self.first
    
    def generateId(self):
        self.prev_id+=1
        return "item" + str(self.prev_id)
    
    #pointer arrow for search and delete
    def index(self, position):
        x = position % self.LEN_ROW * (self.CELL_WIDTH + self.CELL_GAP) + self.LL_X0 + self.CELL_WIDTH / 2
        y = position // self.LEN_ROW * (self.CELL_HEIGHT + self.ROW_GAP) + self.LL_Y0
        return x, y
    
    #accesses the next color in the pallete
    #used to assign a node's color
    def chooseColor(self):
        color = drawable.palette[self.nextColor]
        self.nextColor = (self.nextColor + 1) % len(drawable.palette)
        return color
    
    #used to calculate coordinates of cell parts
    def x_y_offset(self, pos):
        x_offset = pos%self.LEN_ROW * (self.CELL_WIDTH + self.CELL_GAP)
        y_offset = pos//self.LEN_ROW*(self.CELL_HEIGHT+self.ROW_GAP) 
        return x_offset, y_offset


    #assigns coordinates for the node's text  
    def cell_text(self, pos):
        x_offset, y_offset = self.x_y_offset(pos)
        return self.LL_X0 + self.CELL_HEIGHT  + x_offset, self.LL_Y0 + self.CELL_HEIGHT // 2+y_offset
    
    #assigns coordinates for the dot in the node
    def cell_dot(self, pos):
        x_offset, y_offset = self.x_y_offset(pos)
        return self.canvas.create_oval(self.LL_X0 + self.CELL_HEIGHT*2 - self.DOT_SIZE // 2 + x_offset,
                               self.LL_Y0 + self.CELL_HEIGHT // 2 - self.DOT_SIZE // 2 + y_offset,
                               self.LL_X0 + self.CELL_HEIGHT*2 + self.DOT_SIZE // 2 + x_offset,
                               self.LL_Y0 + self.CELL_HEIGHT // 2 + self.DOT_SIZE // 2+ y_offset, fill="RED", outline="RED", tag = id)
    
    #draws arrow based on position
    #short arrow if not at the end of the line.
    #otherwise draws a long arrow
    def cell_arrow(self, pos):
        x_offset, y_offset = self.x_y_offset(pos)       
             
        if len(self.list)>=3 and pos == 4 or (pos-4)%self.LEN_ROW ==0:
            return (self.canvas.create_line(self.LL_X0 + self.CELL_HEIGHT*2 + x_offset,
                               self.LL_Y0 + self.CELL_HEIGHT // 2 + y_offset,
                               self.LL_X0 + self.CELL_HEIGHT*2 + x_offset,
                              self.LL_Y0 + self.CELL_HEIGHT // 2 + y_offset+self.ROW_GAP/2 + self.CELL_HEIGHT/2,
                                tag=id), self.canvas.create_line(self.LL_X0 + self.CELL_HEIGHT*2 + x_offset,
                               self.LL_Y0 + self.CELL_HEIGHT // 2 + y_offset + self.ROW_GAP / 2 + self.CELL_HEIGHT / 2,
                               self.LL_X0 + self.CELL_HEIGHT*2,
                               self.LL_Y0 + self.CELL_HEIGHT // 2 + y_offset+self.ROW_GAP/2 + self.CELL_HEIGHT/2,
                               tag=id), self.canvas.create_line(self.LL_X0 + self.CELL_HEIGHT*2,
                               self.LL_Y0 + self.CELL_HEIGHT // 2 + y_offset + self.ROW_GAP / 2 + self.CELL_HEIGHT / 2,
                               self.LL_X0 + self.CELL_HEIGHT*2,
                               self.LL_Y0 + self.CELL_HEIGHT // 2 + y_offset + self.ROW_GAP + self.CELL_HEIGHT/2,
                               arrow=LAST, tag=id))
        
        else:
            return  (self.canvas.create_line(self.LL_X0 + self.CELL_HEIGHT*2 + x_offset,
                                    self.LL_Y0 + self.CELL_HEIGHT // 2 + y_offset,
                                    self.LL_X0 + x_offset + self.CELL_WIDTH + self.CELL_GAP,
                                    self.LL_Y0 + self.CELL_HEIGHT // 2 + y_offset,
                                     arrow = LAST,tag = id), )
                
    def arrowSetup(self, insert = False):
        for i in self.arrow:
            for j in i:
                self.canvas.delete(j)
        cur = self.first
        pos = len(self.list) if insert == True else len(self.list)-1
        if insert==True:
            while pos>1:
                x_offset, y_offset = self.x_y_offset(pos) 
                if pos <= len(self.list):
                    cell_arrow = self.cell_arrow(pos)
                    self.arrow.append(cell_arrow)
                pos -=1
                cur = cur.next
        else:
            while pos>0:
                x_offset, y_offset = self.x_y_offset(pos) 
                if pos< len(self.list):
                    cell_arrow = self.cell_arrow(pos)
                    self.arrow.append(cell_arrow)
                pos -=1
                cur = cur.next            
        return self.arrow
        
    
    #draws a cell based on color and text input
    #moves cell into first spot in LL
    #draws the arrows linking the nodes
    def createCell(self, pos = 1,  textSize = '12', val = None, cur = None, color= None):
        self.startAnimations()
        callEnviron = self.createCallEnvironment()
        if not cur: cur = self.first
        if not val: val = cur.key
        x_offset, y_offset = self.x_y_offset(pos)       
        if color == None:color = cur.color
        textX, textY= self.cell_text(pos)
        cell_rect = self.canvas.create_rectangle(self.LL_X0 + x_offset,0, self.LL_X0 + self.CELL_WIDTH + x_offset, self.CELL_HEIGHT, fill= color, tag=id)
        cell_text = self.canvas.create_text(textX, textY -self.LL_Y0, text=val, font=('Helvetica', textSize),tag = id)

        self.moveItemsBy((cell_rect, cell_text), (0, self.LL_Y0 + y_offset), steps = 9, sleepTime = .09)
        cell_dot = self.cell_dot(pos)
        
        handler = lambda e: self.setArgument(str(val))
        for item in (cell_rect,cell_text, cell_dot):
            self.canvas.tag_bind(item, '<Button>', handler)
        self.cleanUp(callEnviron)
        
        return cell_rect, cell_text, cell_dot
        
    #creates the initial "node" that indicates the head of the linked list
    def firstPointer(self, next = None):
        rect = self.canvas.create_rectangle(self.LL_X0 + 45, self.LL_Y0, self.LL_X0*2, self.LL_Y0 +self.CELL_HEIGHT, fill ="gainsboro")
        oval = self.canvas.create_oval(self.LL_X0 + self.CELL_HEIGHT//2 - self.DOT_SIZE // 2 +45,
                                self.LL_Y0 + self.CELL_HEIGHT // 2 - self.DOT_SIZE // 2 ,
                                self.LL_X0 + self.CELL_HEIGHT//2 + self.DOT_SIZE // 2 +45,
                                self.LL_Y0 + self.CELL_HEIGHT // 2 + self.DOT_SIZE // 2, 
                                fill="RED", outline="RED",)
        arrow = None
        if self.first:
            arrow = self.canvas.create_line(self.LL_X0 + self.CELL_HEIGHT//2 + 45,
                        self.LL_Y0 + self.CELL_HEIGHT // 2,
                        self.LL_X0 + self.CELL_HEIGHT//2 + 95 + self.CELL_GAP,
                        self.LL_Y0 + self.CELL_HEIGHT // 2,
                        arrow = LAST)
        text= self.canvas.create_text(self.LL_X0 + self.CELL_HEIGHT//2 + 45, self.LL_Y0 + 10,text="first", font=('Courier', '10'))
        return drawable(None, None, rect), drawable(None, None,oval), drawable(None, None, text), drawable(None, None, arrow)
    
        
    ### ANIMATION METHODS###
    
    #returns the first node in list
    def getFirst(self):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()
        if not self.first: 
            self.cleanUp(callEnviron)
            return
        x_offset, y_offset = self.x_y_offset(1)
        peekBox = self.canvas.create_rectangle(self.LL_X0 + x_offset, 
                                               self.LL_Y0 - (self.CELL_GAP + self.CELL_HEIGHT), 
                                               self.LL_X0+ self.CELL_WIDTH+ x_offset,
                                               self.LL_Y0 - self.CELL_GAP, 
                                               fill = self.OPERATIONS_BG)
        callEnviron.add(peekBox)
        textX, textY = self.cell_text(1)
        firstText = self.canvas.create_text(textX, textY, text=self.first.key, font=('Helvetica', 12),tag = id)
        self.moveItemsBy((firstText,),(0, -(self.CELL_HEIGHT + self.CELL_GAP)), steps = 10, sleepTime = 0.05)
        callEnviron.add(firstText)
        self.cleanUp(callEnviron)        
        return self.first
            
    #erases old linked list and draws empty list
    def newLinkedList(self):
        self.first = None
        self.canvas.delete(self.firstPointList[-1])
        rect, oval, text, arrow = self.firstPointer()
        self.firstPointList =[rect, oval, text, arrow]
        self.size = 0
        self.list = []
        self.dot = []
        self.arrow= []
        return self.first
    
 
    #id is used to link the different parts of each node visualization
    #creates a new Node object, slides all the nodes already in LL to the right
    #draws the new Node- slides it into gap at beginnning of LL
    def insertElem(self, val, pos=1, id=-1, sleepTime=0.07, steps = 3):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()
        
        color = self.chooseColor()
        newNode = Node(val, color, n = self.first)
        if self.first:
            pos = len(self.list)
            for i, n in enumerate(self.list):
                dot = self.dot[i]
                items = (n.display_shape, n.display_val, dot.display_shape)
                if (pos-4) %5 == 0:
                    self.moveItemsBy(items, (-((self.CELL_WIDTH + self.CELL_GAP)*(self.LEN_ROW-1)), (self.CELL_HEIGHT + self.ROW_GAP)), 
                                    steps =steps, sleepTime= sleepTime)                                                    
                else: 
                    self.moveItemsBy(items, (self.CELL_WIDTH+ self.CELL_GAP, 0), steps = steps, sleepTime= sleepTime)              
                self.arrowSetup(insert = True)
                pos -= 1
                             
                       
        node = self.createCell(1, '12', val = val, color = newNode.color, cur = newNode)
        if self.first: 
            arrow = self.cell_arrow(1)
            self.arrow.append(arrow)
        self.dot.append(drawable(None, "RED", node[-1]))  
        self.list.append(drawable(val, color, *node[:-1]))
        self.first = newNode
        if len(self.list) == 1:
            rect, oval, text, first_arrow = self.firstPointer()
            self.firstPointList[-1] = first_arrow
            
        if id==-1:
            id = self.generateId()
            newNode.id = id           
        self.wait(0.5)
        self.cleanUp(callEnviron)
        return val 
    
    #deletes first node in LL
    def deleteFirst(self):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()
        first_arrow =self.firstPointList[-1]

        pos = 1
        x, y = self.index(pos)
        arrow = self.canvas.create_line(x, y - 40, x, y, arrow="last", fill='red')
        
        callEnviron.add(arrow)
        self.window.update()
        ans = self.first
        self.first = ans.next
        n = self.list[-1]
        self.list = self.list[:-1]
        dot = self.dot[-1]
        self.dot = self.dot[:-1]
        items = (n.display_shape, n.display_val, dot.display_shape)
        callEnviron |= set(items)
        self.moveItemsOffCanvas(items)
        
        pos = 1
        for i in range(len(self.list)-1, -1, -1):
            n = self.list[i]
            dot = self.dot[i]
            items = (n.display_shape, n.display_val, dot.display_shape)                
            if (pos-4)%self.LEN_ROW == 0:
                self.moveItemsBy(items, (((self.CELL_WIDTH + self.CELL_GAP)*(self.LEN_ROW-1)), -(self.CELL_HEIGHT + self.ROW_GAP)))
            else:
                self.moveItemsBy(items, (-(self.CELL_WIDTH+ self.CELL_GAP), 0))
            pos += 1
        if len(self.list)== 0: 
            self.canvas.delete(first_arrow.display_shape)
            self.firstPointList[-1]= None
        self.arrowSetup()
          
        self.wait(1.0)
        callEnviron.add(ans.id)
        self.cleanUp(callEnviron)
        return ans.key        
        
    
    # delete a node from the linked list, returning the key
    # pair of the deleted node. Attempt to find and delete
    # the first node containing key
    def delete(self, key):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()
                
        first_arrow = self.firstPointList[-1]
        pos = 1
        x, y = self.index(pos)
        arrow = self.canvas.create_line(x, y - 40, x, y, arrow="last", fill='red')
    
        callEnviron.add(arrow)
        self.window.update()
        
        pos = 1
        index = len(self.list)-1
        cur = prev = self.first
        if cur.key == key:
            self.first = self.first.next   
            
        else:
        
            # loop until we hit end, or find key,
            # keeping track of previously visited node
            n = 0
            while n< len(self.list) and cur.key != key:
                self.wait(0.7)    
                arrow = (arrow, )
                if (pos-4)%self.LEN_ROW == 0:
                    self.moveItemsBy(arrow, (-((self.CELL_WIDTH + self.CELL_GAP)*(self.LEN_ROW-1)), (self.CELL_HEIGHT + self.ROW_GAP)))
                    
                else:
                    self.moveItemsBy(arrow, ((self.CELL_WIDTH+ self.CELL_GAP), 0))
                callEnviron.add(arrow)
            
                prev = cur
                cur = cur.next
                pos +=1
                n +=1
                index -= 1
                
    
            # A node with this key isn't on list
            if n == len(self.list): 
                self.cleanUp(callEnviron)
                return

        # otherwise highlight the found node
        x_offset, y_offset = self.x_y_offset(pos)
        cell_outline = self.canvas.create_rectangle(self.LL_X0 + x_offset-5,
                                   self.LL_Y0+y_offset-5,
                                   self.LL_X0 + self.CELL_WIDTH + x_offset+5,
                                   self.LL_Y0 + self.CELL_HEIGHT+y_offset+5, outline = "RED", tag=id)
        
        #remove the node from the list and
        self.wait(0.4)
        
        prev.next = cur.next
        move = self.list[index]
        dot  = self.dot[index]
        
        #update the lists of drawable nodes and dots to reflect the deletion
        if cur == self.first: self.first = cur.next
        self.list[index:index+1] = []
        if len(self.list) == 0: self.first = None
        self.dot[index:index+1] =[]
       
        move = move.display_shape, move.display_val, dot.display_shape, cell_outline        
        callEnviron |= set(move)
        self.moveItemsOffCanvas(move)
        
        #slide all the nodes over to fill in the gap left by deleted node
        for i in range(index-1, -1, -1):
            n = self.list[i]
            dot = self.dot[i]
            items = n.display_shape, n.display_val, dot.display_shape
            if (pos-3) %5 == 1:
                self.moveItemsBy(items, (((self.CELL_WIDTH + self.CELL_GAP)*(self.LEN_ROW-1)), -(self.ROW_GAP+ self.CELL_HEIGHT)))
            else:
                self.moveItemsBy(items, (-(self.CELL_WIDTH + self.CELL_GAP), 0))
            pos += 1
        if self.first == None:
            self.canvas.delete(first_arrow.display_shape)
            self.firstPointer()
            self.firstPointList[-1]= None            
        self.arrowSetup()
        self.wait(1)
        callEnviron.add(cur.id)
        self.cleanUp(callEnviron)
        
        # return the key/data pair of the found node        
        return cur.key    
    
        
    def search(self, key):
        self.startAnimations()
        callEnviron = self.createCallEnvironment()  
        cur = self.first
        pos = 1
        x, y = self.index(pos)
        arrow = self.canvas.create_line(x, y - 40, x, y, arrow="last", fill='red')
        callEnviron.add(arrow)
        pos = 0
        # go through each Element in the linked list
        while pos!= len(self.list) and cur:
            self.window.update()

            # if the value is found
            if cur.key == key:
                
                #highlight the box of the node that contains the search key
                x_offset, y_offset = self.x_y_offset(pos+1)
                cell_outline = self.canvas.create_rectangle(self.LL_X0 + x_offset-5,
                                           self.LL_Y0+y_offset-5,
                                           self.LL_X0 + self.CELL_WIDTH + x_offset+5,
                                           self.LL_Y0 + self.CELL_HEIGHT+y_offset+5, outline = "RED", tag=id)

                callEnviron.add(cell_outline)
                self.wait(1.0)

                # update the display
                self.cleanUp(callEnviron)
                return pos

            # if the value hasn't been found, wait and then move the arrow over one cell
            self.wait(0.7)
            cur = cur.next
           
            arrow = (arrow, )
            if (pos-4)%self.LEN_ROW == 0: 
                self.moveItemsBy(arrow, (-((self.CELL_WIDTH + self.CELL_GAP)*(self.LEN_ROW-1)), (self.CELL_HEIGHT + self.ROW_GAP)))
            else: 
                self.moveItemsBy(arrow, (self.CELL_WIDTH + self.CELL_GAP,0))
            pos+=1
            
        self.cleanUp(callEnviron)
        return None
            
    
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
        self.canvas.delete('all')
        self.newLinkedList()
    
    def clickGetFirst(self):
        cur = self.getFirst()
        if cur!= None: 
            val = cur.key
            msg = "The first node is {}".format(val)
        else: msg = "ERROR: Linked list is empty"
        self.setMessage(msg)
        self.clearArgument()
    

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
    ll.runVisualization()
    
