from tkinter import *
from math import *

try:
    from VisualizationApp import *
except ModuleNotFoundError:
    from .VisualizationApp import *

class HashBase(VisualizationApp):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def createHasher(
            self, x0=100, y0=320, x1=160, y1=380,
            fill='saddle brown', sections=7, label='HASH',
            font=VisualizationApp.VALUE_FONT, foreground='white'):
        """Create canvas items depicting a hash 'engine' that converts
        strings to numbers.  The hasher will fit within the bounding box."""
        sections = max(2, sections)
        self.hasher = {
            'Blocks': [None] * sections,
            'BBox': (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)),
            'SectionHeight': abs(y1 - y0) * 0.8,
            'SectionOffset': abs(y1 - y0) * 0.1,
            'SectionWidth': abs(x1 - x0) / max(2, sections),
            'Phase': 0,
            }
        self.hasher['Blocks'] = [
            self.canvas.create_rectangle(
                *self.hashBlockCoords(b), fill=fill, outline=None, width=0)
            for b in range(sections)]
        self.hasher['Label'] = self.canvas.create_text(
            (x0 + x1) / 2, (y0 + y1) / 2, text=label, font=font,
            fill=foreground, state=DISABLED)
        
    def hashBlockCoords(self, blockIndex, phase=None):
        h = self.hasher
        if phase is not None:
            h['Phase'] = phase
        fromEnd = min(blockIndex, len(h['Blocks']) - 1 - blockIndex)
        p = h['Phase'] * (1 + fromEnd) + (blockIndex % 2) * pi
        x0 = h['BBox'][0] + h['SectionWidth'] * blockIndex
        x1 = h['BBox'][0] + h['SectionWidth'] * (blockIndex + 1)
        y0 = h['BBox'][1] + h['SectionOffset'] * 2 * (sin(p) + 0.5)
        y1 = y0 + h['SectionHeight']
        return (x0, y0, x1, y1)
            
    def hashInputCoords(self):
        h = self.hasher
        return (h['BBox'][0], (h['BBox'][1] * 2 + h['BBox'][3]) / 3)

    def hashSeedCoords(self):
        h = self.hasher
        return (h['BBox'][0], (h['BBox'][1] + h['BBox'][3] * 2) / 3)

    def hashOutputCoords(self):
        h = self.hasher
        return (h['BBox'][2], (h['BBox'][1] + h['BBox'][3]) / 2)

    def incrementHasherPhase(self, increment=0.2):
        self.hasher['Phase'] += increment
        for bIndex, block in enumerate(self.hasher['Blocks']):
            self.canvas.coords(block, *self.hashBlockCoords(bIndex))

    def positionHashBlocks(self, phase=None):
        for bIndex, block in enumerate(self.hasher['Blocks']):
            self.canvas.coords(block, *self.hashBlockCoords(bIndex, phase))
        
    def animateStringHashing(
            self, text, seed, hashed, sleepTime=0.01,
            callEnviron=None, dx=2, font=VisualizationApp.VARIABLE_FONT, 
            color=VisualizationApp.VARIABLE_COLOR):
        """Animate text and seed flowing into left of hasher and producing
        hashed output string while hasher churns.  Move characters by dx
        on each animation step. Returns list of canvas items for output
        characters"""
        
        if not self.hasher:
            return
        h = self.hasher

        # Create individual character text items to feed into hasher
        text, seed, hashed = str(text), str(seed), str(hashed)
        inputCoords = self.hashInputCoords()
        seedCoords = self.hashSeedCoords()
        outputCoords = self.hashOutputCoords()
        charWidth = self.textWidth(font, 'W')
        characters = set([
            self.canvas.create_text(
                inputCoords[0] - ((len(text) - i) * charWidth),
                inputCoords[1], text=c, font=font, fill=color, state=DISABLED)
            for i, c in enumerate(text)] + [
                    self.canvas.create_text(
                        seedCoords[0] - ((len(seed) - i) * charWidth),
                        seedCoords[1], text=c, font=font, fill=color,
                        state=DISABLED)
                    for i, c in enumerate(seed)])
        for c in characters:
            self.canvas.lower(c)
        if callEnviron:
            callEnviron |= characters

        output = []        # Characters of hashed output
        pad = abs(font[1])
        rightEdge = h['BBox'][2] + pad
        leftmostOutput = rightEdge

        # While there are input characters or characters yet to output or
        # characters to move out of hasher
        while (characters or len(output) < len(hashed) or
               leftmostOutput < rightEdge):
            self.moveItemsBy(    # Move all characters
                characters.union(output), (dx, 0), sleepTime=sleepTime, steps=1)
            self.incrementHasherPhase()
            deletion = False
            for char in list(characters): # For all input characters
                coords = self.canvas.coords(char)  # See if they entered the
                if coords[0] - pad >= h['BBox'][0]: # hasher bounding box and
                    deletion = True       # delete them if they did
                    if callEnviron:
                        callEnviron.discard(char)
                    self.canvas.delete(char)
                    characters.discard(char)
                    
            if output:
                leftmostOutput = self.canvas.coords(output[-1])[0]

            # When there are characters to ouput and we've either already
            # output a character or deleted an input character and there
            # is room for the next output character, create it
            if (len(output) < len(hashed) and (output or deletion) and
                leftmostOutput >= rightEdge):
                output.append(
                    self.canvas.create_text(
                        max(leftmostOutput - charWidth, outputCoords[0]),
                        outputCoords[1], text=hashed[-(len(output) + 1)], 
                        font=font, fill=color, state=DISABLED))
                self.canvas.lower(output[-1])
                if callEnviron:
                    callEnviron.add(output[-1])
        return output
