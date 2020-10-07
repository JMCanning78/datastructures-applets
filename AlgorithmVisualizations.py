#! /usr/bin/env python3
__doc__ = """
Program to show algorithm visualizations in a tabbed Tk notebook presentation
form.
This program loads all the visualization modules in a Python package.
It searches the modules for classes that are subclasses of VisualizationApp 
and instantiates each one in a separate tab.  When the user clicks on a
tab, it calls the class's runVisualization method.
A preferred order for the modules (by class name) controls the order of
the recognized modules.  The rest are added in alphabetical order.
"""

import argparse, sys, re, webbrowser
from tkinter import *
from tkinter import ttk
from PythonVisualizations import VisualizationApp
import PythonVisualizations

PREFERRED_ORDER = [
    'Array', 'OrderedArray', 'SimpleArraySort', 'Stack', 'SimpleQueue',
    'PriorityQueue', 'PostfixEvaluate', 'LinkedList', 'TowersOfHanoi',
    'MergeSort', 'AdvancedArraySort', 'BinaryTree', 'Tree234', 'AVLTree',
    'RedBlackTree', 'Quadtree', 'HashTableOpenAddressing',
    'HashTableChaining', 'Heap', 'Graph', 'WeightedGraph', 'BloomFilter',
    'SkipList',
    ]

def findVisualizations(module, verbose=0):
    classes = []
    for name in dir(module):
        this = getattr(module, name)
        if isinstance(this, type(VisualizationApp)) and (
                hasattr(this, 'runVisualization') and
                isinstance(getattr(this, 'runVisualization'),
                           type(VisualizationApp.runVisualization)) and
                this is not VisualizationApp):
            if verbose > 1:
                print('Found {}.{}, a subclass of VisualizationApp'.format(
                    module.__name__, name))
            classes.append(this)
        elif verbose > 2 or (
                verbose == 2 and isinstance(this, type(PythonVisualizations))):
            print('Ignoring {}.{} of type {}'.format(
                module.__name__, name, type(this)), file=sys.stderr)
    return classes

URL_pattern = re.compile(r'(https*|ftp)://[\w-]+\.[\w/.,?&=#%-]+')

TAB_FONT = ('Calibri', 16)
INTRO_FONT = ('Helvetica', 16)

intro_msg = """
Welcome to the algorithm visualizations for the book:
Data Structures and Algorithms in Python

Please use these visualization tools along with the
book to improve your understanding of how computers
organize and manipulate data efficiently.

Select tabs at the top to see the different data structures.


Exceptional students in the Computer Science Department of
Stern College at Yeshiva University developed these visualizations.
https://www.yu.edu/stern/ug/computer-science
"""

def openURL(URL):         # Make a callback function to open an URL
    return lambda e: webbrowser.open(URL)

def showVisualizations(   # Display a set of VisualizationApps in a ttk.Notebook
        classes, start=None, title="Algorithm Visualizations", verbose=0):
    top = Tk()
    top.title(title)
    ttk.Style().configure("TNotebook.Tab", font=TAB_FONT,
                          padding=[12, TAB_FONT[1] * 5 // 8, 12, 2])
    notebook = ttk.Notebook(top)
    intro = ttk.Frame(notebook)
    for line in intro_msg.split('\n'):
        URLs = [m for m in URL_pattern.finditer(line)]
        if URLs:
            frame = ttk.Frame(intro)
            last = 0
            for match in URLs:
                if match.start() > last:
                    ttk.Label(frame, text=line[last:match.start()],
                              font=INTRO_FONT).pack(side=LEFT)
                link = ttk.Label(
                    frame, text=match.group(), font=INTRO_FONT + ('underline',),
                    foreground="blue")
                link.pack(side=LEFT)
                link.bind('<Button-1>', openURL(match.group()))
                last = match.end()
            if last < len(line):
                ttk.Label(frame, text=line[last:], 
                          font=INTRO_FONT).pack(side=LEFT)
            frame.pack()
        else:
            ttk.Label(intro, text=line, font=INTRO_FONT).pack()
    loading = ttk.Label(intro, text='\nLoading ...', 
                        font=INTRO_FONT + ('italic',))
    loading.pack()
    notebook.add(intro, state=NORMAL, text='Introduction', padding=8)
    notebook.pack(expand=True, fill=BOTH)
    notebook.wait_visibility(top)

    classes_dict = dict((app.__name__, app) for app in classes)
    ordered_classes = [classes_dict[app] for app in PREFERRED_ORDER
                       if app in classes_dict]
    ordered_classes += [app for app in classes
                        if app.__name__ not in PREFERRED_ORDER]
    
    for j, app in enumerate(ordered_classes):
        if verbose > 0:
            print('Found app {} and instantiating'.format(app.__name__),
                  file=sys.stderr)
        pane = ttk.Frame(notebook)
        loading['text'] = '\nLoading module {} of {} modules...'.format(
            j + 1, len(classes))
        vizApp = app(window=pane)
        name = getattr(vizApp, 'title', app.__name__)
        notebook.add(pane, text=name)
        if start and start.lower() in (app.__name__.lower(), name.lower()):
            notebook.select(pane)
    loading.destroy()
    top.mainloop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-s', '--start', 
        help='Starting tab.  '
        'Should match one of the visualization module titles or class name.')
    parser.add_argument(
        '-t', '--title',  default='Algorithm Visualizations',
        help='Title for top level window')
    parser.add_argument(
        '-v', '--verbose', action='count', default=0,
        help='Add verbose comments')
    args = parser.parse_args()

    showVisualizations(findVisualizations(PythonVisualizations, args.verbose),
                       start=args.start, title=args.title, verbose=args.verbose)
