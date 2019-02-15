import random
import time
from tkinter import *
from recordclass import recordclass

WIDTH = 800
HEIGHT = 400

CELL_SIZE = 50
ARRAY_X0 = 100
ARRAY_Y0 = 100

class Array(object):
    Element = recordclass('Element', ['val', 'color', 'display_shape', 'display_val'])
    Element.__new__.__defaults__ = (None,) * len(Element._fields)

    colors = ['red', 'green', 'blue', 'orange', 'yellow', 'cyan', 'magenta',
              'dodgerblue', 'turquoise', 'grey', 'gold', 'pink']
    nextColor = 0

    def __init__(self, size=0):
        self.list = [0]*size

    def __str__(self):
        return str(self.list)

    # ANIMATION METHODS
    def speed(self, sleepTime):
        return (sleepTime * (scaleDefault + 50)) / (scale.get() + 50)

    # ARRAY FUNCTIONALITY
    def isSorted(self):
        for i in range(1, len(self.list)):
            if self.list[i] < self.list[i-1]:
                return False
        return True

    def get(self, index):
        try:
            return self.list[index][0]
        except:
            print("Invalid list index")
            return -1

    def set(self, index, val):
        # reset the value of the Element at that index to val
        self.list[index].val = val

        # get the position of the displayed value
        pos = canvas.coords(self.list[index].display_val)

        # delete the displayed value and replace it with the updated value
        canvas.delete(self.list[index].display_val)
        self.list[index].display_val = canvas.create_text(pos[0], pos[1], text=str(val), font=('Helvetica', '20'))

        # update window
        window.update()

    def append(self, val):
        # create new cell and cell value display objects
        cell = canvas.create_rectangle(ARRAY_X0+CELL_SIZE*len(self.list), ARRAY_Y0, ARRAY_X0+CELL_SIZE*(len(self.list)+1), ARRAY_Y0 + CELL_SIZE, fill=Array.colors[Array.nextColor])
        cell_val = canvas.create_text(ARRAY_X0+CELL_SIZE*len(self.list) + (CELL_SIZE / 2), ARRAY_Y0 + (CELL_SIZE / 2), text=val,
                                      font=('Helvetica', '20'))

        # add a new Element to the list with the new value, color, and display objects
        self.list.append(Array.Element(val, Array.colors[Array.nextColor], cell, cell_val))

        # increment nextColor
        Array.nextColor = (Array.nextColor + 1) % len(Array.colors)

        # update window
        window.update()

    def removeFromEnd(self):
        # pop an Element from the list
        n = self.list.pop()

        # delete the associated display objects
        canvas.delete(n.display_shape)
        canvas.delete(n.display_val)

        # update window
        window.update()

    def display(self):
        canvas.delete("all")
        xpos = ARRAY_X0
        ypos = ARRAY_Y0

        # go through each Element in the list
        for n in self.list:
            print(n)
            # create display objects for the associated Elements
            cell = canvas.create_rectangle(xpos, ypos, xpos+CELL_SIZE, ypos+CELL_SIZE, fill=n[1])
            cell_val = canvas.create_text(xpos+(CELL_SIZE/2), ypos+(CELL_SIZE/2), text=n[0], font=('Helvetica', '20'))

            # save the display objects to the appropriate attributes of the Element object
            n.display_shape = cell
            n.display_val = cell_val

            # increment xpos
            xpos += CELL_SIZE

        window.update()

    def find(self, val):
        global cleanup, running
        running = True
        findDisplayObjects = []
        #canvas.delete(findDisplayObjects)
        self.display()

        # draw an arrow over the first cell
        x = ARRAY_X0 + (CELL_SIZE/2)
        y0 = ARRAY_Y0 - 40
        y1 = ARRAY_Y0 - 15
        arrow = canvas.create_line(x, y0, x, y1, arrow="last", fill='red')
        findDisplayObjects.append(arrow)

        # go through each Element in the list
        for n in self.list:
            window.update()

            # if the value is found
            if n.val == val:
                # get the position of the displayed cell and val
                #posCell = canvas.coords(n.display_shape)
                posVal = canvas.coords(n.display_val)

                # cover the current display value with the updated value in green
                #cell_shape = canvas.create_rectangle(posCell[0], posCell[1], posCell[2], posCell[3], fill=n[1])
                cell_val = canvas.create_text(posVal[0], posVal[1], text=str(val), font=('Helvetica', '25'), fill='green2')

                # add the green value to findDisplayObjects for cleanup later
                #findDisplayObjects.append(cell_shape)
                findDisplayObjects.append(cell_val)

                # update the display
                window.update()

                cleanup += findDisplayObjects
                #canvas.after(1000, canvas.delete, arrow)
                #canvas.after(1000, canvas.delete, cell_val)
                return True

            # if the value hasn't been found, wait 1 second, and then move the arrow over one cell
            time.sleep(self.speed(1))
            canvas.move(arrow, CELL_SIZE, 0)

            if not running:
                break

        cleanup += findDisplayObjects
        #canvas.after(1000, canvas.delete, arrow)
        return False

    def remove(self, index):
        n = self.list.pop(3)
        canvas.delete(n.display_shape)
        canvas.delete(n.display_val)
        window.update()

def stop(pauseButton): # will stop after the current shuffle is done
    global running
    running = False

    if waitVar.get():
        play(pauseButton)

def pause(pauseButton):
    global waitVar
    waitVar.set(True)

    pauseButton['text'] = "Play"
    pauseButton['command'] = lambda: onClick(play, pauseButton)

    canvas.wait_variable(waitVar)

def play(pauseButton):
    global waitVar
    waitVar.set(False)

    pauseButton['text'] = 'Pause'
    pauseButton['command'] = lambda: onClick(pause, pauseButton)

def onClick(command, parameter = None):
    cleanUp()
    disableButtons()
    if parameter:
        command(parameter)
    else:
        command()
    if command not in [pause, play]:
        enableButtons()

def cleanUp():
    global cleanup
    if len(cleanup) > 0:
        for o in cleanup:
            canvas.delete(o)
    outputText.set('')
    window.update()

# Button functions
def clickFind():
    entered_text = textBox.get()
    txt = ''
    if entered_text:
        result = array.find(int(entered_text))
        if result:
            txt = "Found!"
        else:
            txt = "Value not found"
        outputText.set(txt)

def clickInsert():
    entered_text = textBox.get()
    if entered_text:
        array.append(int(entered_text))
        textBox.setvar('')

def close_window():
    window.destroy()
    exit()

def disableButtons():
    for button in buttons:
        button.config(state = DISABLED)

def enableButtons():
    for button in buttons:
        button.config(state = NORMAL)

def makeButtons():
    findButton = Button(bottomframe, text="Find", width=7, command= lambda: onClick(clickFind))
    findButton.grid(row=2, column=1)
    insertButton = Button(bottomframe, text="Insert", width=7, command= lambda: onClick(clickInsert))
    insertButton.grid(row=2, column=2)
    deleteButton = Button(bottomframe, text="Delete", width=7, command= lambda: onClick(array.removeFromEnd))
    deleteButton.grid(row=2, column=3)
    buttons = [findButton, insertButton, deleteButton]
    return buttons

window = Tk()
frame = Frame(window)
frame.pack()

waitVar = BooleanVar()

canvas = Canvas(frame, width=WIDTH, height=HEIGHT)
window.title("Array")
canvas.pack()

bottomframe = Frame(window)
bottomframe.pack(side=BOTTOM)

#Label(bottomframe, text="Find:", font="none 12 bold").grid(row=0, column=0, sticky=W)
textBox = Entry(bottomframe, width=20, bg="white")
textBox.grid(row=4, column=0, sticky=W)
scaleDefault = 100
scale = Scale(bottomframe, from_=1, to=200, orient=HORIZONTAL, sliderlength=15)
scale.grid(row=5, column=1, sticky=W)
scale.set(scaleDefault)
scaleLabel = Label(bottomframe, text="Speed:", font="none 10")
scaleLabel.grid(row=5, column=0, sticky=E)

# add a submit button
#Button(bottomframe, text="Find", width=6, command=lambda: array.onClick(clickFind)).grid(row=0, column=2, sticky=W)
outputText = StringVar()
outputText.set('')
output = Label(bottomframe, textvariable=outputText, font="none 12 bold")
output.grid(row=4, column=1, sticky=E)

# exit button
Button(bottomframe, text="EXIT", width=4, command=close_window).grid(row=6, column=3, sticky=W)

cleanup = []
array = Array()
buttons = makeButtons()
array.display()

for i in range(10):
    array.append(i)

window.mainloop()

'''
To Do:
- make it look pretty
- animate insert and delete
- delete/insert at index?
- label arrows for sorts (inner, outer, etc.)
- implement shell sort, radix sort, quick sort
'''