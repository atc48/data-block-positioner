import math


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
        res = [pos.offset(
            sign[0] * w_half,
            sign[1] * h_half
        ) for sign in [
            [-1, -1],  # left-top
            [-1, +1],  # left-bottom
            [+1, +1],  # right-bottom
            [+1, -1]]  # right-top
        ]
        if back_origin:
            res.append(res[0])
        return res


TARGET_BLOCK_DISTANCE = 60
TARGET_BLOCK_ROTATE = 90
TARGET_BLOCK_SIZE = Size(80, 40)


class Target:

    __id_inc = 0

    def __init__(self, x, y, heading=0):
        self.x, self.y = x, y
        self.heading = heading % 360
        self.view_id = self.__mk_view_id()

    def __mk_view_id(self):
        Target.__id_inc += 1
        return "Target_" + str(Target.__id_inc)

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

    def to_list(self):
        return [self.x, self.y, self.heading]


def random_target():
    target = Target(
        random.randint(0, WINDOW_WIDTH),
        random.randint(0, WINDOW_HEIGHT),
        random.randint(0, 35) * 10
    )
    return target
