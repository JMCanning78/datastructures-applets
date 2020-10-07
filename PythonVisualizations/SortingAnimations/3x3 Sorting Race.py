# The following code is a race between different sorting algorithms. 
# The animation sorts nine arrays simultaneously. The arrays are either randomly
# shuffled, partially shuffled, or set in reverse order. The animation then uses
# bubble sort, selection sort, or insertion sort to resort the arrays.


import Draw
import math
import random
import time
import multiprocessing
import queue
import heapq

# Set values for the canvas size, size of the box, number of bars, size of the 
# space for the slider at the bottom, height of arrows, and y spacing factor
XVALUE = 1200
YVALUE = 600
BOX = 300
BARS = 25
SPACE = 40
ARROW = 15
Y = (YVALUE - BOX - SPACE - ARROW) // 22
      
# A class to make the queue into a priority queue
class PriorityQueue(object):
      def __init__(self, q):
            self.__q = q
            self.__h = []  # the prioritized list of elements
        
      # remove the element from the head of the prioritized queue and
      # return it.
      def get(self):
            emptyQueue = False
            while len(self.__h) == 0 or not emptyQueue: 
                  try:
                        item = self.__q.get(block=False)
                        heapq.heappush(self.__h, item)
                  except queue.Empty:
                        emptyQueue = True
                
            # if you made it here, then len(self.__h) > 0  and emptyQueue == True
            return heapq.heappop(self.__h)
    
      # return the element at the head of the prioritized queue, but 
      # does NOT return the element. If you want to consume the element
      # at the head of the prioritized queue, you must then invoke get()
      def peek(self):
            emptyQueue = False
            while len(self.__h) == 0 or not emptyQueue: 
                  try:
                        item = self.__q.get(block=False)
                        heapq.heappush(self.__h, item)
                  except queue.Empty:
                        emptyQueue = True     
                
            return self.__h[0]

# A class for all sorter elements
class Sorter(object):
      
      # Initialize class attributes for number of sorts, number of sorts done,
      # the queue and the priority queue.
      __sorts = 0
      __numDone = 0
      __q = multiprocessing.Queue()
      __pq = PriorityQueue(__q)
      
      def __init__(self, name, row, col):
            
            # Increment the number of sorts attribute
            Sorter.__sorts += 1
            
            # Initialize attribues to None that will be initialized in self.draw
            self.__array = None
            self.__bars = None
            self.__compX = None
            self.__compY = None
            self.__comp = None            
            
            # Create attributes for the x and y coordinate of the box 
            border = (XVALUE - 3 * BOX)/4           
            yBox = (row+1) * BOX//3 + (Y * 8 * row)
            
            self.__xOrigin = int(border + (BOX + border)*col)
            self.__yOrigin = Y + yBox - BOX//3
            
            # Create attributes for the target, name of the type of sort, and its row
            self.__target = name
            self.__name = name.__name__
            self.__row = row
            
            # Create two attributes for the two arrows for each sort
            Draw.setColor(Draw.RED)
            headLength = 2*ARROW//5
            bodyLength = 3* ARROW // 5            
                        
            self.__arrow1 = (Draw.filledPolygon(\
                  [1000, 1000, 1000 + (max(5,BOX/BARS))//2, 1000 - headLength, \
                   1000 + max(5,BOX/BARS), 1000]), Draw.filledRect(\
                         1000 + round(max(5,BOX/BARS)/3), 1000, \
                         round(max(5,BOX/BARS)/3), bodyLength))
            self.__arrow2 = (Draw.filledPolygon(\
                  [1000, 1000, 1000 + (max(5,BOX/BARS))//2, 1000 - headLength, \
                   1000 + max(5,BOX/BARS), 1000]), Draw.filledRect(\
                         1000 + round(max(5,BOX/BARS)/3), 1000, \
                                   round(max(5,BOX/BARS)/3), bodyLength))
      
      @staticmethod
      def getPQ(): return Sorter.__pq
      
      @staticmethod
      def getNumDone(): return Sorter.__numDone
      
      @staticmethod
      def allDone(): 
            return Sorter.__sorts == Sorter.__numDone
            
      # Draw the bars and the displays under them
      def draw(self, array):
            
            # Initialize the arrays to hold the numbers and the bars 
            self.__array = array
            if self.__bars:
                  for i in self.__bars:
                        Draw.delete(i)
            self.__bars = []
            
            # Set values for the color spectrum
            freq = 0.2
            phase = 2*math.pi/3
            center = 128
            width = 127       
                        
            # Draw a bordering box
            Draw.setColor(Draw.BLACK)
            Draw.rect(self.__xOrigin - 1, self.__yOrigin -1, BOX+2, BOX//3+2)
                        
            # Loop through each bar in the array
            for i in range(len(array)): 
                  
                  # Set the three color components and height of that bar. 
                  red = int(math.sin(freq*array[i]) * width + center)
                  green = int(math.sin(freq*array[i] + phase) * width + center)
                  blue = int(math.sin(freq*array[i] + 2*phase) * width + center)
            
                  height = int(BOX//3/BARS * (array[i]+1))
                  
                  # Set the color, draw the bar, and add it to the array. 
                  Draw.setColor(Draw.color(red, green, blue))
                  bar = Draw.filledRect(i*int(BOX/BARS) +self.__xOrigin, \
                                        self.__yOrigin+ BOX//3-height,\
                               int(BOX/BARS), height)
                  
                  self.__bars += [bar]
            
            # If you haven't yet made the bottom display, draw it
            if self.__comp == None:
                  
                  # Draw a display below the graph indicating the type of sort and 
                  # number of comparisons done. 
                  font = min(Y, BOX//11)
                  
                  Draw.setColor(Draw.BLACK)
                  Draw.setFontSize(font)
                  
                  Draw.string(self.__name + " Sort", self.__xOrigin, \
                              self.__yOrigin + BOX//3 + ARROW + Y)
                  Draw.string("Comparisons:", self.__xOrigin, \
                              self.__yOrigin + BOX//3 + ARROW + Y*3)
                  
                  # Save as attributes the item used for drawing the string and
                  # the x and y coordinates of that element
                  self.__compX = self.__xOrigin + int(font*9)
                  self.__compY = self.__yOrigin + BOX//3 + ARROW + Y*3
                  self.__comp = Draw.string(0, self.__compX, self.__compY)                   
      
      # Redraw the shuffled array and create the sorting process 
      def sortProcess(self, array):
            Sorter.draw(self, array)
            self.__processID = multiprocessing.Process(\
                  target=self.__target, args=(Sorter.__q, self.__array, \
                                              self.__name, self.__row)) 
                 
      # Start the sorting process
      def go(self):
            self.__processID.start()
            
      # Using the message at the first position in the array, translate the 
      # message and change the number of comparisons, location of the arrows and 
      # location of the bars accordingly.
      def sorting(self, message):
            
            # Keep track of how many sorts are finished
            if message[4] == "Done": 
                  Sorter.__numDone += 1
                  
                  # Print out which sort finished and how long it took.
                  print(Sorter.__numDone, self.__name, self.__row, \
                        time.time()-message[5], flush=True)
                  
                  # Move the arrows out of the frame
                  self.moveArrows(-1000, -1000)
                
            # Otherwise, move the arrows to the two items being compared and 
            # increment the number of comparisons. 
            else: 
                  self.moveArrows(self.__bars[message[4]],self.__bars[message[5]])
                  self.updateComp(message[0])
                  
                  # If a swap is needed, animate the swap and swap the
                  # positions in the array.
                  if message[-1] != None:
                        self.swap(self.__bars[message[4]], self.__bars[message[5]])
                        
                        tempposition = self.__bars[message[4]]
                        self.__bars[message[4]] = self.__bars[message[5]]
                        self.__bars[message[5]] = tempposition                                               
                             
      
      # Update the string indicating the number of comparisons done
      def updateComp(self, comp):
            
            Draw.setColor(Draw.BLACK)
            
            # Delete the corresponding old display and create a new one using 
            # the x and y saved in init             
            Draw.delete(self.__comp)
            self.__comp = Draw.string(str(comp), self.__compX, self.__compY)
            
                  
      # Move the arrows to point to the items being compared
      def moveArrows(self, bar1, bar2):
            
            headLength = 2*ARROW//5
            
            # If the sort is not done, set the x coordinates to the x value of the bars 
            if not bar1 == -1000:
                  x1 = Draw.coords(bar1)[0]
                  x2 = Draw.coords(bar2)[0]
            
            # If the sort is done, set the x coordinates to offscreen 
            else: 
                  x1 = -1000
                  x2 = -1000
                  
            Draw.moveTo(self.__arrow1, x1, self.__yOrigin+ BOX//3+ headLength+2)
            Draw.moveTo(self.__arrow2, x2, self.__yOrigin+ BOX//3+ headLength+2)      
      
      # Swap the 2 bars
      def swap(self, bar1, bar2): 
         
            # Get the coordinates of the two bars
            coordsBar1 = Draw.coords(bar1)
            coordsBar2 = Draw.coords(bar2)
            
            # Swap their x coordinates but keep their y coordinates/heights
            Draw.moveTo(bar1, coordsBar2[0], coordsBar1[1])
            Draw.moveTo(bar2, coordsBar1[0], coordsBar2[1])      
      
      
# Draw the row header displays
def rowHeader():
      
      # Draw the row headers
      shuffles = ["Random", "Shuffle", "Mostly", "Sorted", None, "Reversed"]
      Draw.setFontSize(10)
      Draw.setColor(Draw.BLACK)
      
      # Loop through the rows and draw the row headers
      for i in range(len(shuffles)//2):                  
            Draw.string(shuffles[i*2], 8, (i+1)*BOX//3+(Y*8*i+Y)-2*(BOX//3)//3)
            Draw.string(shuffles[i*2 + 1], 8,(i+1)*BOX//3+(Y*8*i+Y)-(BOX//3)//2)  


# Create a slider to indicate speed.
def slider():
      
      l = XVALUE/3  # Bar starts 1/3 the way across & is 1/3 the canvas length
      h = (SPACE - Y) //4   # Height of the bar
      y = YVALUE - SPACE + 2*h  # Where the horizontal bar starts
     
      # Draw the line
      Draw.setColor(Draw.BLACK)
      Draw.filledRect(l, y, l, h)
      
      # Draw the tab
      tab = Draw.filledRect(3*l/2 - (h/2)/2, y - (h*3)/3, h/2, h*3)
      
      # Return a tuple with the measurments for the length, top y of bar,
      # bottom y of bar, y of tab, width of tab, and the tab item 
      return (l, y, y+h, y - (h*3)/3, h/2, tab)


# Shuffle the position of the bars in the array
def shuffle(array):
   
      # Work backwards from the end of the array
      for i in range(len(array)-1, 0, -1):
      
            # Select from the unshuffles positions, including i
            j = random.randint(0, i)            
                  
            # Swap the two positions in the array
            tempposition = array[i]
            array[i] = array[j]
            array[j] = tempposition 


# Partially shuffle the array so it is still mostly sorted
def partialShuffle(array):
      
      # Work backwards from the end, shuffling every fourth bar 
      for i in range(len(array)-1, 0, -4):
      
            # Select from the unshuffles positions, including i
            j = random.randint(0, i)           
                  
            # Swap the two positions in the array
            tempposition = array[i]
            array[i] = array[j]
            array[j] = tempposition


# Completely reverse the positions of the bars
def reverse(array):
      
      # Loop through the first half of the elements
      for i in range(len(array)//2):                
                  
            # Swap that elements position with the element in the 
            # equivalent position on the end
            tempposition = array[i]
            array[i] = array[i-(2*i + 1)]
            array[i-(2*i + 1)] = tempposition 
        

# Sort the first column according to bubble sort and record the number of 
# comparisons and time the sort takes         
def Bubble(q, array, name, row):
      
      # Initialize the variable to record time and number of comparisons
      initTime = time.time()
      comp = 0
      
      # Loop through all but the last element
      for i in range(BARS-1):
         
            # Loop through the unsorted bars
            for j in range(0, BARS-i-1):
                  
                  # Increment the comp variable
                  comp +=1
                  
                  # If the bar is taller than the bar to its right, swap position
                  if array[j] > array[j+1]: 
                        tempposition = array[j]
                        array[j] = array[j+1]
                        array[j+1] = tempposition  
                        
                        # Send a message to main to swap the variables and
                        # increment the number of comparisons.
                        q.put([comp, random.random(), name, row, j, j+1])
                                                 
                  # If the bars don't need to be swapped, send a message only to 
                  # increment the number of comparisons
                  else:
                        q.put([comp, random.random(), name, row, j, j+1, None])
      
      # Send a message that the sort is done and indicate the time it took
      q.put([comp+1, random.random(), name, row, "Done", initTime])
 
      
# Sort the second column according to selection sort and record the number of 
# comparisons and time the sort takes
def Selection(q, array, name, row):
      
      # Initialize the variables to record time and number of comparisons
      initTime = time.time()
      comp = 0
      
      # Loop through all but the last element
      for i in range(BARS-1):
         
            # Initialize the values of the minimum and the position of the minimum
            mini = array[i]
            place = i
         
            # Loop through the unsorted bars
            for j in range(i, BARS-1):
            
                  # Increment the comp variable
                  comp += 1
            
                  # Send a message to main to increment the number of comparisons.
                  if not j == BARS-1:
                        q.put([comp, random.random(), name, row, j+1, place, None])
                        
                  # If the next bar is smaller than the indicated min, change the mini
                  # and place variables to account for the true mini and its position
                  if array[j+1] < mini: 
                        mini = array[j+1]
                        place = j+1
                  
            
            # Swap the position of the i with the minimum
            tempposition = array[i]
            array[i] = array[place]
            array[place] = tempposition                    
            
            # Send a message to main to swap the variables and increment the 
            # number of comparisons
            q.put([comp, random.random(), name, row, i, place])
      
      # Send a message that the sort is done and indicate the time it took
      q.put([comp+1, random.random(), name, row, "Done", initTime])      
   

# Sort the third column according to insertion sort and record the number of
# comparisons and time the sort takes
def Insertion(q, array, name, row):
      # Initialize the variables to record time and number of comparisons
      initTime = time.time()
      comp = 0

      # Loop through all but the first element
      for i in range(1, BARS):
         
            # Initialize val as the value you are analyzing and pos as the position
            # you are trying to fill
            val = array[i]
            pos = i-1
            
            # While the bar is less than the bar to its left, loop through from 
            # right to left
            while pos >= 0 and val < array[pos]:
               
                  # Increment the comp variable
                  comp +=1
                  
                  # Swap the bar with the bar on the left
                  tempposition = array[pos]
                  array[pos] = val
                  array[pos+1] = tempposition
                  
                  # Send a message to main to swap the variables and increment  
                  # the number of comparisons
                  q.put([comp, random.random(), name, row, pos, pos+1])                
                  
                  # Set the val to the value on the left (so you are working  
                  # with the same bar) and pos to the position on the left
                  val = array[pos]             
                  pos -= 1
                  
            # When you fall out of the while loop, it indicates that another 
            # comparison was done, although a swap was not needed. Therefore, 
            # send a message to increment the number of comparisons
            if not pos == -1:
                  comp +=1
                  q.put([comp, random.random(), name, row, pos, pos + 1, None])

      
      # Send a message that the sort is done and indicate the time it took
      q.put([comp+1, random.random(), name, row, "Done", initTime])      


# Update the speed of the animation 
def speed(speedScale, x, y, speedValue):  
      
      # Reminder: speedScale is a tuple with the measurments for the length (0), 
      # top y of bar (1), bottom y of bar (2), y of tab (3), width of tab (4), 
      # and the tab item (5)
      
      # Test if the bar was clicked, adjust speedValue, and move the tab
      if x >= speedScale[0] and x <= 2*speedScale[0] and \
         y >= speedScale[1] and y <= speedScale[2]:
            speedValue = int((x - speedScale[0])/speedScale[0] * 100)
            Draw.moveTo(speedScale[-1], speedScale[0] + \
                        int(speedScale[0] / 100 * speedValue)-speedScale[4]/2,\
                        speedScale[3])
 
      return speedValue      


# Sort the shuffled arrays
def sortingProcess(speedScale, method, d):
  
      # Initialize the variables for the current speedValue and number of comparisons
      speedValue = 50
      comps = 1
      
      # As long as they are still sorting...
      while not Sorter.allDone():

            # Get values for what was clicked to see if the speed was changed
            clickedX= 0
            clickedY = 0
            if Draw.mousePressed():
                  if Draw.mouseLeft():
                        clickedX = Draw.mouseX()
                        clickedY = Draw.mouseY()
                        speedValue = speed(speedScale, clickedX, \
                                           clickedY, speedValue)
            
            # Wait a certain amount of time after every sort did a comparison. 
            # Time waiting is determined by the user
            pq = Sorter.getPQ()
           
            if pq.peek()[0] > comps:
                  Draw.show()
                  time.sleep((1-(speedValue/100))/2)
                  comps += 1
                 
            # Get the next message in the queue
            message = pq.get() 
            d[message[2] + str(message[3])].sorting(message)
            
      Draw.show()
              

def main():
      Draw.setCanvasSize(XVALUE, YVALUE)
      
      # Initialize the arrays we will be sorting and which methods are used
      arrays = [[j for j in range(BARS)] for i in range(3)]
      method = [Bubble, Selection, Insertion] 
      
      # Create a dictionary to store all the Sorter objects 
      d = {}
      for i in range(3):
            for j in range(len(method)):
                  d[method[j].__name__ + str(i)] = Sorter(method[j], i, j)
      Draw.show()
      
      # Draw the original displays
      for i in d:
            d[i].draw(arrays[0])
            
      # Draw the row headers and slider
      rowHeader()
      speedScale = slider()
      Draw.show()
      time.sleep(1)
      
      # Shuffle the arrays
      shuffle(arrays[0])  
      partialShuffle(arrays[1])
      reverse(arrays[2])
      
      # Redraw the shuffled displays and create a process to later sort
      for i in d:
            d[i].sortProcess(arrays[int(i[-1])])
      
      Draw.show()
      time.sleep(0.01)      
      
      # Start the processes
      for i in d:
            d[i].go()
      time.sleep(1)
            
      # Sort the arrays
      sortingProcess(speedScale, method, d)
      
      
# Run main
if __name__ == "__main__":
      main()