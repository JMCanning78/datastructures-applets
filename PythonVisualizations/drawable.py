import functools

@functools.total_ordering
class drawable(object):      # A record describing a drawable Tk object
    def __init__(            # Constructor
            self, val=None,  # Value in data structure to be displayed
            color=None,      # Background color to use
            display_shape=None, # Tk display object for background
            display_val=None): # Tk display object for value
        self.val = val       # Store initial arguments
        self.color = color
        self.display_shape = display_shape
        self.display_val = display_val

    __fields = ('val', 'color', 'display_shape', 'display_val')

    def __getitem__(self, key): # Implement posititional field access
        if isinstance(key, int):
            if 0 <= key and key < len(self.__fields):
                return getattr(self, self.__fields[key])
            raise IndexError
        elif isinstance(key, str):
            return getattr(self, key)
        raise ValueError

    def __setitem__(self, key, val): # Implement posititional field access
        if isinstance(key, int):
            if 0 <= key and key < len(self.__fields):
                return setattr(self, self.__fields[key], val)
            raise IndexError
        elif isinstance(key, str):
            return setattr(self, key, val)
        raise ValueError

    def __eq__(self, other):  # Equality test between drawables
        if self._is_valid_operand(other): # Only test value to preserve
            return self.val == other.val  # sort stability
        return NotImplemented

    def __lt__(self, other):  # Less than test between drawables
        if self._is_valid_operand(other): # Only test value to preserve
            return self.val < other.val   # sort stability
        return NotImplemented
        
    def _is_valid_operand(self, other): # Check that other is drawable
        return isinstance(other, drawable)

    def __len__(self):
        return len(self.__fields)

    def __str__(self):
        return '<drawable: {}>'.format(', '.join(repr(attr) for attr in self))
        
    def copy(self):          # Retun a copy of this drawable
        return drawable(*(attr for attr in self))
    
    palette = ['indianRed2', 'PaleGreen2', 'SkyBlue2', 'orange2',
               'yellow2', 'magenta2', 'cyan2', 'DodgerBlue2',
               'turquoise3', 'slate gray', 'gold', 'pink']
