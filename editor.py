#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Import python modules
import tkinter
import itertools
from string import printable

# Import 4PX modules
from glyphs import glyphs

# Constants
MIN_X = 10
MIN_Y = 10
MAX_X = MIN_X + 1.5*70
MAX_Y = MIN_Y + 4*230
TAB = 4

#------------------------------------------------------------------------------#
class ColorArray:

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class DataOverflow(Exception): pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class Color:

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        @property
        def value(self):
            return '#' + ''.join('{:02X}'.format(comp*255) for comp in self.rgb)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def __init__(self):
            self.rgb = [0, 0, 0]
            self.index = iter(range(len(self.rgb)))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def extend(self, value):
            try:
                self.rgb[next(self.index)] = value
            except StopIteration:
                raise ColorArray.DataOverflow from None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, number_of_colors=4):
        self.array = [self.Color() for i in range(number_of_colors)]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __iter__(self):
        return iter(self.array)



#------------------------------------------------------------------------------#
class Editor(tkinter.Tk):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, initial_text='', *args, **kwargs):
        # Create window
        tkinter.Tk.__init__(self, *args, **kwargs)
        self.title('4PX')
        # Create Canvas context
        self.canvas = tkinter.Canvas(background='black',
                                     relief=tkinter.FLAT,
                                     cursor='xterm',
                                     width=2*MIN_X + MAX_X,
                                     height=2*MIN_Y + MAX_Y,
                                     highlightthickness=0)
        self.canvas.pack()
        # Initial cursor position
        self.cursor = MIN_X, MIN_Y

        # Initialize color arrays
        self.color_array1 = ColorArray()
        self.color_array2 = ColorArray()

        # Bind function for typing
        self.bind('<Key>', lambda e: self.on_type(e.char))
        self.bind('<Return>', lambda e: self.on_enter())
        self.bind('<Tab>', lambda e: self.on_tab())
        # Insert initial text
        self.insert_text(initial_text)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _draw_pixels(self, x, y, color_array):
        rect = self.canvas.create_rectangle
        # Return canvas ids of the created pixels
        for i, color in enumerate(color_array):
            rect(x, y+i, x+1, y+i+1, width=0, fill=color.value)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_enter(self):
        # Get current cursor coordinate
        x, y = self.cursor
        # If no more vertical space left
        if y == MAX_Y:
            # Do nothing
            return print('You ran out of space!')
        # If there is more vertical space
        # Set x to start position
        x = MIN_X
        # And increase value of y
        y += 5
        # Store new values
        self.cursor = x, y
        # Create new arrays
        self.color_array1 = ColorArray()
        self.color_array2 = ColorArray()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_tab(self):
        for i in range(TAB):
            self.on_type(' ')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_type(self, char):
        # If character has a glyph
        try:
            character = glyphs[char]
            x, y = self.cursor

            color_array3 = ColorArray()
            color_arrays = self.color_array1, self.color_array2, color_array3

            # Go through the character dots, and the three color arrays
            for states, *colors in zip(character, *color_arrays):
                # Start writing subpixel states
                # to the first color array
                colors = iter(colors)
                color = next(colors)
                for state in states:
                    try:
                        color.extend(state)
                    # If first pixel is full
                    except ColorArray.DataOverflow:
                        # Start writing to the second pixel
                        color = next(colors)
                        color.extend(state)
                # Add subpixel space to current pixel
                try:
                    color.extend(0)
                # If current pixel is full
                except ColorArray.DataOverflow:
                    # Start writing to next pixel
                    color = next(colors)
                    color.extend(0)

            # Draw pixels and store canvas IDs
            self._draw_pixels(x, y, self.color_array1)
            self._draw_pixels(x + 1, y, self.color_array2)

            # Switch arrays to get ready for next character
            try:
                color = next(colors)
                self.color_array1 = self.color_array2
                self.cursor = x + 1, y
            except StopIteration:
                self.color_array1 = color_array3
                self.cursor = x + 2, y
            self.color_array2 = ColorArray()

        # If character does not have a glyph
        except KeyError:
            if char in printable:
                print('Character {!r} is not implemented'.format(char))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def insert_text(self, text):
        # Translate each character in text
        for char in text:
            # If new line
            if char == '\n':
                self.on_enter()
            # If tab
            elif char == '\t':
                self.on_tab()
            # Everything else
            else:
                self.on_type(char)


#------------------------------------------------------------------------------#
# Open this python file
with open(__file__) as f:
    # Get text and run 4PX Editor and insert text
    Editor(initial_text=f.read()).mainloop()
