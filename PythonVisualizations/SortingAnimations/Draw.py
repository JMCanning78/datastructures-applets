"""
Draw.py

The Draw module defines functions that allow the user to create a
drawing.  A drawing appears on the canvas.  The canvas appears
in the window.  

This module has been recoded by AJB to remove references to 
pygame, and solely uses tkinter.

Original version is from Sedgwick, Princeton University
"""

import time
import os
import sys
import string
import tkinter

from tkinter import font


#-----------------------------------------------------------------------

# create a custom color
def color(r, g, b):
    return '#%02x%02x%02x' % (r, g, b)

# Handy pre-defined colors

WHITE      = '#ffffff'
BLACK      = '#000000'
GRAY       = '#888888'
RED        = '#ff0000'
GREEN      = '#00ff00'
BLUE       = '#0000ff'
CYAN       = '#00ffff'
MAGENTA    = '#ff00ff'
YELLOW     = '#ffff00'
DARK_RED   = '#800000'
DARK_GREEN = '#008000'
DARK_BLUE  = '#000080'
DARK_GRAY  = '#404040'
LIGHT_GRAY = '#C0C0C0'
ORANGE     = '#ffc800'
VIOLET     = '#ee82ee'
PINK       = '#ffafaf'


# Default Sizes and Values


_DEFAULT_CANVAS_SIZE = 512

_DEFAULT_PEN_COLOR = BLACK

_DEFAULT_FONT_FAMILY = 'Helvetica'
_DEFAULT_FONT_SIZE = 12
_DEFAULT_FONT_WEIGHT = 'normal'
_DEFAULT_FONT_SLANT = 'roman'

_validFontFamilies = None
_fontFamily = _DEFAULT_FONT_FAMILY
_fontSize   = _DEFAULT_FONT_SIZE
_fontWeight = _DEFAULT_FONT_WEIGHT
_fontSlant  = _DEFAULT_FONT_SLANT

_canvasWidth = float(_DEFAULT_CANVAS_SIZE)
_canvasHeight = float(_DEFAULT_CANVAS_SIZE)
_penColor = _DEFAULT_PEN_COLOR



_canvas = None
_tkWindow = None

_images = []
_imageRefs = []

# Has the window been created?
_windowCreated = False

# Do we want to update the display only upon calling show() ?
_showMode = False

# the queue (really a list) of keys that have been typed, awaiting processing
_keysTyped = []

# the queue of mouse clicks. Each element in the queue consists of
# a tuple containing x, y, "left" or "right"
_clicks = []

# The position of the mouse as of the most recent mouse click
_mousePos = None

# True if the mouse has moved since the last time we checked
_mouseMoved = False

 

def _on_closing():
    global _tkWindow
    _tkWindow.destroy()


def setCanvasSize(w=_DEFAULT_CANVAS_SIZE, h=_DEFAULT_CANVAS_SIZE):
    """
    Set the size of the canvas to w pixels wide and h pixels high.
    Calling this function is optional. If you call it, you must do
    so before calling any drawing function.
    """
    global _background
    # global _surface
    global _tkWindow
    global _canvas
    global _canvasWidth
    global _canvasHeight
    global _windowCreated
    global _validFontFamilies

    if _windowCreated:
        raise Exception('The Draw window already was created')

    if (w < 1) or (h < 1):
        raise Exception('width and height must be positive')

    _canvasWidth = w
    _canvasHeight = h
    
    _tkWindow = tkinter.Tk()
    _tkWindow.title("Draw")
    _tkWindow.protocol("WM_DELETE_WINDOW", _on_closing)
    _canvas = tkinter.Canvas(_tkWindow, width=w, height=h, 
                             bd=0, highlightthickness=0)
    _canvas.pack()
    _canvas.config(bg=WHITE)
    #print("Doing the bindings")
    _canvas.bind("<Button-1>", _leftButtonCallback)
    _canvas.bind("<Button-2>", _rightButtonCallback)
    _canvas.bind("<Button-3>", _rightButtonCallback)
    _tkWindow.bind("<Motion>",   _motionCallback)
    #print("Done with the bindings")
    _canvas.bind_all("<Key>",  _keyCallback)
    
    _validFontFamilies = list(tkinter.font.families())
    
    _windowCreated = True

    _tkWindow.update()

def setBackground(c=WHITE):
    global _canvas
    _makeSureWindowCreated()
    _canvas.config(bg=c)

def setColor(c=_DEFAULT_PEN_COLOR):
    """
    Set the pen color to c
    c defaults to BLACK.
    """
    global _penColor
    _makeSureWindowCreated()    
    _penColor = c

def setFontFamily(f=_DEFAULT_FONT_FAMILY):
    """
    Set the font family to f (e.g. 'Helvetica' or 'Courier' or 'Times').
    """
    global _fontFamily
    global _validFontFamilies
    
    _makeSureWindowCreated()    
    _fontFamily = f

    if not (f in _validFontFamilies):
        errStr = "Invalid font " + f + ", not one of " + str(_validFontFamilies)
        raise Exception(errStr)
     
def availableFonts():
    _makeSureWindowCreated()  
    return _validFontFamilies
    

def setFontSize(s=_DEFAULT_FONT_SIZE):
    """
    Set the font size to s (e.g. 12 or 16).
    """
    global _fontSize
    _fontSize = s
    
def setFontBold(b = None):
    """
    Set the bolding as desired. The default weight is no bolding.
    """
    global _fontWeight
    if not b:
        _fontWeight = _DEFAULT_FONT_WEIGHT
        
    else:
        _fontWeight = 'bold'
        
def setFontItalic(i = None):
    """
    Set the italic as desired. The default italic is none.
    """
    global _fontSlant
    if not i:
        _fontSlant = _DEFAULT_FONT_SLANT
        
    else:
        _fontSlant = 'italic'
        
        

#-----------------------------------------------------------------------

def _makeSureWindowCreated():
    global _windowCreated
    if not _windowCreated:
        setCanvasSize()
        _windowCreated = True

#-----------------------------------------------------------------------

# Functions to draw shapes, text, and images

def line(x0, y0, x1, y1):
    """
    Draw a line from (x0, y0) to (x1, y1).
    """

    global _canvas
    global _penColor

    _makeSureWindowCreated()

    id = _canvas.create_line(x0, y0, x1, y1, capstyle=tkinter.ROUND, fill = _penColor)
    
    _doUpdate()
    
    return id
	                       

def oval(x, y, width, height):
    """
    Outline largest oval that fits in a box of size width x height
    with top left at (x,y)
    """
    
    global _canvas
    global _penColor
    
    _makeSureWindowCreated()
    
    # it appears that the -1 is needed for x1 and y1 when drawing an outline, 
    # similar to when doing an outline of a rectangle. This was confirmed 
    # by magnified visual inspection of a rectangle and oval.
    id = _canvas.create_oval(x, y, x+width-1, y+height-1, outline = _penColor)
    
    _doUpdate()
    
    return id

def filledOval(x, y, width, height):
    """
    Fill largest oval that fits in a box of size width x height
    with top left at (x,y)
    """
    global _canvas
    global _penColor
    
    _makeSureWindowCreated()
    
    id = _canvas.create_oval(x, y, x+width, y+height, fill = _penColor, width=0)
    
    _doUpdate()
    
    return id

def rect(x, y, width, height):
    """
    Outline a rectangle of width and height whose upper left point is (x, y).
    """
    global _canvas
    global _penColor
    
    _makeSureWindowCreated()
    
    # Note that the -1 is needed, since the right and bottom 
    # borders actually are 1 pixel outside the bounding
    # box of the rectangle
    id = _canvas.create_rectangle(x, y, x+width-1, y+height-1, 
                                  outline = _penColor, width=1)
    
    _doUpdate()
    
    return id

def filledRect(x, y, width, height):
    """
    Fill a rectangle of width and height whose upper left point is (x, y).
    """
    global _canvas
    global _penColor
    
    _makeSureWindowCreated()
    
    id = _canvas.create_rectangle(x, y, x+width, y+height, 
                                  fill = _penColor, width=0)
    
    _doUpdate()

    return id

def polygon(pts):
    """
    Outline a polygon with x,y coordinates appearing in pts.
    """
    global _canvas
    global _penColor
    
    _makeSureWindowCreated()
    
    id = _canvas.create_polygon(pts, fill='', outline = _penColor, width = 1)
    
    _doUpdate()
    
    return id


def filledPolygon(pts):
    """
    Fill a polygon with x,y coordinates appearing in pts.
    """
    global _canvas
    global _penColor
    
    _makeSureWindowCreated()
    
    id = _canvas.create_polygon(pts, fill = _penColor, outline = _penColor)
    
    _doUpdate()
    
    return id

def string(s, x, y):
    """
    Draw string s at (x, y).
    """
    global _tkWindow
    global _canvas
    global _penColor
    global _fontFamily
    global _fontSize
    global _fontSlant
    global _fontWeight
 
    _makeSureWindowCreated()
    
    style = _fontSlant + " " + _fontWeight
    
    id = _canvas.create_text(x, y, text = s, 
                            fill = _penColor, 
                            anchor=tkinter.NW,
                            font=(_fontFamily, str(_fontSize), style)
                            )
    _doUpdate()
    
    return id 

# Make sure that id is iterable. if id happens to be a single
# canvas object then just put it inside a tuple, which will be iterable
def _makeIterable(a):
    t = type(a)
    if not(t is list or t is tuple): a = (a,)
    return a

def bbox(id):
    """
    Return a tuple (x1,y1, x2,y2) of the corners of the bounding box of the object
        
    id can either be a single canvas object, or a list, tuple, or set of
    canvas objects.
    """    
    global _canvas
    
    id = _makeIterable(id)      # Make sure that the id is iterable
    
    # loop through all the items and find the cumulative bounding box
    ans = [float('inf'), float('inf'), -float('inf'), -float('inf')]
    for item in id:
        b = _canvas.bbox(item)
        ans[0] = min(ans[0], b[0])
        ans[1] = min(ans[1], b[1])
        ans[2] = max(ans[2], b[2])
        ans[3] = max(ans[3], b[3])
    
    return tuple(ans)

def moveBy(id, dx, dy):
    """
    Move the canvas object by adding the amount dx to its x coordinate, 
    and by adding dy to its y coordinates
    
    id can either be a single canvas object, or a list, tuple, or set of
    canvas objects.
    """    
    global _canvas
    
    # move the item(s) by dx,dy
    id = _makeIterable(id)
    for item in id:
        _canvas.move(item, dx, dy)  

def moveTo(id, x, y):
    """
    Move the canvas object to coordinates x, y
    
    id can either be a single canvas object, or a list, tuple, or set of
    canvas objects - i.e. an compound object.
    
    If the object is a compound object, then all the constituent objects will 
    be moved so that the upper left hand corner 
    of the bounding box of all the objects is moved to x,y
    """     
    global _canvas
    
    id = _makeIterable(id)      # Make sure that the id is iterable
    
    # loop through all the items and find the upper left corner of the bounding box
    c = [float('inf'), float('inf')]
    for item in id:
        b = _canvas.coords(item)
        c[0] = min(c[0], b[0])
        c[1] = min(c[1], b[1])
  
    # compute the dx,dy needed to get that corner to x,y
    dx = x - c[0]
    dy = y - c[1]
    
    # Move the item(s) by dx,dy
    for item in id:
        _canvas.move(item, dx, dy) 
      

def getColor(id):
    """
    Returns the color of the canvas object. 
    
    id MUST be a single canvas object, not a list, tuple or set
    """
    global _canvas
    
    return _canvas.itemcget(id, 'fill')
    
def changeColor(id, color):
    """
    Change the canvas object's color
        
    id can either be a single canvas object, or a list, tuple, or set of
    canvas objects.
    """     
    global _canvas
    
    # Make sure that the id is iterable
    id = _makeIterable(id)  
    
    # Change the color of the object(s)
    for item in id:
        _canvas.itemconfigure(item, fill = color)
    
def coords(id):
    """
    Return a tuple (x1,y1, x2,y2, ... xi, yi) containing the coordinates of the
    canvas objects. For a string, it just returns the x,y coordinates of the 
    upper left hand corner of the string as rendered on the string.
    
    id can either be a single canvas object, or a list, tuple, or set of
    canvas objects.
    """

    global _canvas
    
    # Make sure that the id is iterable
    id = _makeIterable(id)   
    
    # build up the tuple containing all the coords in the object(s)
    ans = tuple()
    for item in id:
        ans += tuple(_canvas.coords(item)) 
        
    return ans

def delete(id):
    """
    Delete from the canvas the specified canvas objects. The objects
    will vanish upon the next Draw.show()
    id can either be a single canvas object, or a list, tuple, or set of
    canvas objects.
    """
    
    global _canvas
    
    # Make sure that the id is iterable
    id = _makeIterable(id)
    
    # delete all the items in the iterable
    for item in id:
        _canvas.delete(item) 

def bringToFront(id):
    """
    Raise the specified objcet(s) to be in front of everything else on screen.
    id can either be a single canvas object, or a list, tuple, or set of
    canvas objects.
    """
    global _canvas
    
    # Make sure that the id is iterable
    id = _makeIterable(id)
    
    # raise all the items in the iterable
    for item in id:
        _canvas.tag_raise(item, 'all') 




# return a PhotoImage object associated with the file "name". 
# Caches the last 50 images loaded.
# If we need to implement loading a photoImage of a tile from an
# image file, see http://tkinter.unpythonic.net/wiki/PhotoImage.
# To support this, we would specify file names like this, which would
# uniquely identify the exact tile associated with that name:
#    "foo.gif|x0|y0|wide|high"
# The code at that URL says to do:
#
#def subimage(src, l, t, r, b):
#    dst = PhotoImage()
#    dst.tk.call(dst, 'copy', src, '-from', l, t, r, b, '-to', 0, 0)
#    return dst
# alternately, could write a helper function that you give it an image
# file name, and it returns to you a 2D list of colors, using the material
# at http://mgltools.scripps.edu/api/DejaVu/Tkinter.PhotoImage-class.html

def _getPhotoImage(name):
    global _images
    for p in _images:
        if p[0] == name:
            return p[1]
       
    if len(_images) > 50:
        _images.pop(0)
    
    ans = tkinter.PhotoImage(file = name)
    
    _images.append([name, ans])
    return ans

# keeps up to 50 photo images alive at any given time. 
# We need to do this since when the image is rendered later,
# the local variable will have gone out of scope.
# See https://tkinter.unpythonic.net/wiki/PhotoImage - 
#  "Disappearing Photoimage"
def _getPhotoImageReference(w, h):
    global _imageRefs
    
    # We're only going to cache 50 of these at any given time
    if len(_imageRefs) >= 50: _imageRefs.pop(0)
    
    # Create the photoimage and store a reference to keep it from being gc'ed
    ans = tkinter.PhotoImage(width=w, height=h)
    _imageRefs.append(ans)
    
    return ans
    

# The mag parameter only applies to images specified via a 2d array
def picture(pic, x=0, y=0, mag=1):
    """
    Draw pic placing the upper left corner at (x,y).  pic is the 
    name of a .gif, .pgm, or .ppm format image. 
    """
    global _canvas
    _makeSureWindowCreated()
    
    # picture was specified by a file name
    if type(pic) is str:
        im = _getPhotoImage(pic)
        
    # picture is, presumably, a 2D grid of colors
    else:
        numRows = len(pic)
        numCols = len(pic[0])
        im = _getPhotoImageReference(numCols*mag, numRows*mag)
        line = ""
        if mag == 1:
            for row in range(numRows):
                line += '{' + ' '.join(pic[row]) + '} '
        else:
            for row in range(numRows):
                magRow = [pic[row][j//mag] for j in range(numCols * mag)]
                theLine = '{' + ' '.join(magRow) + '} '
                for dup in range(mag):
                    line += theLine
                    
        im.put(line)
        
    id = _canvas.create_image((x, y), image = im, anchor = tkinter.NW, state='normal')
    
    _doUpdate()
    
    return id

def clear():
    """
    Clear the canvas to the background color
    """
    global _canvas
    _makeSureWindowCreated()
    _canvas.delete(tkinter.ALL)
    
    _doUpdate()


#-----------------------------------------------------------------------

def _doUpdate(inShow = False):
    global _showMode
    
    # if we're in showMode, then only update if inShow is True
    # otherwise, update always
    
    if (not _showMode) or inShow:
        _tkWindow.update()
        #_tkWindow.update_idletasks()        

def show(msec=0):
    """
    Force an update of the display, and then wait the specified number
    of milliseconds.
    """
    global _tkWindow
    global _canvas
    global _showMode
    
    _makeSureWindowCreated()
    
    _showMode = True
    _doUpdate(True)

    if msec > 0: _canvas.after(int(msec))

def _leftButtonCallback(event):
    """
    Check if a left mouse button event has occurred
    """
    global _clicks

    _makeSureWindowCreated()
    
    _clicks = [(event.x, event.y, "left")] + _clicks
    
    
def _rightButtonCallback(event):
    """
    Check if a right mouse button event has occurred
    """
    global _clicks
    
    _makeSureWindowCreated()
    
    _clicks = [(event.x, event.y, "right")] + _clicks
    
def _motionCallback(event):
    """
    Check if a mouse motion event has occurred
    EXPERIMENTAL!
    """
    global _mouseMoved
    
    _mouseMoved = True
    
def mouseMoved():
    global _mouseMoved
    
    answer = _mouseMoved
    _mouseMoved = False
    _doUpdate(True)
    
    return answer

def currentMouse():
    # root = tkinter.Tk()
    global _canvas
    _makeSureWindowCreated()   
    x = _canvas.winfo_pointerx() - _canvas.winfo_rootx()
    y = _canvas.winfo_pointery() - _canvas.winfo_rooty()
    return x,y
    

def _keyCallback(event):
    """
    Check if a key has been typed, and if so, put that key in a queue.
    """
    global _surface
    global _keysTyped

    _makeSureWindowCreated()

    _keysTyped = [event.keysym] + _keysTyped
            

# Functions for retrieving keys

def hasNextKeyTyped():
    """
    Return True if the queue of keys the user typed is not empty.
    Otherwise return False.
    """
    global _keysTyped
    _doUpdate(True)  # AJB 
    return _keysTyped != []

def nextKeyTyped():
    """
    Remove the first key from the queue of keys that the the user typed,
    and return that key.
    """
    global _keysTyped
    return _keysTyped.pop()

# Functions for dealing with mouse clicks 

def mousePressed():
    """
    Returns True if a mouse click is available in the queue, False otherwise
    """
    global _clicks
    global _mousePos
    
    _mousePos = None
    if _clicks != []:
        _mousePos = _clicks.pop()

    _doUpdate(True)
    return _mousePos != None
    
def mouseX():
    """
    Return the x coordinate in user space of the location at
    which the mouse was most recently left-clicked. If a left-click
    hasn't happened yet, raise an exception, since mouseX() shouldn't
    be called until mousePressed() returns True.
    """
    global _mousePos
    if _mousePos:
        return _mousePos[0]      
    raise Exception(
        "Can't determine mouse position if a click hasn't happened")
    
def mouseY():
    """
    Return the y coordinate in user space of the location at
    which the mouse was most recently left-clicked. If a left-click
    hasn't happened yet, raise an exception, since mouseY() shouldn't
    be called until mousePressed() returns True.
    """
    global _mousePos
    if _mousePos:
        return _mousePos[1] 
    raise Exception(
        "Can't determine mouse position if a click hasn't happened")

def mouseLeft():
    """
    Return True if the most recent mouse click was a left button click
    """
    global _mousePos
    if _mousePos:
        return _mousePos[2] == "left"
    raise Exception(
        "Can't determine mouse button if click hasn't happened")

def mouseRight():
    """
    Return True if the most recent mouse click was a right button click
    """
    global _mousePos
    if _mousePos:
        return _mousePos[2] == "right"
    raise Exception(
        "Can't determine mouse button if click hasn't happened")

def _regressionTest():
    """
    Perform regression testing.
    """

    clear()
    setBackground(YELLOW)
    
    setColor(BLUE)
    box = filledRect(20, 20, 20, 20)
    ans = getColor(box)
    print("The color of the box is", ans, "but I set it to", BLUE, flush=True)
    print("The coords of the box are:", coords(box), flush=True)
    
    # Test handling of mouse and keyboard events.
    setColor(BLACK)
    print('Left click with the mouse or type a key')
    while True:
        if mousePressed():
            filledOval(mouseX()-20, mouseY()-20, 40, 40)
        if hasNextKeyTyped():
            print(nextKeyTyped())
        show(0)
        
    # Never get here.
    show()

#-----------------------------------------------------------------------

def _main():
    """
    Dispatch to a function that does regression testing, or to a
    dialog-box-handling function.
    """
    import sys
    if len(sys.argv) == 1:
        _regressionTest()
    elif sys.argv[1] == 'getFileName':
        _getFileName()
    elif sys.argv[1] == 'confirmFileSave':
        _confirmFileSave()
    elif sys.argv[1] == 'reportFileSaveError':
        _reportFileSaveError(sys.argv[2])

if __name__ == '__main__':
    _main()
