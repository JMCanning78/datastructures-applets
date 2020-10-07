__doc__ = """
Base class for Python visualizations.
Provides common tools for all modules including control panel
and drawing canvas.
The control panel has containers for
 * Functions that take an argument
 * Functions that take no argument
 * A speed control for slow to fast animation or single step increments
 * A text message area for providing messages
 * A text window for showing and highlighting code snippets
"""

import time, math, operator, re, sys
from collections import *
from tkinter import *

try:
    from coordinates import *
except ModuleNotFoundError:
    from .coordinates import *
    
# Utilities for vector math; used for canvas item coordinates
V = vector
def add_vector(v1, v2):
    return V(v1) + V(v2)

def subtract_vector(v1, v2):
    return V(v1) - V(v2)
    return tuple(map(operator.sub, v1, v2))

def divide_vector(v1, v2):   # v2 can be scalar
    if not isinstance(v2, (list, tuple)):
        v2 = [v2] * len(v1)  # Copy scalar value for vector dimension
    return V(v1) / V(v2)

def multiply_vector(v1, v2): # v2 can be scalar
    if not isinstance(v2, (list, tuple)):
        v2 = [v2] * len(v1)  # Copy scalar value for vector dimension
    return V(v1) * V(v2)

def rotate_vector(v1, angle=0): # Rotate vector by angle degrees
    return V(v1).rotate(angle)

def vector_length2(vect):    # Get the vector's length squared
    return V(vect).len2()

def vector_length(vect):     # Get the vector's length
    return V(vect).vlen()

def BBoxesOverlap(bbox1, bbox2): # Determine if bounding boxes overlap
    return (rangesOverlap(bbox1[0], bbox1[2], bbox2[0], bbox2[2]) and 
            rangesOverlap(bbox1[1], bbox1[3], bbox2[1], bbox2[3]))

def rangesOverlap(           # Determine if a range overlaps another
        lo1, hi1, lo2, hi2,  # Allow zero overlap, if requested
        zeroOK=True):
    return ((hi1 > lo2 or (zeroOK and hi1 == lo2)) and
            (lo1 < hi2 or (zeroOK and lo1 == hi2)))
    
def gridDict(frame):
    slaves = frame.grid_slaves()
    return defaultdict(
        lambda: None,
        zip([(int(s.grid_info()['column']), int(s.grid_info()['row']))
             for s in slaves],
            slaves))

# Utilities for validating characters typed in Tk entry widgets
# These must be registered with the parent window before use
def numericValidate(action, index, value_if_allowed, prior_value, text,
                    validation_type, trigger_type, widget_name):
    return len(value_if_allowed) == 0 or value_if_allowed.isdigit()

def makeWidthValidate(maxWidth):
    "Register this with one parameter: %P"
    return lambda value_if_allowed: len(value_if_allowed) <= maxWidth

geom_delims = re.compile(r'[\sXx+-]')


class VisualizationApp(object):  # Base class for Python visualizations

    # Default styles for display of values and operational controls
    FONT_SIZE = 20
    VALUE_FONT = ('Helvetica', FONT_SIZE)
    VALUE_COLOR = 'black'
    VARIABLE_FONT = ('Courier', FONT_SIZE * 8 // 10)
    VARIABLE_COLOR = 'brown3'
    FOUND_FONT = ('Helvetica', FONT_SIZE)
    FOUND_COLOR = 'green2'
    OPERATIONS_BG = 'beige'
    OPERATIONS_BORDER = 'black'
    CODE_FONT = ('Courier', 12)
    SMALL_FONT = ('Helvetica', 9)
    CODE_HIGHLIGHT = 'yellow'
    CONTROLS_FONT = ('Helvetica', 12)
    HINT_FONT = CONTROLS_FONT + ('italic',)
    HINT_FG = 'blue'
    HINT_BG = 'beige'
    CALL_STACK_BOUNDARY = 'gray60'

    # Speed control slider
    SPEED_SCALE_MIN = 10
    SPEED_SCALE_MAX = 500
    SPEED_SCALE_DEFAULT = (SPEED_SCALE_MIN + SPEED_SCALE_MAX) // 2

    # Animation states
    STOPPED = 0
    RUNNING = 1
    PAUSED = 2

    def __init__(  # Constructor
            self,
            window=None,      # Run visualization within given window
            title=None,
            canvasWidth=800,  # Canvas size
            canvasHeight=400,
            maxArgWidth=3,    # Maximum length/width of text arguments
            hoverDelay=1000,  # Milliseconds to wait before showing hints
    ):
        self.title = title
        # Set up Tk windows for canvas and operational controls
        if window:
            self.window = window
        else:
            self.window = Tk()
            if title:
                self.window.title(title)
        self.canvas = Canvas(
            self.window, width=canvasWidth, height=canvasHeight)
        self.canvas.pack(expand=True, fill=BOTH)
        self.maxArgWidth = maxArgWidth
        self.HOVER_DELAY = hoverDelay
        self.setUpControlPanel()

        # Set up instance variables for managing animations and operations
        self.callStack = []    # Stack of local environments for visualziation
        self.animationState = self.STOPPED
        self.pauseButton, self.stopButton = None, None
        
    def setUpControlPanel(self):  # Set up control panel structure
        self.controlPanel = Frame(self.window)
        self.controlPanel.pack(side=BOTTOM, fill=X)
        self.operationsUpper = LabelFrame(self.controlPanel, text="Operations")
        self.operationsUpper.grid(row=0, column=0)
        self.operationsBorder = Frame(
            self.operationsUpper, padx=2, pady=2, bg=self.OPERATIONS_BORDER)
        self.operationsBorder.pack(side=TOP)
        self.operations = Frame(self.operationsBorder, bg=self.OPERATIONS_BG)
        self.opSeparator = None
        self.operations.pack(side=LEFT)
        self.operationsLower = Frame(self.controlPanel)
        self.operationsLower.grid(row=1, column=0)
        self.operationsLowerCenter = Frame(self.operationsLower, padx=2, pady=5)
        self.operationsLowerCenter.pack(side=TOP)
        self.codeFrame = Frame(self.controlPanel)
        self.codeFrame.grid(row=0, column=1, rowspan=2, sticky=(N, E, S, W))
        # self.controlPanel.grid_columnconfigure(1, maxsize=200)
        self.codeText = None

        self.speedControl = None
        self.speedScale = Scale(
            self.operationsLowerCenter, orient=HORIZONTAL,
            from_=self.SPEED_SCALE_MIN, to=self.SPEED_SCALE_MAX,
            showvalue=False, sliderlength=20)
        self.speedScale.grid(row=0, column=1, sticky=W)
        self.speedScale.set(self.SPEED_SCALE_DEFAULT)
        self.slowLabel = Label(
            self.operationsLowerCenter, text="Animation speed:  slow",
            font=self.CONTROLS_FONT)
        self.slowLabel.grid(row=0, column=0, sticky=W)
        self.fastLabel = Label(
            self.operationsLowerCenter, text="fast", font=self.CONTROLS_FONT)
        self.fastLabel.grid(row=0, column=2, sticky=W)
        self.textEntries, self.entryHints = [], []
        self.outputText = StringVar()
        self.outputText.set('')
        self.message = Label(
            self.operationsLowerCenter, textvariable=self.outputText,
            font=self.CONTROLS_FONT + ('italic',), fg="blue")
        self.message.grid(row=0, column=4, sticky=(E, W))
        self.operationsLowerCenter.grid_columnconfigure(4, minsize=200)
        self.operationsLowerCenter.grid_columnconfigure(3, minsize=10)

    buttonTypes = (Button, Checkbutton, Radiobutton)
    
    def addOperation(  # Add a button to the operations control panel
            self,      # The button can require N arguments provided by text
            label,     # entry widgets. Button label
            callback,  # Function to call when button pressed
            numArguments=0, # Count of required user entered arguments
            validationCmd=None, # Tk validation command tuple for argument(s)
            helpText=None,  # Help text for overall operation
            argHelpText=[], # Help text for each argument
            maxRows=4,      # Operations w/o args beyond maxRows -> new columns
            buttonType=Button, # Type of button (see buttonTypes)
            cleanUpBefore=True, # Clean up all previous animations before Op
            **kwargs):       # Tk button keyword args
        gridItems = gridDict(self.operations) # Operations inserted in grid
        nColumns, nRows = self.operations.grid_size()
        withArgument = [
            gridItems[0, row] for row in range(nRows)
            if isinstance(gridItems[0, row], self.buttonTypes)]
        withoutArgument = [
            gridItems[col, row]
            for row in range(nRows) for col in range(4, nColumns)
            if isinstance(gridItems[col, row], self.buttonTypes)]
        if buttonType not in self.buttonTypes:
            raise ValueError('Unknown button type: {}'.format(buttonType))
        button = buttonType( # Create button based on type
            self.operations, text=label, font=self.CONTROLS_FONT,
            command=self.runOperation(callback, cleanUpBefore),
            bg=self.OPERATIONS_BG, **kwargs)
        setattr(button, 'required_args', numArguments)
        if numArguments:
            while len(self.textEntries) < numArguments:  # Build argument entry
                textEntry = self.makeArgumentEntry(
                    validationCmd,
                    argHelpText[len(self.textEntries)]
                    if len(argHelpText) > len(self.textEntries) else '')
                self.textEntries.append(textEntry)
                textEntry.grid(column=2, row=len(self.textEntries), padx=8)
            if argHelpText: # Make a label if there are hints on what to enter
                self.makeEntryHints(argHelpText[:numArguments])

            # Place button in grid of buttons
            buttonRow = len(withArgument) + 1
            button.grid(column=0, row=buttonRow, padx=8, sticky=(E, W))
            button.config(state=DISABLED)
            nEntries = len(self.textEntries)
            rowSpan = max(1, (len(withArgument) + 1) // nEntries)
            
            # Spread text entries across all rows of buttons with arguments
            # with the hint about what to enter below, if any
            for i, entry in enumerate(self.textEntries):
                entryRowSpan = rowSpan if i < nEntries - 1 else max(
                    1, len(withArgument) + 1 - (nEntries - 1) * rowSpan)
                entry.grid_configure(row=rowSpan * i + 1, rowspan=entryRowSpan)
            if self.entryHints:
                self.entryHintRow = max(nEntries, len(withArgument) + 1) + (
                    0 if entryRowSpan > 2 else 1)
                self.entryHints[0].grid_configure(
                    column=2, row=self.entryHintRow)

        else:
            buttonRow = len(withoutArgument) % maxRows + 1
            button.grid(column=4 + len(withoutArgument) // maxRows,
                        row=buttonRow, padx=8, sticky=(E, W))
        if ((len(withoutArgument) if numArguments else len(withArgument)) > 0
                and not self.opSeparator):  # If both kinds of buttons are present
            self.opSeparator = Frame(  # but not a separator line, create one
                self.operations, width=2, bg=self.OPERATIONS_BORDER)
            self.opSeparator.grid(column=3, row=1, sticky=(N, E, W, S))
        if self.opSeparator:
            self.opSeparator.grid_configure(
                rowspan=max(nRows, buttonRow, 
                            self.entryHintRow if self.entryHints else 1))
        if helpText:
            button.bind('<Enter>', self.makeArmHintHandler(button, helpText))
            button.bind('<Leave>', self.makeDisarmHintHandler(button))
            button.bind('<Button>', self.makeDisarmHintHandler(button), '+')
        return button

    def makeArgumentEntry(self, validationCmd, helpText=''):
        entry = Entry(
            self.operations, width=self.maxArgWidth, bg='white',
            validate='key', validatecommand=validationCmd, 
            font=self.CONTROLS_FONT)
        entry.bind(
            '<KeyRelease>', lambda ev: self.argumentChanged(), '+')
        if helpText:
            entry.bind('<Enter>', self.makeArmHintHandler(entry, helpText))
            entry.bind('<Leave>', self.makeDisarmHintHandler(entry))
            entry.bind('<KeyRelease>', self.makeDisarmHintHandler(entry), '+')
        return entry

    def makeEntryHints(self, hints):
        while self.entryHints: # Remove past hints
            self.entryHints.pop().destroy()
        hint = Label(
            self.operations, text='Click to enter ' + ',\n'.join(hints),
            font=self.HINT_FONT, fg=self.HINT_FG, bg=self.HINT_BG)
        hint.bind('<Button>', # Remove the hint when first clicked
                  deleteInitialHintHandler(hint, self.textEntries[0]))
        for entry in self.textEntries: # and when entries get focus
            entry.bind('<FocusIn>', deleteInitialHintHandler(hint, entry))
        self.entryHints = [hint]
        
    def makeArmHintHandler(self, widget, helpText):
        def handler(event):
            setattr(widget, 'timeout_ID',
                    widget.after(
                        self.HOVER_DELAY, 
                        lambda: self.setMessage(helpText) or
                        setattr(widget, 'timeout_ID', None)))
        return handler

    def makeDisarmHintHandler(self, widget):
        def handler(event):
            if event.widget == widget and getattr(widget, 'timeout_ID'):
                widget.after_cancel(getattr(widget, 'timeout_ID'))
            setattr(widget, 'timeout_ID', None)
        return handler

    def addAnimationButtons(self):
        self.pauseButton = self.addOperation(
            "Pause", lambda: self.onClick(self.pause, self.pauseButton),
            cleanUpBefore=False)
        self.pauseButton['state'] = DISABLED
        self.stopButton = self.addOperation(
            "Stop", lambda: self.onClick(self.stop, self.pauseButton),
            cleanUpBefore=False)
        self.stopButton['state'] = DISABLED
        
    def runOperation(self, command, cleanUpBefore):
        def animatedOperation():
            try:
                if cleanUpBefore:
                    self.cleanUp()
                command()
            except UserStop as e:
                self.cleanUp(self.callStack[0] if self.callStack else None)
        return animatedOperation
                
    def getArgument(self, index=0, clear=False):
        if 0 <= index and index < len(self.textEntries):
            val = self.textEntries[index].get()
            if clear:
                self.clearArgument(index)
            return val

    def getArguments(self, clear=False):
        return [self.getArgument(i, clear=clear)
                for i in range(len(self.textEntries))]

    def clearArgument(self, index=0):
        if 0 <= index and index < len(self.textEntries):
            self.textEntries[index].delete(0, END)
            while self.entryHints:
                self.entryHints.pop().destroy()
            self.argumentChanged()

    def setArgument(self, val='', index=0):
        if 0 <= index and index < len(self.textEntries):
            self.textEntries[index].delete(0, END)
            self.textEntries[index].insert(0, str(val))
            while self.entryHints:
                self.entryHints.pop().destroy()
            self.argumentChanged()

    def setArguments(self, *values):
        for index in range(min(len(values), len(self.textEntries))):
            self.textEntries[index].delete(0, END)
            self.textEntries[index].insert(0, str(values[index]))
        self.argumentChanged()

    def argumentChanged(self):
        args = self.getArguments()
        gridItems = gridDict(self.operations)  # All operations
        nColumns, nRows = self.operations.grid_size()
        for button in [gridItems[0, row] for row in range(nRows)
                       if isinstance(gridItems[0, row], self.buttonTypes)]:
            nArgs = getattr(button, 'required_args')
            button['state'] = (
                DISABLED if self.animationState != self.STOPPED or any(
                    arg == '' for arg in args[:nArgs]) else NORMAL)

    def setMessage(self, val=''):
        self.outputText.set(val)

    def showCode(self,     # Show algorithm code in a scrollable text box
                 code,     # Code to display, plus optional boundary line
                 addBoundary=False, # to separate calls on the stack
                 prefix='',    # Prefix to apply to snippet labels
                 snippets={}): # Dict of snippet label -> text indices
        code = code.strip()
        if len(code) == 0:  # Empty code string?
            return          # then nothing to show
        if self.codeText is None:
            self.codeText = Text(
                self.codeFrame, wrap=NONE, background=self.OPERATIONS_BG,
                font=self.CODE_FONT, width=40, height=12, padx=10, pady=10,
                takefocus=False)
            self.codeText.grid(row=0, column=0, sticky=(N, E, S, W))
            self.codeVScroll = Scrollbar(
                self.codeFrame, orient=VERTICAL, command=self.codeText.yview)
            self.codeVScroll.grid(row=0, column=1, rowspan=2, sticky=(N, S))
            self.codeHScroll = Scrollbar(
                self.codeFrame, orient=HORIZONTAL, command=self.codeText.xview)
            self.codeHScroll.grid(row=1, column=0, sticky=(E, W))
            self.codeText['xscrollcommand'] = self.codeHScroll.set
            self.codeText['yscrollcommand'] = self.codeVScroll.set
            self.codeText.tag_config('call_stack_boundary',
                                     font=self.CODE_FONT + ('overstrike',),
                                     background=self.CALL_STACK_BOUNDARY)
        
        self.codeText.configure(state=NORMAL)
        
        # Add a call stack boundary line if requested and other code exists
        currentCode = self.codeText.get('1.0', END)
        if addBoundary and currentCode and not currentCode.isspace():
            self.codeText.insert('1.0',
                                 self.codeText.config('width')[-1] * '-' + '\n')
            self.codeText.tag_add('call_stack_boundary', '1.0', '1.end')
        
        # Add code at top of text widget (above stack boundary, if any)
        self.codeText.insert('1.0', code + '\n')
        self.codeText.see('1.0')
        self.window.update()
       
        # Tag the snippets with unique tag name
        for tagName in snippets:
            self.codeText.tag_add(prefix + tagName, *snippets[tagName])
        self.codeText.configure(state=DISABLED)

    def highlightCodeTags(self, tags, callEnviron):
        codeHighlightBlock = self.getCodeHighlightBlock(callEnviron)
        if codeHighlightBlock is None:  # This shouldn't happen, but...
            return
        if not isinstance(tags, (list, tuple, set)):
            tags = [tags]
        for tagName in self.codeText.tag_names() if self.codeText else []:
            if not tagName.startswith(codeHighlightBlock.prefix):
                continue  # Only change tags for this call environment
            highlight = tagName[len(codeHighlightBlock.prefix):] in tags
            self.codeText.tag_config(
                tagName,
                background=self.CODE_HIGHLIGHT if highlight else '',
                underline=1 if highlight else 0)
            if highlight:
                ranges = self.codeText.tag_ranges(tagName)
                if len(ranges) > 0:
                    self.codeText.see(ranges[0])
        

    # Return the CodeHighlightBlock from the set object from the call stack
    # NOTE: this could be more efficient if the objects on the call stacks
    # were dictionaries but Python doesn't allow mutable objects like a
    # CodeHighlightBlock as keys so we'd need a special key that couldn't
    # be confused with a canvas item (string or integer) to index it
    # Instead, we do a linear search and find it by its type
    def getCodeHighlightBlock(self, callEnvironment):
        for item in callEnvironment:
            if isinstance(item, CodeHighlightBlock):
                return item
            
    def cleanUp(self,         # Remove Tk items from past animations either
                callEnviron=None,  # for a particular call or all calls
                stopAnimations=True): # and stop animations
        if stopAnimations:
            self.stopAnimations()
        minStack = 1 if callEnviron else 0 # Don't clean beyond minimum, keep
        while len(self.callStack) > minStack: # 1st call unless cleaning all
            top = self.callStack.pop()
            self.cleanUpCallEnviron(top)
            if callEnviron and callEnviron == top: # Stop popping stack if a
                break         # a particular call was being cleaned up
                
        if callEnviron is None:  # Clear any messages if cleaning up everything
            self.setMessage()
        if len(self.callStack) == 0: # When call stack is empty
            while len(self.codeFrame.children) > 0: # Remove code window
                tkItem = self.codeFrame.children.popitem()
                tkItem[1].destroy()
            self.codeText = None

    def cleanUpCallEnviron(self, callEnviron): # Clean up a call on the stack
        while len(callEnviron):
            thing = callEnviron.pop()
            if isinstance(thing, (str, int)) and self.canvas.type(thing):
                self.canvas.delete(thing)
            elif isinstance(thing, CodeHighlightBlock) and self.codeText:
                self.codeText.configure(state=NORMAL)
                last_line = int(float(self.codeText.index(END)))
                self.codeText.delete(
                    '1.0', '{}.0'.format(min(last_line, thing.lines + 2)))
                self.codeText.configure(state=DISABLED)

    def createCallEnvironment( # Create a call environment on the call stack
            self,              # for animating a particular call
            code='',           # code for this call, if any
            snippets={}):      # code snippet dictionary, if any
        # The call environment is a set for local variables represented by
        # canvas items plus a codeHighlightBlock that controls code highlights
        codeHighlightBlock = CodeHighlightBlock(code, snippets)
        callEnviron = set([codeHighlightBlock])
        self.callStack.append(callEnviron) # Push environment on stack
        self.showCode(code, addBoundary=True, prefix=codeHighlightBlock.prefix,
                      snippets=snippets)
        return callEnviron
        
    # Tk widget methods
    def widgetDimensions(self, widget):  # Get widget's (width, height)
        geom = geom_delims.split(widget.winfo_geometry())
        if geom[0] == '1' and geom[1] == '1':  # If not yet managed, use config
            geom = (widget.config('width')[-1], widget.config('height')[-1])
        return int(geom[0]), int(geom[1])

    # CANVAS ITEM METHODS
    def canvas_itemconfigure(  # Get a dictionary with the canvas item's
            self, canvasitem): # configuration
        config = self.canvas.itemconfigure(canvasitem)
        for key in config:     # Replace tuple values with the last item
            if isinstance(config[key], tuple):  # in tuple
                config[key] = config[key][-1]
        return config

    def copyCanvasItem(      # Make a copy of an item in the canvas
            self, canvasitem):
        creator = getattr(self.canvas,  # Get canvas creation function for type
                          'create_{}'.format(self.canvas.type(canvasitem)))
        newItem = creator(*self.canvas.coords(canvasitem),
                          **self.canvas_itemconfigure(canvasitem))
        for eventType in self.canvas.tag_bind(canvasitem): # Copy event handlers
            self.canvas.tag_bind(newItem, eventType,
                                 self.canvas.tag_bind(canvasitem, eventType))
        return newItem

    def moveItemsOffCanvas(  # Animate the removal of canvas items by sliding
            self, items,     # them off one of the canvas edges
            edge=N,          # One of the 4 tkinter edges: N, E, S, or W
            steps=10,        # Number of intermediate steps along line
            sleepTime=0.1):  # Base time between steps (adjusted by user)
        if not isinstance(items, (list, tuple, set)):
            items = tuple(items)
        curPositions = [self.canvas.coords(i) for i in items]
        bboxes = [self.canvas.bbox(i) for i in items]
        bbox = bboxes[0]  # Get bounding box of all items
        for bb in bboxes[1:]:
            bbox = [min(bbox[0], bb[0]), min(bbox[1], bb[1]),
                    max(bbox[2], bb[2]), max(bbox[3], bb[3])]
        canvasDimensions = self.widgetDimensions(self.canvas)
        # Compute delta vector that moves them on a line away from the
        # center of the canvas
        delta = ((bbox[0] + bbox[2] - canvasDimensions[0]) / 2,
                 0 - bbox[3])
        if edge == S:
            delta = (delta[0], canvasDimensions[1] - bbox[1])
        elif edge in (W, E):
            delta = (0 - bbox[2],
                     (bbox[1] + bbox[3] - canvasDimensions[1]) / 2)
            if edge == E:
                delta = (canvasDimensions[0] - bbox[0], delta[1])
        # Ensure no more that 45 degree angle to departure boundary
        if abs(delta[0]) > abs(delta[1]) and edge not in (E, W):
            delta = (abs(delta[1]) * (-1 if delta[0] < 0 else 1), delta[1])
        elif abs(delta[0]) < abs(delta[1]) and edge not in (N, S):
            delta = (delta[0], abs(delta[0]) * (-1 if delta[1] < 0 else 1))
        self.moveItemsBy(items, delta, steps=steps, sleepTime=sleepTime)

    def moveItemsBy(         # Animate canvas items moving from their current
            self, items,     # location in a direction indicated by a single
            delta,           # delta vector. items can be 1 item or a list/tuple
            steps=10,        # Number of intermediate steps along line
            sleepTime=0.1):  # Base time between steps (adjusted by user)
        if not isinstance(items, (list, tuple, set)):
            items = tuple(items)
        if not isinstance(delta, (list, tuple)) or len(delta) != 2:
            raise ValueError('Delta must be a 2-dimensional vector')
        if vector_length2(delta) < 0.001: # If delta is tiny
            return           # then no movement is needed
        steps = max(1, steps) # Must use at least 1 step

        # move the items in steps along vector
        moveBy = divide_vector(delta, steps)
        for step in range(steps):
            for item in items:
                self.canvas.move(item, *moveBy)
            self.wait(sleepTime)

    def moveItemsTo(         # Animate canvas items moving from their current
            self, items,     # location to destination locations along line(s)
            toPositions,     # items can be a single item or list of items
            steps=10,        # Number of intermediate steps along line
            sleepTime=0.1):  # Base time between steps (adjusted by user)
        if not isinstance(items, (list, tuple, set)):
            items = tuple(items)
        if not isinstance(toPositions, (list, tuple)):
            raise ValueError('toPositions must be a list or tuple of positions')
        if not isinstance(toPositions[0], (list, tuple)):
            toPositions = tuple(toPositions)
        steps = max(1, steps) # Must use at least 1 step
        moveBy = [divide_vector(subtract_vector(toPos, fromPos), steps)
                  for toPos, fromPos in zip(
                          toPositions,
                          [self.canvas.coords(item)[:2] for item in items])]

        # move the items until they reach the toPositions
        for step in range(steps):
            for i, item in enumerate(items):
                self.canvas.move(item, *moveBy[i])
            self.wait(sleepTime)
            
        # Force position of new objects to their exact destinations
        for pos, item in zip(toPositions, items):
            self.canvas.coords(item, *pos)

    def moveItemsOnCurve(    # Animate canvas items moving from their current
            self, items,     # location to destinations along a curve
            toPositions,     # items can be a single item or list of items
            startAngle=90,   # Starting angle away from destination
            steps=10,        # Number of intermediate steps to reach destination
            sleepTime=0.1):  # Base time between steps (adjusted by user)
        if not isinstance(items, (list, tuple, set)):
            items = tuple(items)
        if not isinstance(toPositions, (list, tuple)):
            raise ValueError('toPositions must be a list or tuple of positions')
        if not isinstance(toPositions[0], (list, tuple)):
            toPositions = tuple(toPositions)
        steps = max(1, steps) # Must use at least 1 step

        # move the items until they reach the toPositions
        for step in range(steps):  # Go through all steps of the annimation
            toGo = steps - 1 - step  # remaining steps to go
            ang = startAngle * toGo / steps  # angle decreases on each step
            scale = 1 + abs(ang) / 180  # scale is larger for higher angles
            for i, item in enumerate(items):
                coords = self.canvas.coords(item)[:2]
                moveBy = rotate_vector(
                    divide_vector(subtract_vector(toPositions[i], coords),
                                  (toGo + 1) / scale),
                    ang)
                self.canvas.move(item, *moveBy)
            self.wait(sleepTime)
            
        # Force position of new objects to their exact destinations
        for pos, item in zip(toPositions, items):
            self.canvas.coords(item, *pos)

    # ANIMATION METHODS
    def speed(self, sleepTime):
        return sleepTime * 50 * self.SPEED_SCALE_MIN / self.speedScale.get()

    def wait(self, sleepTime):    # Sleep for a user-adjusted period
        if sleepTime > 0:
            self.window.update()
            time.sleep(self.speed(sleepTime))
        if self.animationState == self.STOPPED: # If user requested to stop
            raise UserStop()      # animation while waiting then raise exception

    def onClick(self, command, *parameters): # When user clicks an operations
        self.enableButtons(False) # button, disable all buttons,
        command(*parameters)      # run the command, and re-enable the buttons
        if command not in [self.pause, self.play]: # if it was something
            self.enableButtons()  # other than pause or play command
            
    def enableButtons(self, enable=True):
        gridItems = gridDict(self.operations)  # All Tk items in operations 
        nColumns, nRows = self.operations.grid_size() # by grid cell
        for col in range(nColumns):
            for btn in [gridItems[col, row] for row in range(nRows)]:
                # Only change button types, not text entry or other widgets
                # Pause/Stop buttons can only be enabled here
                if isinstance(btn, self.buttonTypes) and (
                        enable or btn not in (self.stopButton, 
                                              self.pauseButton)):
                    btn['state'] = NORMAL if enable else DISABLED

    def stop(self, pauseButton):
        self.stopAnimations()
        self.animationState = self.STOPPED  # Always stop on user request
        pauseButton['text'] = "Play"
        pauseButton['command'] = self.runOperation(
            lambda: self.onClick(self.play, pauseButton), False)

    def pause(self, pauseButton):
        self.pauseAnimations()
        pauseButton['text'] = "Play"
        pauseButton['command'] = self.runOperation(
            lambda: self.onClick(self.play, pauseButton), False)
        while self.animationState == self.PAUSED:
            self.wait(0.05)

    def play(self, pauseButton):
        self.startAnimations()

    def startAnimations(self):
        self.animationState = self.RUNNING
        self.enableButtons(enable=False)
        if self.pauseButton:
            self.pauseButton['text'] = 'Pause'
            self.pauseButton['command'] = self.runOperation(
                lambda: self.onClick(self.pause, self.pauseButton), False)
            self.pauseButton['state'] = NORMAL
        if self.stopButton:
            self.stopButton['state'] = NORMAL

    def stopAnimations(self):  # Stop animation of a call on the call stack
        # Calls from stack level 2+ only stop animation for their level
        # At lowest level, animation stops and play & stop buttons are disabled
        if len(self.callStack) <= 1:
            self.animationState = self.STOPPED
            self.enableButtons(enable=True)
            if self.pauseButton:
                self.pauseButton['state'] = DISABLED
            if self.stopButton:
                self.stopButton['state'] = DISABLED
            self.argumentChanged()
        # Otherwise, let animation be stopped by a lower call

    def pauseAnimations(self):
        self.animationState = self.PAUSED

    def runVisualization(self):
        self.window.mainloop()

# Class to hold information about visualizing the code during animation
# of a particular call on the call stack
class CodeHighlightBlock(object):
    counter = 1
    
    def __init__(self,       # Constructor takes code block and snippets
                 code,       # and makes a unique prefix for snippet keys
                 snippets):  # to translate them into a unique tag name
        self.code = code.strip()
        self.lines = len(self.code.split('\n')) if len(code) > 0 else 0
        self.snippets = snippets
        self.prefix = '{:04d}-'.format(self.counter)
        CodeHighlightBlock.counter += 1

class UserStop(Exception):   # Exception thrown when user stops animation
    pass

# Tk widget utilities

# Tkinter returns a string with a large integer followed by <lambda>
# as a handler ID.  The calls to .bind() without a handler function
# return an executable Python string containing handler IDs.  This
# regular expression extracts the identifier from the executable
# Python string.  The re.sub function is used on the compiled regex to
# run a function on each handler ID in the the binding string.
bindingID = re.compile(r'\d+<lambda>', re.IGNORECASE)

def deleteInitialHintHandler(hint, textEntry):
    "Remove a hint when clicked or when text is first entered in textEntry"
    return lambda event: (
        textEntry.focus_set() if event.widget == hint else 0) or (
            hint.destroy() or
            # Remove any bound handlers the textEntry has for <FocusIn> events
            bindingID.sub(lambda ID: textEntry.unbind(ID),
                          textEntry.bind('<FocusIn>')))
