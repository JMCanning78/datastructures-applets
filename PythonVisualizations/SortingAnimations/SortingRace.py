#An animation of a race between sorting algorithms to demonstrate their 
#strengths and weaknesses. 
#Includes representation of O(n^2) vs. O(nlogn), best and worst case scenarios.
#Each algorithm is animated as a car competing in the race. 
#The following algorithms are represented: 
#bubble sort, selection sort, insertion sort, merge sort, and quick sort. 
#The algorithms are raced under 3 sets of conditions: 
#a random array of 10 elements, a random array of 100 elements, and an almost 
#sorted array of 100 elements. 
#Algorithms sort the same array concurrently using multiprocessing.
#Speed is measured based on the number of comparisons necessary to sort 
#the array (fewer comparisons=faster). A priority queue is used to align 
#progress based on number of comparisons done. 
#The distance to the finish line represents the number of inversions remaining 
#in the array to be sorted.

import Draw
import random
import time
import multiprocessing
import queue
import heapq

class Car(object):
   def __init__(self,x,y,color,letter):
      self.__x = x
      self.__y = y
      self.__color = color
      self.__letter = letter
      self.__draw = self.drawCar()
         
   def drawCar(self): #draws a car
      #top
      Draw.setColor(self.__color)
      a=Draw.filledOval(self.__x,self.__y+15,120,40)
      b=Draw.filledOval(self.__x+20,self.__y,80,40)
      
      #window
      Draw.setColor(Draw.LIGHT_GRAY)
      c=Draw.filledOval(self.__x+25,self.__y+5,70,30)
      
      #bottom
      Draw.setColor(self.__color)
      d=Draw.filledRect(self.__x+25,self.__y+20,70,15)
      e=Draw.filledRect(self.__x,self.__y+35,120,20)
      
      #wheels
      Draw.setColor(Draw.BLACK)
      f=Draw.filledOval(self.__x+20,self.__y+40,25,25)
      g=Draw.filledOval(self.__x+75,self.__y+40,25,25)
      Draw.setColor(Draw.WHITE)
      h=Draw.filledOval(self.__x+25,self.__y+45,15,15)
      i=Draw.filledOval(self.__x+80,self.__y+45,15,15)
      
      #letter
      Draw.setFontSize(30)
      Draw.setColor(Draw.BLACK)
      j=Draw.string(self.__letter,self.__x+50,self.__y+20) 
      
      return [a,b,c,d,e,f,g,h,i,j]
   
   def move(self,message,totalInversions): #moves car based on inversions removed
      step = 480/totalInversions #total distance/total inversions=
                                 #one "step" per inversion removed                          
      Draw.moveTo(self.__draw,\
                  self.__x+(totalInversions-message[2])*step,self.__y)  
      
   def reset(self): #moves cars back to starting positions
      Draw.moveTo(self.__draw,self.__x,self.__y)
      
#priority queue to order messages based on number of comparisons
class PriorityQueue(object): # by Prof. Alan Broder
   def __init__(self,q):
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
   
    
# Sort the Array using bubble sort  
#original sort code by Prof. Alan Broder
def bubbleSort(a,q,bubbleInversions): 
   
   numComparisons=0

   # outer loop from right to left
   for last in range(len(a)-1, 0, -1):   
         
      # inner loop goes left to right
      for inner in range(last):      
            
         # If element to right of inner is smaller, then swap!
         if a[inner] > a[inner+1]:  
            temp       = a[inner]   
            a[inner]   = a[inner+1] 
            a[inner+1] = temp
            
         
            #for each swap, remove one inversion     
            bubbleInversions-=1
            
         numComparisons+=1
         #after numComparisons and inversions have both been incremented, 
         #send message
         q.put([numComparisons,"bubble",bubbleInversions])
   
   #send message that sort is done            
   q.put([numComparisons,"done","Bubble Sort"])
   
   
# Sort by selecting min and swapping min to leftmost  
#original sort code by Prof. Alan Broder
def selectionSort(a,q,selectionInversions):  
   
   numComparisons=0
   
   for outer in range(len(a)-1): 
      min = outer                                 # Assume min is leftmost
         
      for inner in range(outer+1, len(a)): # Hunt to right
         if a[inner] < a[min]:      # If we find new min,
            min = inner                           # update the min index
         numComparisons+=1 
           
         
      # __a[min] is smallest among __a[outer]...__a[__nItems-1]
      temp      = a[outer] # Swap leftmost and min
      a[outer] = a[min]
      a[min]   = temp
      
       
      
      #for each step that min moved left, remove one inversion
      selectionInversions-=(min-outer)
      
      #for any number with position between outer and min that is greater 
      #than outer (now in min's position), add one inversion
      #for any number between outer and min that is less than outer, 
      #remove one inversion
      
      for i in range (outer+1,min):
         if a[i]>a[min]:
            selectionInversions+=1
         elif a[i]<a[min]:
            selectionInversions-=1
      
      #after numComparisons and inversions have both been incremented, 
      #send message      
      q.put([numComparisons,"selection",selectionInversions]) 
      
   #send message that sort is done  
   q.put([numComparisons+1,"done","Selection Sort"])
   
# Sort by repeated inserts   
#original sort code by Prof. Alan Broder
def insertionSort(a,q,insertionInversions):          
   
   numComparisons=0
   
   for outer in range(1, len(a)): # Mark one element
      temp = a[outer]             # Store marked elem in temp
      inner = outer                      # Inner loop starts at mark
         
      while inner > 0 and temp < a[inner-1]: # If marked
         a[inner] = a[inner-1] # elem smaller, then
         inner -= 1  # shift elem to right
      
         #for each shift left, remove one inversion
         insertionInversions-=1
         
         numComparisons+=1
         #after numComparisons and inversions have both been incremented, 
         #send message         
         q.put([numComparisons,"insertion",insertionInversions])
      
      a[inner] = temp             # Move marked elem to 'hole'
      
   #send message that sort is done     
   q.put([numComparisons,"done","Insertion Sort"])   
   
   
# Iterative Merge sort (Bottom Up)  
#source: https://www.geeksforgeeks.org/iterative-merge-sort/
# Contributed by Madhur Chhangani [RCOEM] 
  
# Iterative mergesort function to  
# sort arr[0...n-1]  
def mergeSort(a,q,mergeInversions): 
   
   numComparisons=0
   current_size = 1
   
   # Outer loop for traversing Each  
   # sub array of current_size  
   while current_size < len(a) - 1:
      
      left = 0
      # Inner loop for merge call  
      # in a sub array  
      # Each complete Iteration sorts  
      # the iterating sub array  
      while left < len(a)-1:
         
         # mid index = left index of  
         # sub array + current sub  
         # array size - 1  
         mid = min((left + current_size - 1),(len(a)-1)) 
           
         # (False result,True result)  
         # [Condition] Can use current_size  
         # if 2 * current_size < len(a)-1  
         # else len(a)-1  
         right = ((2 * current_size + left - 1,  
                 len(a) - 1)[2 * current_size  
                     + left - 1 > len(a)-1])  
                           
         # Merge call for each sub array  
         n1 = mid - left + 1
         n2 = right - mid  
         
         # create temp arrays
         L = [0] * n1  
         R = [0] * n2  
         
         # Copy data to temp arrays L[] and R[] 
         for i in range(0, n1):  
            L[i] = a[left + i]  
         for i in range(0, n2):  
            R[i] = a[mid + i + 1]  
       
         # Merge the temp arrays back into arr[l..r] 
         i, j, k = 0, 0, left  
         while i < n1 and j < n2:  
            if L[i] > R[j]:
               a[k] = R[j]  
               j += 1
               
               #if the next value comes from the Right, remove # of inversions
               #corresponding to # of values left in Left               
               mergeInversions-=len(L)-i
               
            else:
               a[k] = L[i]  
               i += 1
            k+=1
            
            numComparisons+=1 
            #after numComparisons and inversions have both been incremented, 
            #send message            
            q.put([numComparisons,"merge",mergeInversions])
         
         # Copy the remaining elements of L[], if there are any         
         while i < n1:
            a[k] = L[i]  
            i += 1
            k += 1
         # Copy the remaining elements of R[], if there are any  
         while j < n2:
            a[k] = R[j]  
            j += 1
            k += 1 
            
         left = left + current_size*2
         
      # Increasing sub array size by  
      # multiple of 2  
      current_size = 2 * current_size
      
   #send message that sort is done           
   q.put([numComparisons,"done","Merge Sort"])
   


# Python program for implementation of Quicksort  
#source: https://www.geeksforgeeks.org/python-program-for-iterative-quick-sort/
#contributed by Mohit Kumra 
# Function to do Quick sort 
# arr[] --> Array to be sorted, 
# l  --> Starting index, 
# h  --> Ending index 
def quickSort(arr,q,quickInversions):
   numComparisons=0
   l=0
   h=len(arr)-1
  
   # Create an auxiliary stack 
   #keeps track of low and high index of each subarray to be sorted
   stack = [0] * len(arr) 
  
   # initialize top of stack 
   top = -1
  
   # push initial values of l and h to stack 
   top = top + 1
   stack[top] = l 
   top = top + 1
   stack[top] = h 
  
   # Keep popping from stack while is not empty 
   #pops 2 values at a time and works on the subarray between those indexes
   while top >= 0: 
  
      # Pop h and l 
      h = stack[top] 
      top = top - 1
      l = stack[top] 
      top = top - 1
  
      # Set pivot element at its correct position in 
      # sorted array 
      # Takes last element as pivot, places 
      # the pivot element at its correct position in sorted 
      # array, and places all smaller (smaller than pivot) 
      # to left of pivot and all greater elements to right 
      # of pivot 
      i = (l-1)         # index of smaller element 
      pivot = arr[h]     # pivot 
    
      for j in range(l, h): 
    
         # If current element is smaller than or 
         # equal to pivot 
         if   arr[j] <= pivot: 
           
            # increment index of smaller element 
            i = i+1 
            #swap into left side
            arr[i],arr[j] = arr[j],arr[i]
            
            #if the value switched into i did not replace itself,
            #remove one inversion
            if arr[i]!=arr[j]: quickInversions-=1
            #for numbers in between: 
            #for each step moved by smaller, remove 1 inversion
            #if smaller than larger number, remove 1
            #if greater than larger number, add 1            
            for k in range(i+1,j):
               quickInversions-=1
               if arr[k]<arr[j]:      quickInversions-=1
               elif arr[k]>arr[j]:    quickInversions+=1  
                  
         numComparisons+=1   
         
      #swap pivot into proper place   
      arr[i+1],arr[h] = arr[h],arr[i+1] 
         
      #calculate inversions using same logic as above
      if arr[i+1]!=arr[h]: quickInversions-=1
                  
      for k in range(i+2,h):
         quickInversions-=1
         if arr[k]<arr[h]:      quickInversions-=1
         elif arr[k]>arr[h]:    quickInversions+=1  
               
           
      #after all inversions are calculated, send message         
      q.put([numComparisons,"quick",quickInversions])         
        
      p = i+1
  
      # If there are elements on left side of pivot, 
      # then push left side to stack 
      if p-1 > l: 
         top = top + 1
         stack[top] = l 
         top = top + 1
         stack[top] = p - 1
  
      # If there are elements on right side of pivot, 
      # then push right side to stack 
      if p+1 < h: 
         top = top + 1
         stack[top] = p + 1
         top = top + 1
         stack[top] = h 
         
   #send message that sort is done           
   q.put([numComparisons,"done","Quick Sort"])   

                  
#counts number of inversions
def countInversions(a):
   ans=0
   for i in range (len(a)):
      for j in range (i+1, len(a)):
         if a[i]>a[j]: #if number is larger than subsequent number, 
            ans+=1     #add inversion
   return ans   

#flashes message on bottom of canvas
def flash (words,x):
   Draw.setColor(Draw.BLACK)
   Draw.setFontSize(36)      
   w=Draw.string(words,x,550)
   Draw.show()
   time.sleep(2)
   Draw.delete(w)  
   
#draws title of race   
def drawTitle(name, a):
   Draw.setColor(Draw.BLACK)
   Draw.setFontSize(20)
   n=Draw.string(name,100,6)
   d=Draw.string("Distance: " +str(len(a))+ " elements",100,28)
   c=Draw.string("Comparisons: ",100,50)
   
   return [n,d,c]


def race(a, cars): 
   #count inversions and assign initial number to each sort
   totalInversions = bubbleInversions = selectionInversions \
      = insertionInversions = mergeInversions = quickInversions = \
      countInversions(a)
   print("total inversions=", totalInversions)
   
   #create queue
   q = multiprocessing.Queue()
   prioritized = PriorityQueue(q)
   jobs = [ 
      multiprocessing.Process(target=bubbleSort, args=(a,q,bubbleInversions)),\
      multiprocessing.Process(target=selectionSort, args=(a,q,selectionInversions)),\
      multiprocessing.Process(target=insertionSort, args=(a,q,insertionInversions)),\
      multiprocessing.Process(target=mergeSort, args=(a,q,mergeInversions)),\
      multiprocessing.Process(target=quickSort, args=(a,q,quickInversions))
   ]  
   
   #starting message
   time.sleep(1)
   flash("On your marks",260)
   flash("get set",300)
   flash("SORT!",300)
  
   #initialize comparisons string
   Draw.setFontSize(20)
   comps = 0
   compstr=Draw.string(str(comps),232,50)
   Draw.show()    
   
   #initialize start and end time
   startTime=0
   endTime=0
   
   #start the processes
   for p in jobs:
      p.start()
   time.sleep(3) #give time for messages to get to priority queue
   
   # stop when all processes are done running or 10 secs after winner wins
   numDone = 0
   
   while numDone < len(jobs) and endTime-startTime < 10:
      
      if startTime>0: endTime=time.time() #keeps track of time since winner
      
      # Get the next message that one of the processes has sent
      message = prioritized.get()
      print(message)
      
      #update number of comparisons
      Draw.delete(compstr)
      comps=message[0]
      compstr=Draw.string(str(comps),232,50)
      Draw.show()
      
      #see which sort the message is from, and move its car to the number 
      #of steps corresponding to its inversions removed
      if message[1]!="done":
         cars[message[1]].move(message,totalInversions)
    
      # if the process has announced that it is done, increment "done"s by 1
      else:
         numDone += 1  
         #the first one done is the winner
         if numDone==1:
            winner= message[2]
            startTime=time.time() #start 10 sec timer
         
            
   #display winner
   Draw.setFontSize(30)
   result=Draw.string("Winner: "+winner,210,540)
   Draw.show()
   time.sleep(2)
   #clear comparison and winner strings
   Draw.delete([compstr,result])


def main():
   Draw.setCanvasSize(750,605)
   
   #draw finish line
   Draw.setColor(Draw.BLACK)
   Draw.rect(580,75,70,455)
   for i in range(7):
      Draw.filledRect(580,75+70*i,35,35)
   for i in range(6):
      Draw.filledRect(615,110+70*i,35,35)
      
   #draw racetrack
   Draw.setColor(Draw.DARK_GRAY)
   Draw.filledRect(100,75,480,455)
   Draw.setColor(Draw.WHITE)
   for i in range(4):
      for j in range(0,470,20):
         Draw.filledRect(110+j,157+92*i,10,5)
   
   #create cars
   bubbleCar    = Car(100,83,Draw.RED,"B")
   selectionCar = Car(100,175,Draw.YELLOW,"S")
   insertionCar = Car(100,267,Draw.GREEN," I")
   mergeCar     = Car(100,359,Draw.BLUE,"M")
   quickCar     = Car(100,451,Draw.VIOLET,"Q")
   
   cars = {"bubble":bubbleCar, "selection":selectionCar, \
           "insertion":insertionCar,"merge":mergeCar, "quick":quickCar}
   
   #Race 1: random array of 10
   #create array
   a=[0]*10
   for i in range (len(a)):
      a[i]=random.randint(0,99)
   print("Random array 10:",a)
   #draw title
   title=drawTitle("Round 1: Random Array",a)
   #start race
   race(a, cars)
   time.sleep(3)
   
   #reset board
   Draw.delete(title)
   for k in cars:
      cars[k].reset() 
   
   #Race 2: random array of 100
   #create array
   b=[0]*100
   for i in range (len(b)):
      b[i]=random.randint(0,99)
   print("Random array 100:",b) 
   #draw title
   title=drawTitle("Round 2: Random Array",b)
   #start race
   race(b, cars)
   time.sleep(3)
  
   #reset board
   Draw.delete(title)
   for k in cars:
      cars[k].reset()  
      
   #Race 3: almost sorted 100
   #create sorted array
   c=[0]*100
   for i in range(len(c)-1): #leave last element unsorted
      c[i]=i
   #swap 10 random pairs
   for i in range(10):
      n = random.randint(0,len(c)-2)
      temp = c[n]   
      c[n]   = c[n+1] 
      c[n+1] = temp   
   print("Almost sorted:",c)
   #draw title
   title=drawTitle("Round 3: Almost Sorted Array",c) 
   #start race
   race(c,cars)
   
               
if __name__ == '__main__':
   main()