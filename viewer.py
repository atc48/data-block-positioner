import tkinter as tk
from tkinter import ttk
import math
import re


WND_W = 800
WND_H = 600


class Pos:

    def __init__(self, x, y):
        self.x, self.y = x, y
        
    def dup(self):
        return Pos(self.x, self.y)
    
    def offset(self, xoffset, yoffset):
        return Pos(self.x + xoffset, self.y + yoffset)
    
    def rotate_by(self, distance, direction):
        return self.offset(
            distance * math.cos(math.radians(direction)),
            distance * math.sin(math.radians(direction))
        )

    def mult(self, x_mult, y_mult):
        return Pos(
            self.x * x_mult,
            self.y * y_mult
        )

    def to_list(self):
        return [self.x, self.y]


class Size:

    def __init__(self, w, h):
        self.w, self.h = w, h

    def dup(self):
        return Size(self.w, self.h)

    def rect_points_with_center_pos(self, pos, back_origin=False):
        w_half, h_half = self.w / 2, self.h / 2
        res = [ pos.offset(
            sign[0] * w_half,
            sign[1] * h_half
        ) for sign in [
            [-1, -1], # left-top
            [-1, +1], # left-bottom
            [+1, +1], # right-bottom
            [+1, -1]] # right-top
        ]
        if back_origin:
            res.append(res[0])
        return res


TARGET_BLOCK_DISTANCE = 60
TARGET_BLOCK_ROTATE = 90
TARGET_BLOCK_SIZE = Size(80, 40)

    
class Target:

    id_inc = 0

    def __init__(self, x, y, heading=0):
        self.x, self.y = x, y
        self.heading = heading % 360
        self.view_id = self.__mk_view_id()

    def __mk_view_id(self):
        Target.id_inc += 1
        return "Target_" + str(Target.id_inc)

    def pos(self):
        return Pos(self.x, self.y)

    def block_pos(self):
        return self.block_default_pos()

    def block_default_pos(self):
        rotate_from_heading = TARGET_BLOCK_ROTATE
        distance = TARGET_BLOCK_DISTANCE
        direction = (self.heading + rotate_from_heading) % 360
        return self.pos().rotate_by(distance, direction)

    def block_size(self):
        return TARGET_BLOCK_SIZE.dup()


TARGET_RADIUS   = 10/2
TARGET_COLOR    = "red"
TARGET_NOSE_LEN   = TARGET_RADIUS * 2
TARGET_NOSE_WIDTH = 2


class CanvasDrawer:

    def __init__(self, parent):
        self.canvas = tk.Canvas(parent, width = WND_W, height = WND_H)

    def clear(self):
        self.canvas.delete("all")
        self

    def draw(self, target):
        self.__drawSymbol(target.pos(), target.view_id)
        self.__drawNose(target.pos(), target.heading, target.view_id)
        self.__drawBlock(target.pos(), target.block_pos(), target.block_size(), target.view_id)
        self.canvas.pack()
        return self

    def __drawSymbol(self, pos, tag):
        rad = TARGET_RADIUS
        color = TARGET_COLOR
        self.canvas.create_oval(
            *self.__offset([-rad, -rad, rad, rad], [pos.x, pos.y]),
            fill=color, outline = color,
            tag=tag
        )

    def __drawNose(self, pos, heading, tag):
        size = TARGET_NOSE_LEN
        color = TARGET_COLOR
        width = TARGET_NOSE_WIDTH
        self.canvas.create_line(
            *self.__offset(
                [0,0,
                 math.cos(math.radians(heading)) * size,
                 math.sin(math.radians(heading)) * size],
                [pos.x, pos.y]
            ),
            fill=color, width=width,
            tag = tag
        )

    def __drawBlock(self, target_pos, block_pos, size, tag):
        width = 1
        color = "gray"
        self.canvas.create_line(
            target_pos.x, target_pos.y,
            block_pos.x, block_pos.y,
            fill=color, width=width,
            tag = tag
        )
        rect_points = [p.to_list() for p in
                       size.rect_points_with_center_pos(block_pos, True)]
        self.canvas.create_line(
            *sum(rect_points, []), # flatten
            fill=color, width=width,
            tag = tag
        )
     
    def __offset(self, coordinates, offset):
        ret = coordinates[:]
        for i in range(len(ret)):
            ret[i] = ret[i] + offset[i % 2]
        return ret


class WindowEventHandler:

    def __init__(self, canvas, target_stream, form):
        canvas.bind("<Button-1>", self.__onClicked)
        self.target_stream = target_stream
        self.form = form

    def __onClicked(self, e):
        self.target_stream.append(e.x, e.y, self.form.heading())


class TargetStream:

    def __init__(self):
        self.observers = []
        self.targets = []

    def on_append(self, fn):
        self.observers.append( fn )

    def append(self, x, y, hdg=0):
        target = Target(x, y, hdg)
        self.targets.append( target )
        for fn in self.observers:
            fn(target)


class Form:

    def __init__(self, parent):
        frame = tk.Frame(parent)
        frame.pack(side=tk.BOTTOM)
        
        label = tk.Label(frame, text=u'HEADING:')
        label.grid(column=0,row=0)
        heading = ttk.Combobox(frame, width=5)
        heading['values'] = tuple([i * 10 for i in range(36)])
        heading.set(180)
        heading.grid(column=1,row=0)
        self.__heading = heading

    def heading(self):
        val = self.__heading.get()
        m = re.search('[0-9]+', val)
        return m and int(m.group(0)) or 0


def show_window():
    root = tk.Tk()
    root.title("WINDOW")
    root.geometry("{}x{}".format(WND_W, WND_H))

    form = Form(root)
    target_stream = TargetStream()
    drawer = CanvasDrawer(root)
    handler = WindowEventHandler(drawer.canvas, target_stream, form)

    target_stream.on_append(
        lambda target:
        drawer.draw(target)
    )

    target_stream.append(100, 100, 180)

    root.mainloop()


if __name__ == '__main__':
    show_window()
