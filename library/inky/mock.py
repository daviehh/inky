import sys
import numpy


from . import inky


class InkyMock(inky.Inky):

    def __init__(self, colour, h_flip=False, v_flip=False):
        """Initialise an Inky pHAT Display.

        :param colour: one of red, black or yellow, default: black

        """
        global tkinter, ImageTk, Image

        try:
            import tkinter
            from PIL import ImageTk, Image
        except ImportError:
            sys.exit('Simulation requires tkinter')

        resolution = (self.WIDTH, self.HEIGHT)

        if resolution not in inky._RESOLUTION.keys():
            raise ValueError('Resolution {}x{} not supported!'.format(*resolution))

        self.resolution = resolution
        self.width, self.height = resolution
        self.cols, self.rows, self.rotation = inky._RESOLUTION[resolution]

        if colour not in ('red', 'black', 'yellow'):
            raise ValueError('Colour {} is not supported!'.format(colour))

        self.colour = colour

        self.h_flip = h_flip
        self.v_flip = v_flip

        bw_inky_palette = [255, 255, 255,  # 0 = white
                           0, 0, 0]  # 1 = black

        red_inky_palette = [255, 255, 255,  # 0 = white
                            0, 0, 0,  # 1 = black
                            255, 0, 0]  # index 2 is red

        ylw_inky_palette = [255, 255, 255,  # 0 = white
                            0, 0, 0,  # 1 = black
                            223, 204, 16]  # index 2 is yellow
        # yellow color value: screen capture from
        # https://www.thoughtsmakethings.com/Pimoroni-Inky-pHAT

        self.c_palette = {"black": bw_inky_palette,
                          "red": red_inky_palette,
                          "yellow": ylw_inky_palette}

        self.tk_root = tkinter.Tk()
        self.tk_root.title("Inky Preview")
        self.tk_root.geometry('{}x{}'.format(self.WIDTH, self.HEIGHT))
        self.tk_root.aspect(self.WIDTH, self.HEIGHT, self.WIDTH, self.HEIGHT)
        self.cv = None
        self.cvh = self.HEIGHT
        self.cvw = self.WIDTH

    def resize(self, event):
        # adapted from:
        # https://stackoverflow.com/questions/24061099/tkinter-resize-background-image-to-window-size
        # https://stackoverflow.com/questions/19838972/how-to-update-an-image-on-a-canvas
        self.cvw = event.width
        self.cvh = event.height
        self.cv.config(width=self.cvw, height=self.cvh)
        image = self.disp_img_copy.resize([self.cvw, self.cvh])
        self.photo = ImageTk.PhotoImage(image)
        self.cv.itemconfig(self.cvhandle, image=self.photo, anchor='nw')
        self.tk_root.update()

    def _send_command(self, command, data=None):
        pass

    def _simulate(self, region):
        pass

    def _display(self, region):
        im = Image.fromarray(region, "P")
        im.putpalette(self.c_palette[self.colour])

        self.disp_img_copy = im.copy()  # can be changed due to window resizing, so copy
        image = self.disp_img_copy.resize([self.cvw, self.cvh])
        self.photo = ImageTk.PhotoImage(image)
        if self.cv is None:
            self.cv = tkinter.Canvas(self.tk_root, width=self.WIDTH, height=self.HEIGHT)
        self.cv.pack(side='top', fill='both', expand='yes')
        self.cvhandle = self.cv.create_image(0, 0, image=self.photo, anchor='nw')
        self.cv.bind('<Configure>', self.resize)
        self.tk_root.update()

    def show(self, busy_wait=True):
        """Show buffer on display.

        :param busy_wait: Ignored. Updates are simulated and instant.

        """
        print(">>simulating...")

        region = self.buf

        if self.v_flip:
            region = numpy.fliplr(region)

        if self.h_flip:
            region = numpy.flipud(region)

        if self.rotation:
            region = numpy.rot90(region, self.rotation // 90)

        self._simulate(region)


class InkyMockPHAT(InkyMock):

    """Inky wHAT e-Ink Display Driver."""

    WIDTH = 212
    HEIGHT = 104

    WHITE = 0
    BLACK = 1
    RED = 2
    YELLOW = 2

    def _simulate(self, region):
        region = numpy.rot90(region, self.rotation // 90)
        region = numpy.flipud(region)  # spec: phat rotated -90
        region = numpy.fliplr(region)  # spec: phat rotated -90
        self._display(region)


class InkyMockWHAT(InkyMock):

    """Inky wHAT e-Ink Display Driver."""

    WIDTH = 400
    HEIGHT = 300

    WHITE = 0
    BLACK = 1
    RED = 2
    YELLOW = 2

    def _simulate(self, region):
        region = numpy.rot90(region, self.rotation // 90)
        region = region.reshape(300, 400)  # for display
        self._display(region)
