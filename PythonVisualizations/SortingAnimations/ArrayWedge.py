import Draw
import random
import math

Draw.setCanvasSize(500,500) 
WEDGES = 50 # number of wedges (and elements) in array

# Sort the list using bubblesort      
def bubbleSort(wedgeList):  
    numComps = 0 # number of comparisons run by bubblesort
    # outer loop from right to left
    for last in range(len(wedgeList)-1, 0, -1):   
          
        # inner loop goes left to right
        for inner in range(last):   
            
            numComps += 1 # increment comparisons by one 
            
            # If element to right of inner is smaller, then swap!
            if wedgeList[inner] > wedgeList[inner+1]:  
                temp              = wedgeList[inner]   
                wedgeList[inner]   = wedgeList[inner+1] 
                wedgeList[inner+1] = temp
                
                makeWedge(wedgeList, numComps) # draw wedge at new position

def makeWedge(wedgeList, numComps):
    Draw.clear()
    
    for i in range(len(wedgeList)): # for each element in list
        drawWedge(i, wedgeList[i][1]) # draw the wedge 
        Draw.setColor(Draw.BLACK)
        Draw.setFontSize(10)
        Draw.string("\u05D1\u05E1\u05F4\u05D3", 475, 0) # Hebrew BS"D,right corner  
        Draw.setFontSize(22)    
        Draw.string("Number of Comparisons: " + str(numComps), 0, 460)
    Draw.show()
        
def drawWedge(wedgeNum, color):
    radius = 200
    xC = 250 # x coord of center
    yC = 250 # y coord of center 
    
    
    # compute angle to point A on circle
    angleA = (2 * math.pi / WEDGES) * (-wedgeNum)
    print(angleA)
    
    #compute x and y coords of point A on circle
    xA = radius * math.cos(angleA) + xC
    yA = radius * math.sin(angleA) + yC
    print(xA, yA)
    
    # compute angle to point B on circle
    angleB = (2 * math.pi / WEDGES) * (-wedgeNum - 1)
    print(angleB)
    
    # compute x and y coords of point B on circle
    xB = radius * math.cos(angleB) + xC
    yB = radius * math.sin(angleB) + yC
    print(xB, yB)
    
    # Build a list of points
    pointList= [xA, yA, xB, yB, xC, yC]
    
    Draw.setColor(color)
    Draw.filledPolygon(pointList) # draw the wedge
 
                
def main():       
    wedgeList = [] # initialize list to hold tuples 
    numComps = 0 # number of comparisons

    # generate a rainbow pattern
    frequency = .3 # set variable frequency to .3
    for i in range(WEDGES): # iterate WEDGES (n) times
        red   = int(math.sin(frequency*i + 0) * 127 + 128)
        green = int(math.sin(frequency*i + 2) * 127 + 128)
        blue  = int(math.sin(frequency*i + 4) * 127 + 128)
        rainbowColor = Draw.color(red, green, blue) 
        Draw.setColor(rainbowColor)
        wedgeList.append((i, rainbowColor)) # add number and color tuple to list 
    
    random.shuffle(wedgeList) # shuffle list of tuples 
    print(wedgeList) # print the shuffled list
    
    makeWedge(wedgeList, numComps) # make the wedges
    
    bubbleSort(wedgeList) # sort the list with bubblesort
    print(bubbleSort(wedgeList))  # print the sorted list
    
    
main() 


