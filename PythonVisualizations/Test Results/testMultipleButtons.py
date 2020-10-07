# NOTE TO WINDOWS DEVELOPERS
#
# VisualizationApp.py is in this test directory as a symbolic link to
# the version in the parent directory.  Unless you've taken special
# steps to get your Windows system to support symbolic links and for
# git to correctly copy them onto your working copy, the statement
# below to import VisualizationApp will not work.  To run this
# program, copy it to the same directory as VisualizationApp.py and
# run it there.
# On macOS and Linux, the symbolic links should work with the git
# and GitHub Desktop clients using their default settings.

from VisualizationApp import *
import sys
from tkinter import *

__doc__ = '''
USAGE:

Run this program with optional arguments:
  python3 testMultipleButtons.py ['helpText' ...]]]

* The helpText is displayed initially to explain the purpose of the text
  entry areas.  It disappears when clicked or a value is entered in one of
  of the entry areas. 
'''

# Default help text
help='Click to enter argument'

# Parse arguments
try:
   if len(sys.argv) > 1: # Use command line argument if provided
      help = sys.argv[1:]
except:
   print('Error parsing arguments\n', __doc__)
   sys.exit(-1)
   
app = VisualizationApp()

buttons = []
argNumber = IntVar()
argNumber.set(1)
useCheckbutton = IntVar()
useCheckbutton.set(0)

def addOperationWithArg():
   opName = 'Operation {}'.format(len(buttons) + 1)
   buttons.append(app.addOperation(
      opName,
      lambda: app.setMessage('{} invoked with args {}'.format(
         opName, app.getArguments())),
      buttonType=VisualizationApp.buttonTypes[useCheckbutton.get()],
      numArguments=argNumber.get(), 
      helpText=help if isinstance(help, str) else opName + ' help here',
      argHelpText=help if isinstance(help, list) else []))

def changeParams():
   createButton['text'] = createButtonLabel()

# Make buttons that control parameters of buttons to be created
for argCount in range(1,5):
   app.addOperation(
      '{} argument{}'.format(argCount, '' if argCount == 1 else 's'),
      changeParams, buttonType=Radiobutton, value=argCount, variable=argNumber)
app.addOperation('Use Checkbutton', changeParams,
                 buttonType=Checkbutton, variable=useCheckbutton)

def createButtonLabel():
   return 'Create {} with {} argument{}'.format(
      VisualizationApp.buttonTypes[useCheckbutton.get()].__name__,
      argNumber.get(), '' if argNumber.get() == 1 else 's')

createButton = app.addOperation(createButtonLabel(), addOperationWithArg)

app.runVisualization()
