import Draw
import multiprocessing
import math
import time
import random

# My project displays a visualization of six arrays beings sorted by different sorting algorithms.
# The animation shows how each of the sorting algorithms approaches an array that contains items 
# that are shuffled, in reversed order, or are almost sorted.
# The number of comparisons of each sort is displayed. This signifies the number of times that two items
# in the array were compared in order to check if they were in the correct order.

# The arrows point to three positions in the array. The red arrow points to either the starting or ending position 
# of the current loop of sorting. The green arrow points to the position of the current item being sorted.
# The blue arrow points to the position of the item to which the current item is being compared.

# This file calls the multiprocessing module in order to concurrently animate the movement of items in the arrays.
# A copy of the Draw.py file is needed in order to run the animation.

# The code for cocktail, comb, and shell sorts was modified. Credit is given below to the original sources.
# I would like to thank Professor Alan Broder for providing me with the code for Draw.py, bubble, selection and insertion sorts,
# and for serving as my mentor on this project.
# -- Talia Leitner

# this function is called by the processes in animateDrawArray
def createArray(q,name,l,x,y,a):
	for i in range(len(l)):

		# frequency variable ensures that the rainbow has the correct number of shades of colors
		# relative to the number of rectangles that will be drawn
		f= 2*math.pi/len(l)

		# setting up next color
		red= int(math.sin(f*i + 0) *127 +128)
		green= int(math.sin(f*i + 2) *127 +128)
		blue= int(math.sin(f*i + 4) *127 +128)

		color= Draw.color(red,green,blue)

		# send message with placement and color of the rectangle
		q.put([name,x,y,i,color])
		time.sleep(.01)

		# each rectangle is 'a' units wide
		x+=a

	# send message when finished drawing all of the rectangles
	q.put([name,'done'])

# this function is called by animateDrawArray
def drawArray(l,x,y,i,color,a):
	# draw the next rectangle
	r= Draw.filledRect(x,y,a,200)
	# set color of the rectangle
	Draw.changeColor(r,color)
	Draw.show()

	# add object's graphical information to the list
	l[i]=r

# this funtion is called by the processes in animateArrayAction
def shuffle(q,name,l,seedVal):
	
	# seed value ensures that the arrays are all shuffled the same
	random.seed(seedVal)

	# Working backwards from the end
	for i in range(len(l)-1, 0, -1):
		# select any of the unshuffled positions
		# (even position i !!)
		j = random.randint(0, i)

		# Send message for swap
		q.put([name,i,j])
		time.sleep(.01)

		# Swap the elements at the two positions
		temp = l[i]
		l[i] = l[j]
		l[j] = temp

	# Send message when done shuffling
	q.put([name,'done'])

# this function is called by the processes in animateArrayAction
def reverse(q,name,l):
	# find the value of the last index
	last=len(l)-1
	# find the rounded midpoint
	mid=len(l)//2
	for i in range(mid):
		# send message to swap
		q.put([name,i,last-i])
		time.sleep(.01)
		# swap the i'th element with the element that is i positions away from the end
		temp=l[i]
		l[i]=l[last-i]
		l[last-i]=temp

	# Send message when done reversing
	q.put([name,'done'])

# this funtion is called by the processes in animateArrayAction
# reorders the array so that it's almost sorted
def reorder(q,name,l):
	# find the value of the last index
	last=len(l)-1    
	# find the rounded midpoint
	mid=len(l)//2
	for i in range(mid,last):
		# send message to swap
		q.put([name,i,i+1])
		time.sleep(.01)        
		# swap the original element with the element to its right
		temp=l[i]
		l[i]=l[i+1]
		l[i+1]=temp    

	# Send message when done reordering
	q.put([name,'done'])

# this function is called by the processes in animateSort
def bubbleSort(q,name,l):
	# Outer loop from right to left
	for last in range(len(l)-1, 0, -1):
		
		# Inner loop goes left to right
		for inner in range(last):
			# Send message to update the arrows
			q.put([name,'Arrow',last,inner,inner+1])
			time.sleep(.01)
			
		# If element to right of inner is smaller, then swap!
			if l[inner] > l[inner+1]:

				# Send message to swap
				q.put([name,inner,inner+1])
				time.sleep(.01)

				# Swap the elements at the two positions
				temp = l[inner]
				l[inner] = l[inner+1]
				l[inner+1] = temp

	# Send message when done sorting
	q.put([name,'done'])

# this function is called by the processes in animateSort
def selectionSort(q,name,l):

	for outer in range(len(l)-1): 
		min = outer              # Assume min is leftmost

		for inner in range(outer+1, len(l)): # Hunt to right

			# Send message to update the arrows
			q.put([name,'Arrow',outer,min,inner])
			time.sleep(.01)

			if l[inner] < l[min]:      # If we find new min,
				min = inner        # update the min index

		# Send message to swap
		q.put([name,outer,min])
		time.sleep(.01)

		# [min] is smallest among [outer]...[len(l)-1]
		temp = l[outer] # Swap leftmost and min
		l[outer] = l[min]
		l[min] = temp

	# Send message when done sorting
	q.put([name,'done'])

# this function is called by the processes in animateSort
def insertionSort(q,name,l):               # Sort by repeated inserts

	for outer in range(1, len(l)):         # Mark one element
		temp = l[outer]                    # Store marked elem in temp
		inner = outer                      # Inner loop starts at mark

		# only send messages to move the rectangles if temp needs to be moved to the left
		if temp < l[inner-1]:
			# Send message to move the rectangle off screen
			q.put([name,'saveTemp',outer])
			time.sleep(.01)

			while inner > 0 and temp < l[inner-1]:
				# Send message to update the arrows
				q.put([name,'Arrow',outer,inner,inner-1])
				time.sleep(.01)

				# Send message to make a copy of the the rectangle from the left
				# and put it in the current rectangle's place
				q.put([name,'copyOver',inner])
				time.sleep(.01)

				l[inner] = l[inner-1]           # If marked elem smaller, then
				inner -= 1                      # shift elem to right

				# exit while loop when l[inner-1] is not greater than temp
				# but it is still a compare so arrows should be moved!
				if inner > 0 and not temp < l[inner-1]:
					# Send message to update the arrows
					q.put([name,'Arrow',outer,inner,inner-1])
					time.sleep(.01)

			# Send message to return temp to the screen
			q.put([name,'restoreTemp',inner])
			time.sleep(.01)
			l[inner] = temp             		# Move marked elem to 'hole'
		else: 
			# send message for arrows to move to show that the position was checked 
			# even when temp isn't moved
			q.put([name,'Arrow',outer,inner,inner-1])
			time.sleep(.01)

	# Send message when done sorting
	q.put([name,'done'])

# this function is called by subclass Insertion's method processMessage
def saveTemp(l,outer):
	# returns the ID for the graphical object that is being sorted
	return l[outer]

# this function is called by subclass Insertion's method processMessage
def copyOver(l,inner,mainTemp,a):
	coords = Draw.coords(l[inner-1])  # get the coordinates of the object at inner-1
	color = Draw.getColor(l[inner-1]) # get the color of the object at inner-1

	# move the graphical object referred to by mainTemp one position to the left off-screen
	Draw.moveTo(mainTemp,coords[0],1000)

	# Delete the graphical object at inner, but only if what's there doesn't
	# happen to correspond to the off-screen graphical object referred to by mainTemp
	if l[inner] != mainTemp:
		Draw.delete(l[inner])

	# now create a new box at inner with the color of the box at inner-1
	Draw.setColor(color)
	l[inner] = Draw.filledRect(coords[0]+a, coords[1], a, 200)
	Draw.show()

# this function is called by subclass Insertion's method processMessage
def restoreTemp(l,mainTemp,inner):
	coords = Draw.coords(l[inner]) # get the coordinates of the object at inner

	# delete the graphical object that is currently at inner, if it's not mainTemp
	if l[inner] != mainTemp:
		Draw.delete(l[inner])

	# now move mainTemp back onto screen
	Draw.moveTo(mainTemp,coords[0],coords[1])
	Draw.show()

	# now remember that mainTemp is at that slot
	l[inner] = mainTemp

# Thank you to geeksforgeeks.org for the cocktail sort code.
# this function is called by the processes in animateSort
def cocktailSort(q,name,l):
	n = len(l)
	swapped = True
	start = 0
	end = n-1
	while swapped==True:

		# reset the swapped flag on entering the loop, 
		# because it might be true from a previous iteration 
		swapped = False

		# loop from left to right same as the bubble sort 
		for i in range (start, end):
			# Send message to update the arrows
			q.put([name,'Arrow',end,i,i+1])
			time.sleep(.01)

			if (l[i] > l[i+1]):
				# Send message to swap
				q.put([name,i,i+1])
				time.sleep(.01)

				temp = l[i]
				l[i] = l[i+1]
				l[i+1] = temp
				swapped=True

		# if nothing moved, then array is sorted 
		if swapped==False:
			# exit the while loop
			break

		# otherwise, reset the swapped flag so that it 
		# can be used in the next stage 
		swapped = False

		# move the end point back by one, because 
		# item at the end is in its rightful spot 
		end = end-1

		# from right to left, doing the same
		# comparison as in the previous stage
		for i in range(end-1, start-1,-1):
			# Send message to update the arrows
			q.put([name,'Arrow',start,i,i+1])
			time.sleep(.01)

			if (l[i] > l[i+1]):
				# Send messsage to swap
				q.put([name,i,i+1])
				time.sleep(.01)				

				temp = l[i]
				l[i] = l[i+1]
				l[i+1] = temp				
				swapped = True

		# increase the starting point, because
		# the last stage would have moved the next
		# smallest number to its rightful spot
		start = start+1

	# Send message when done sorting       
	q.put([name,'done'])

# Thank you to geeksforgeeks.org and wikipedia.org for the comb sort code.
# this function is called by the processes in animateSort
def combSort(q,name,l):
	n = len(l)

	# Initialize gap 
	gap = n

	# Initialize sorted as false to make sure that the loop runs
	sorted = False

	# Keep running while not sorted 
	while not sorted:
		# Find next gap
		gap = getNextGap(gap)
		
		# Done sorting when gap is equal to 1 and no items are swapped
		if gap==1:
			sorted=True

		# Compare all elements with current gap
		for i in range(n-gap):

			# Send message to update the arrows
			q.put([name,'Arrow',n-gap,i,i+gap])
			time.sleep(.01)

			if l[i] > l[i + gap]:

				# Send message to swap
				q.put([name,i,i+gap])
				time.sleep(.01)

				temp=l[i]
				l[i]=l[i+gap]
				l[i+gap]=temp
				sorted=False

	# Send message when done sorting        
	q.put([name,'done'])

# this function is called by combSort
# to find next gap from current
def getNextGap(gap): 
	# Shrink gap by Shrink factor
	shrink=1.3
	gap /= shrink
	if gap < 1: 
		return 1
	return int(gap)

# Thank you to geeksforgeeks.org for the shell sort code.
# this function is called by the processes in animateSort
def shellSort(q,name,l):

	# Start with a big gap, then reduce the gap 
	n = len(l)
	gap = int(n/2)

	# Do a gapped insertion sort for this gap size
	# The first gap elements l[0..gap-1] are already in gapped order
	# keep adding one more element until the entire array is gap sorted 
	while gap > 0:

		for i in range(gap,n):
			# add l[i] to the elements that have been gap sorted 
			# save l[i] in temp and make a hole at position i
			temp = l[i]
			# only send messages to move the rectangles if temp needs to be moved to the left
			if temp < l[i-gap]:

				# Send message to move the rectangle off screen
				q.put([name,'saveTemp',i])
				time.sleep(.01)

				# shift earlier gap-sorted elements up until the correct 
				# location for l[i] is found
				j = i
				while j >= gap and l[j-gap]>temp:
					# Send message to update the arrows
					q.put([name,'Arrow',i,j,j-gap])
					time.sleep(.01)

					# Send message to make a copy of the the rectangle from the left
					# and put it in the current rectangle's place
					q.put([name,'copyOverGap',j,gap])
					time.sleep(.01)

					l[j] = l[j-gap]
					j -= gap

					# exit while loop when l[j-gap] is not greater than temp
					# but it is still a compare so arrows should be moved!
					if j >= gap and not l[j-gap]>temp:
						# Send message to update the arrows
						q.put([name,'Arrow',i,j,j-gap])
						time.sleep(.01)

				# Send message to return temp to the screen
				q.put([name,'restoreTemp',j])
				time.sleep(.01)
				# put temp (the original a[i]) in its correct location
				l[j] = temp
			else: 
				# send message for arrows to move to show that the position was checked 
				# even if temp wasn't moved
				j=i
				q.put([name,'Arrow',i,j,j-gap])
				time.sleep(.01)

		# change gap size so that it's smaller
		gap = int(gap/2)
	# Send message when done sorting
	q.put([name,'done'])

# this function is called by subclass Shell's method processMessage
def copyOverGap(l,j,gap,mainTemp,a):
	coords = Draw.coords(l[j-gap])  # get the coordinates of the object at j-gap
	color = Draw.getColor(l[j-gap]) # get the color of the object at j-gap

	jcoords = Draw.coords(l[j])  # get the coordinates of the object at j

	# move the graphical object referred to by mainTemp one position to the left off-screen
	Draw.moveTo(mainTemp,coords[0],1000)

	# Delete the graphical object at inner, but only if what's there doesn't
	# happen to correspond to the off-screen graphical object referred to by mainTemp
	if l[j] != mainTemp:
		Draw.delete(l[j])

	# now create a new box at inner with the color of the box at inner-1
	Draw.setColor(color)
	l[j] = Draw.filledRect(jcoords[0], jcoords[1], a, 200)
	Draw.show()

# this function animates swapping the objects in the 'original' and 'destination' cells
def animateSwap(l,originalCell,destinationCell):

	# get the coordinates of the two rectangles
	coords = Draw.coords(l[originalCell])
	coords2 = Draw.coords(l[destinationCell])

	# swap the rectangles
	Draw.moveTo(l[originalCell],coords2[0],coords2[1])
	Draw.moveTo(l[destinationCell],coords[0],coords[1])
	Draw.show()

	# swap the elements at the two positions
	temp = l[originalCell]
	l[originalCell] = l[destinationCell]
	l[destinationCell] = temp  

# this function is called by class Sorter's init method
def drawArrow(color):
	# set color of the arrow
	Draw.setColor(color)
	# draw triangle top of arrow off-screen
	poly=[1000,1005, 1005,1000, 1010,1005, 1005,1005]
	p=Draw.filledPolygon(poly)
	# draw rectangle bottom of arrow off-screen
	r=Draw.filledRect(1002.5,1005, 5,20)
	# return tuple containing both pieces of the arrow
	return (p,r)

# this function is called by class Sorter's method processMessage
def moveArrow(l,arrow1,arrow2,arrow3,pos1,pos2,pos3):

	# get the coordinates of the three items being compared
	coordsR= Draw.bbox(l[pos1])
	coordsG= Draw.bbox(l[pos2])
	coordsB= Draw.bbox(l[pos3])

	# move the red arrow (indicates the starting position of the item being swapped)
	Draw.moveTo(arrow1,coordsR[0]+5,coordsR[1]+205)

	# move the green arrow (indicates the current position of the item being swapped)
	# added +5 for the x because the arrow is 10 units wide and the rectangles are 20 units wide
	Draw.moveTo(arrow2,coordsG[0]+5,coordsG[1]+205)

	# blue arrow (indicates the position of the item being compared)
	Draw.moveTo(arrow3,coordsB[0]+5,coordsB[1]+205)

	Draw.show()

# # this function is called by class Sorter's init and processMessage methods
def showComparisons(numInsComparisons,x,y):
	Draw.setColor(Draw.BLUE)
	# returns the ID for the string with the updated number of comparisons
	return Draw.string(str(numInsComparisons),x,y)

# superclass for sorting
class Sorter(object):
	def __init__(self,x,y):
		# set number of compares for each sort equal to 0        
		self.__numComparisons=0
		# draw text for the number of comparisons
		self.__stringID=showComparisons(self.__numComparisons,x,y)
		# last's arrow
		self.__arrow1=drawArrow(Draw.RED)
		# inner's arrow
		self.__arrow2=drawArrow(Draw.GREEN)
		# (inner+1)'s arrow
		self.__arrow3=drawArrow(Draw.BLUE)
		Draw.show()

	def sort(self, jobs, Sort, q, name, numbers):
		# initialize the sorting process
		p = multiprocessing.Process(target=Sort, args=(q,name,numbers))
		jobs.append(p)

	def processMessage(self, l, message, x, y):
		if message[1] == 'Arrow':
			# update the number of comparisons
			Draw.delete(self.__stringID)
			self.__numComparisons +=1
			self.__stringID = showComparisons(self.__numComparisons,x,y)
			Draw.show()
			# update the arrows -- message format is [name,'Arrow',pos1, pos2, pos3]
			moveArrow(l,self.__arrow1,self.__arrow2,self.__arrow3,message[2],message[3],message[4])

		elif message[1] == 'done':
			# delete the arrows when done sorting -- message format is [name,'done']
			Draw.delete(self.__arrow1)
			Draw.delete(self.__arrow2)
			Draw.delete(self.__arrow3)  
			Draw.show()

		else:
			# swap the rectangles -- message format is [name, originalCell, destinationCell]
			animateSwap(l, message[1], message[2])

	def cleanup(self):
		# delete text for the number of comparisons
		Draw.delete(self.__stringID)
		Draw.show()

# subclass for insertion sort
class Insertion(Sorter):
	def __init__(self,y):
		super().__init__(515,y)

	def processMessage(self, l, message, x, y):
		# insertion sort sends different messages for sorting than do the others
		if message[1]== 'saveTemp':
			# save a reference to the graphical object that was stored in temp's position
			self.__mainTemp=saveTemp(l,message[2])
		elif message[1]== 'copyOver':
			# copy over the rectangle from the left
			copyOver(l,message[2],self.__mainTemp,20)
		elif message[1]== 'restoreTemp':
			# move the graphical object that was in temp's position to its new position
			restoreTemp(l,self.__mainTemp,message[2])
		else:
			super().processMessage(l,message,x,y)

# subclass for shell sort
class Shell(Sorter):
	def __init__(self,y):
		super().__init__(1065,y)

	def processMessage(self, l, message, x, y):
		# shell sort sends different messages for sorting than do the others
		if message[1]== 'saveTemp':
			# save a reference to the graphical object that was stored in temp's position
			self.__mainTemp=saveTemp(l,message[2])
		elif message[1]== 'copyOverGap':
			# copy over the rectangle from the left
			copyOverGap(l,message[2],message[3],self.__mainTemp,20)
		elif message[1]== 'restoreTemp':
			# move the graphical object that was in temp's position to its new position
			restoreTemp(l,self.__mainTemp,message[2])
		else:
			super().processMessage(l,message,x,y)

# this function uses multi processing to animate sorting all of the arrays
def animateSort(q,bubbleList,selectionList,insertionList,cocktailList,combList,shellList,numbers):
	# list of processes
	jobs=[]

	# initialize the classes
	bub = Sorter(515,30)
	sel = Sorter(515,280)
	ins = Insertion(530)
	coc = Sorter(1065,30)
	comb= Sorter(1065,280)
	shell= Shell(530)

	# initialize the processes
	bub.sort(jobs, bubbleSort, q,'Bub',numbers)
	sel.sort(jobs, selectionSort, q,'Sel',numbers)
	ins.sort(jobs, insertionSort, q,'Ins',numbers)
	coc.sort(jobs, cocktailSort, q,'Coc',numbers)
	comb.sort(jobs, combSort, q,'Comb',numbers)
	shell.sort(jobs, shellSort, q,'Shell',numbers)

	# start the processes
	for p in jobs:
		p.start()

	numDone = 0
	while numDone < len(jobs):
		# Get the next message that one of the processes has sent
		message= q.get()

		if message[0] == 'Bub':
			bub.processMessage(bubbleList,message,515,30)

		elif message[0] == 'Sel':
			sel.processMessage(selectionList,message,515,280)

		elif message[0] == 'Ins':
			ins.processMessage(insertionList,message,515,530)

		elif message[0] == 'Coc':
			coc.processMessage(cocktailList,message,1065,30)

		elif message[0] == 'Comb':
			comb.processMessage(combList,message,1065,280)	

		elif message[0] == 'Shell':
			shell.processMessage(shellList,message,1065,530)

		# check if the sort is done
		if message[1] == 'done':
			numDone += 1 

	# pause animation for a few seconds
	time.sleep(3)

	# delete text for number of comparisons
	bub.cleanup()
	sel.cleanup()
	ins.cleanup()
	coc.cleanup()
	comb.cleanup()
	shell.cleanup()

# this function takes shuffle, reverse or reorder as input for the parameter 'action'
# and uses multi processing to animate all of the arrays
def animateArrayAction(q,action,bubbleList,selectionList,insertionList,cocktailList,combList,shellList):
	# list of processes
	jobs=[]

	# shuffle takes one parameter more than reverse and reorder
	if action==shuffle:
		# take action on top-left array
		p = multiprocessing.Process(target=action, args=(q,'bubbleList',bubbleList,250))
		jobs.append(p)
		# take action on middle-left array
		p = multiprocessing.Process(target=action, args=(q,'selectionList',selectionList,250))
		jobs.append(p)
		# take action on bottom-left array
		p = multiprocessing.Process(target=action, args=(q,'insertionList',insertionList,250))
		jobs.append(p)
		#take action on top-right array
		p = multiprocessing.Process(target=action, args=(q,'cocktailList',cocktailList,250))
		jobs.append(p)
		#take action on middle-right array
		p = multiprocessing.Process(target=action, args=(q,'combList',combList,250))
		jobs.append(p)	
		#take action on bottom-right array
		p = multiprocessing.Process(target=action, args=(q,'shellList',shellList,250))
		jobs.append(p)

	else:
		# take action on top-left array
		p = multiprocessing.Process(target=action, args=(q,'bubbleList',bubbleList))
		jobs.append(p)
		# take action on middle-left array
		p = multiprocessing.Process(target=action, args=(q,'selectionList',selectionList))
		jobs.append(p)
		# take action on bottom-left array
		p = multiprocessing.Process(target=action, args=(q,'insertionList',insertionList))
		jobs.append(p)
		# take action on top-right array
		p = multiprocessing.Process(target=action, args=(q,'cocktailList',cocktailList))
		jobs.append(p)
		#take action on middle-right array
		p = multiprocessing.Process(target=action, args=(q,'combList',combList))
		jobs.append(p)
		# take action on bottom-right array
		p = multiprocessing.Process(target=action, args=(q,'shellList',shellList))
		jobs.append(p)

	# start the processes
	for p in jobs:
		p.start()

	numDone = 0
	while numDone < len(jobs):
		# Get the next message that one of the processes has sent
		message = q.get()

		# keep track of how many processes have completed
		if message[1] == 'done': # Message format is [name, 'done']
			numDone += 1

		# otherwise, move the appropriate object on the canvas
		else:                    # Message format is [name, originalCell, destinationCell]
			if message[0] == 'bubbleList':
				animateSwap(bubbleList, message[1], message[2])

			elif message[0] == 'selectionList':
				animateSwap(selectionList, message[1], message[2])

			elif message[0] == 'insertionList':
				animateSwap(insertionList, message[1], message[2])

			elif message[0] == 'cocktailList':
				animateSwap(cocktailList, message[1], message[2])

			elif message[0] == 'combList':
				animateSwap(combList, message[1], message[2])	    

			elif message[0] == 'shellList':
				animateSwap(shellList, message[1], message[2])	    

# this function uses multi processing to animate drawing all of the arrays
def animateDrawArray(q,bubbleList,selectionList,insertionList,cocktailList,combList,shellList):
	# list of processes
	jobs=[]

	# create top-left array
	p=multiprocessing.Process(target=createArray, args=(q,'bubbleList',bubbleList,25,50,20))
	jobs.append(p)
	# create middle-left array
	p=multiprocessing.Process(target=createArray, args=(q,'selectionList',selectionList,25,300,20))
	jobs.append(p)
	# create bottom-left array
	p=multiprocessing.Process(target=createArray, args=(q,'insertionList',insertionList,25,550,20))
	jobs.append(p)
	# create top-right array
	p=multiprocessing.Process(target=createArray, args=(q,'cocktailList',cocktailList,575,50,20))
	jobs.append(p)
	# create middle-right array
	p=multiprocessing.Process(target=createArray, args=(q,'combList',combList,575,300,20))
	jobs.append(p)    
	# create bottom-right array
	p=multiprocessing.Process(target=createArray, args=(q,'shellList',shellList,575,550,20))
	jobs.append(p)

	# start the processes
	for p in jobs:
		p.start()

	numDone = 0
	while numDone<len(jobs):
		# Get the next message that one of the processes has sent
		message = q.get()

		# keep track of how many processes have completed
		if message[1] == 'done': # Message format is [name, 'done']
			numDone += 1

		else: # otherwise draw the appropriate rectangle -- Message format is [name,x,y,i,color]
			if message[0]=='bubbleList':
				drawArray(bubbleList,message[1],message[2],message[3],message[4],20)
			elif message[0]=='selectionList':
				drawArray(selectionList,message[1],message[2],message[3],message[4],20)
			elif message[0]=='insertionList':
				drawArray(insertionList,message[1],message[2],message[3],message[4],20)  
			elif message[0]=='cocktailList':
				drawArray(cocktailList,message[1],message[2],message[3],message[4],20)
			elif message[0]=='combList':
				drawArray(combList,message[1],message[2],message[3],message[4],20)	    
			elif message[0]=='shellList':
				drawArray(shellList,message[1],message[2],message[3],message[4],20)   	    

# resets integers in list numbers so that they're ordered
def reset(numbers):
	for i in range(len(numbers)):
		numbers[i]=i

# this function is called by main
# shuffles integers in list numbers
def shuffleNums(numbers,seedVal):
	# make sure the integers are in order
	reset(numbers)
	# seed value ensures that the integers are shuffled the same as the objects in the arrays
	random.seed(seedVal)
	# Working backwards from the end
	for i in range(len(numbers)-1, 0, -1):
		# select any of the unshuffled positions
		# (even position i !!)
		j = random.randint(0, i)
		# Swap the elements at the two positions
		temp = numbers[i]
		numbers[i] = numbers[j]
		numbers[j] = temp 

# this function is called by main
# reverses integers in list numbers
def reverseNums(numbers):
	# make sure the integers are in order
	reset(numbers)
	last=len(numbers)-1
	mid=len(numbers)//2
	for i in range(mid):
		# swap the item in position 'i' with the item that is 'i' positions away from the end
		temp=numbers[i]
		numbers[i]=numbers[last-i]
		numbers[last-i]=temp

# this function is called by main
# reorders/almost sorts integers in list numbers
def reorderNums(numbers):
	# make sure the integers are in order
	reset(numbers)
	last=len(numbers)-1
	mid=len(numbers)//2
	for i in range(mid,last):    
		# swap the original element with the element to its right
		temp=numbers[i]
		numbers[i]=numbers[i+1]
		numbers[i+1]=temp

def main():
	Draw.setCanvasSize(1100,800)
	q= multiprocessing.Queue()

	# DRAWING ARRAYS
	# variable for length of the arrays
	length=25
	# create lists for each sort's array to hold graphical information
	bubbleList= [None]*length
	selectionList= [None]*length
	insertionList= [None]*length
	cocktailList= [None]*length
	combList= [None]*length
	shellList= [None]*length
	# create list numbers to hold corresponding integers
	numbers= [None]*length

	# animate drawing the arrays
	animateDrawArray(q,bubbleList,selectionList,insertionList,cocktailList,combList,shellList)

	# print original lists for reference
	print("Original bubbleList: ", bubbleList)
	print("Original selectionList: ", selectionList)
	print("Original insertionList: ", insertionList)
	print("Original cocktailList: ", cocktailList)
	print("Original combList: ", combList)
	print("Original shellList: ", shellList)

	# draw text for sort names
	Draw.setFontBold(True)
	Draw.setFontSize(16)    
	Draw.setColor(Draw.BLUE)
	bubSort= Draw.string("Bubble Sort",15,30)
	selSort= Draw.string("Selection Sort",15,280)
	insSort= Draw.string("Insertion Sort",15,530)
	cocSort= Draw.string("Cocktail Sort",565,30)
	combSort= Draw.string("Comb Sort",565,280)
	shellSort= Draw.string("Shell Sort",565,530)
	# draw text for comparisons
	bubComp= Draw.string("Comparisons: ",400,30)
	selComp= Draw.string("Comparisons: ",400,280)
	insComp= Draw.string("Comparisons: ",400,530)
	cocComp= Draw.string("Comparisons: ",950,30)
	combComp= Draw.string("Comparisons: ",950,280)
	shellComp= Draw.string("Comparisons: ",950,530)
	Draw.show()
	
	# add integers to list numbers
	reset(numbers)
	# print original list numbers for reference
	print("Original numbers: ", numbers)	

	# SHUFFLE ARRAYS
	# draw text for shuffle
	Draw.setFontSize(24)
	s= Draw.string("SHUFFLED",485,5)
	Draw.changeColor(s,Draw.BLUE)
	Draw.show()
	# return font size back to 16
	Draw.setFontSize(16)

	# animate shuffling the arrays
	animateArrayAction(q,shuffle,bubbleList,selectionList,insertionList,cocktailList,combList,shellList)
	# pause for a moment after shuffling
	time.sleep(1)

	# shuffle integers in list numbers
	shuffleNums(numbers,250)

	# sort for first time
	animateSort(q,bubbleList,selectionList,insertionList,cocktailList,combList,shellList,numbers)

	# REVERSE ARRAYS
	# draw text for reverse
	Draw.setFontSize(24)
	Draw.delete(s)  
	s=Draw.string("REVERSED",485,5)
	Draw.changeColor(s,Draw.BLUE)
	Draw.show()
	# return font size back to 16
	Draw.setFontSize(16)

	# animate reversing the arrays
	animateArrayAction(q,reverse,bubbleList,selectionList,insertionList,cocktailList,combList,shellList)
	# pause for a moment after reversing
	time.sleep(1)

	# reverse integers in list numbers
	reverseNums(numbers)

	# sort for second time   
	animateSort(q,bubbleList,selectionList,insertionList,cocktailList,combList,shellList,numbers)

	# ALMOST SORT ARRAYS
	# draw text for almost sorted   
	Draw.setFontSize(24)
	Draw.delete(s)
	s=Draw.string("ALMOST SORTED",440,5)
	Draw.changeColor(s,Draw.BLUE)   
	Draw.show()
	# return font size back to 16
	Draw.setFontSize(16)

	# animate reordering the arrays so that they're almost sorted
	animateArrayAction(q,reorder,bubbleList,selectionList,insertionList,cocktailList,combList,shellList)
	time.sleep(1)

	# reorder/almost sort integers in list numbers
	reorderNums(numbers)

	# sort for third time
	animateSort(q,bubbleList,selectionList,insertionList,cocktailList,combList,shellList,numbers)

	# delete almost sorted text
	Draw.delete(s)
	Draw.show()

if __name__ == '__main__':
	main()
