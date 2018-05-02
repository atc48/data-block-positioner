import math
import re
import random
import tkinter as tk
from tkinter import ttk
from target_model import *


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
TARGET_RADIUS = 10/2
TARGET_COLOR = "red"
TARGET_NOSE_LEN = TARGET_RADIUS * 2
TARGET_NOSE_WIDTH = 2


class CanvasDrawer:

    def __init__(self, parent):
        self.canvas = tk.Canvas(
            parent, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

    def clear(self):
        self.canvas.delete("all")
        self

    def draw(self, target):
        self.__drawSymbol(target.pos(), target.view_id)
        self.__drawNose(target.pos(), target.heading, target.view_id)
        self.__drawBlock(target.pos(), target.block_pos(),
                         target.block_size(), target.view_id)
        self.canvas.pack()
        return self

    def __drawSymbol(self, pos, tag):
        rad = TARGET_RADIUS
        color = TARGET_COLOR
        self.canvas.create_oval(
            *self.__offset([-rad, -rad, rad, rad], [pos.x, pos.y]),
            fill=color, outline=color,
            tag=tag
        )

    def __drawNose(self, pos, heading, tag):
        size = TARGET_NOSE_LEN
        color = TARGET_COLOR
        width = TARGET_NOSE_WIDTH
        self.canvas.create_line(
            *self.__offset(
                [0, 0,
                 math.cos(math.radians(heading)) * size,
                 math.sin(math.radians(heading)) * size],
                [pos.x, pos.y]
            ),
            fill=color, width=width,
            tag=tag
        )

    def __drawBlock(self, target_pos, block_pos, size, tag):
        width = 1
        color = "gray"
        self.canvas.create_line(
            target_pos.x, target_pos.y,
            block_pos.x, block_pos.y,
            fill=color, width=width,
            tag=tag
        )
        rect_points = [p.to_list() for p in
                       size.rect_points_with_center_pos(block_pos, True)]
        self.canvas.create_line(
            *sum(rect_points, []),  # flatten
            fill=color, width=width,
            tag=tag
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
        self.observers.append(fn)

    def append(self, x, y, hdg=0):
        target = Target(x, y, hdg)
        self.targets.append(target)
        for fn in self.observers:
            fn(target)


class Form:

    def __init__(self, parent):
        frame = tk.Frame(parent)
        frame.pack(side=tk.BOTTOM)

        label = tk.Label(frame, text=u'HEADING:')
        label.grid(column=0, row=0)
        heading = ttk.Combobox(frame, width=5)
        heading['values'] = tuple([i * 10 for i in range(36)])
        heading.set(180)
        heading.grid(column=1, row=0)
        self.__heading = heading

    def heading(self):
        val = self.__heading.get()
        m = re.search('[0-9]+', val)
        return m and int(m.group(0)) or 0


def show_window():
    root = tk.Tk()
    root.title("WINDOW")
    root.geometry("{}x{}".format(WINDOW_WIDTH, WINDOW_HEIGHT))

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
