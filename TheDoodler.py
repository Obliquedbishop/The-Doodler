import turtle
from quickdraw import QuickDrawData
import random
import os
from math import sin, cos
import numpy as np
from collections import OrderedDict

TURTLE_SIZE = 20
OBJECT_NAMES = []
doodle_area_dict = OrderedDict()
drawing_dict = {}
pencil_counter = 0
turtle_stroke_dict = dict()
flag = 0

border = turtle.Turtle()
border.hideturtle()
a1 = []
modify_input = ""
BIN_FILE_PATH = "./.quickdrawcache"
for bin_file in os.listdir(BIN_FILE_PATH):
    bin_file_name = bin_file.removesuffix(".bin")
    OBJECT_NAMES.append(bin_file_name)

# Setting up the screen
notebook = turtle.Screen()
notebook.title("Custom Doodles")
notebook.screensize(1920, 1080)
notebook.setup(width=1.0, height=1.0)
turtle.setworldcoordinates(-10, 1080, 1920, -10)
notebook.colormode(255)
notebook.bgcolor("black")


def choose_doodle():
    qd = QuickDrawData()
    doodle_name = random.choice(OBJECT_NAMES)
    selected_doodle = qd.get_drawing(doodle_name)
    # im = selected_doodle.get_image()
    # im.show()
    doodle_strokes = selected_doodle.strokes
    return doodle_strokes


def doodle_area(pencil, doodle_strokes, coordinates):
    x, y = coordinates
    x_max, x_min, y_max, y_min = max_min(doodle_strokes)
    area_set = set()
    y_max = round(y_max)
    x_max = round(x_max)
    for y_pos in range(0, y_max):
        a_y = round(y_pos + y)
        for x_pos in range(0, x_max):
            a_x = round(x_pos + x)
            area_set.add((a_x, a_y))
    doodle_area_dict[pencil] = area_set


def update_area(pencil, doodle_strokes, coordinates):
    doodle_area(pencil, doodle_strokes, coordinates)
    for i in doodle_area_dict:
        if i == pencil:
            break
        else:
            doodle_area_dict[i] = doodle_area_dict[i] - doodle_area_dict[pencil]


def scale_strokes(doodle_strokes, factor=1.0):
    scaled_doodle_strokes = []
    for doodle_stroke in doodle_strokes:
        scaled_doodle_stroke = []
        for stroke_position in doodle_stroke:
            x, y = stroke_position
            x = x * factor
            y = y * factor
            scaled_doodle_stroke.append((x, y))
        scaled_doodle_strokes.append(scaled_doodle_stroke)
    return scaled_doodle_strokes


def translate_strokes(doodle_strokes, coordinates=(0.0, 0.0)):
    xn, yn = coordinates
    translated_doodle_strokes = []
    for doodle_stroke in doodle_strokes:
        translated_doodle_stroke = []
        for stroke_position in doodle_stroke:
            x, y = stroke_position
            x = x + xn
            y = y + yn
            translated_doodle_stroke.append((x, y))
        translated_doodle_strokes.append(translated_doodle_stroke)
    return translated_doodle_strokes


def max_min(doodle_strokes):
    x_max_n = 0
    x_min_n = 0
    y_max_n = 0
    y_min_n = 0
    for doodle_stroke in doodle_strokes:
        for stroke_position in doodle_stroke:
            x, y = stroke_position
            if x > x_max_n:
                x_max_n = x
            if y > y_max_n:
                y_max_n = y
            if x < x_min_n:
                x_min_n = x
            if y < y_min_n:
                y_min_n = y
    return x_max_n, x_min_n, y_max_n, y_min_n


def rotate_strokes(doodle_strokes, angle=0.0):

    theta = np.deg2rad(angle)
    rot = np.array([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])

    x_max, x_min, y_max, y_min = max_min(doodle_strokes)
    x_c = (x_max + x_min)/2
    y_c = (y_max + y_min)/2

    new_strokes = []
    for doodle_stroke in doodle_strokes:
        new_stroke = []
        for stroke_position in doodle_stroke:
            x, y = stroke_position
            x = x - x_c
            y = y_c - y
            v = np.array([x, y])
            v2 = np.dot(rot, v)
            k = tuple(v2)
            x, y = k
            new_stroke_position = (x + x_c, y_c - y)
            new_stroke.append(new_stroke_position)
        new_strokes.append(new_stroke)
    x_max_n, x_min_n, y_max_n, y_min_n = max_min(new_strokes)
    new_strokes = translate_strokes(new_strokes, (x_min - x_min_n, y_min - y_min_n))
    return new_strokes


def modify_doodle():
    global modify_input, flag
    flag = 0
    prompt = "Press d to delete doodle, c to change colour, r to rotate doodle, s to scale doodle"
    modify_input = notebook.textinput("Modify Doodle", prompt)
    if "d" in modify_input:
        notebook.onclick(delete_doodle)

    if "r" in modify_input:
        notebook.onclick(rotate_doodle)

    elif "s" in modify_input:
        notebook.onclick(scale_doodle)

    elif "c" in modify_input:
        notebook.onclick(colour_doodle)


def req_pencil(coordinates):
    """
    Gets the pencil turtle which drew the doodle at those 'coordinates'.
    :param coordinates: Tuple (x, y).
    :return: The pencil turtle.
    """
    x, y = coordinates
    x = round(x)
    y = round(y)
    for pencil in doodle_area_dict:
        if (x, y) in doodle_area_dict[pencil]:
            return pencil


def delete_doodle(x, y, pencil=None):
    print("del")
    global border
    if pencil is None:
        pencil = req_pencil((x, y))
    if pencil is not None:
        for i in drawing_dict:
            if drawing_dict[i][0] == pencil:
                border = drawing_dict[i][1]
                break
        pencil.clear()
        border.clear()
        if flag == 0:
            del doodle_area_dict[pencil]
            del turtle_stroke_dict[pencil]
        notebook.onclick(spawn_pencil)


def rotate_doodle(x, y):
    print("rot")
    global border, a1, modify_input, flag
    pencil = req_pencil((x, y))
    print(pencil)
    if pencil is not None:
        if flag == 0:
            a1 = turtle_stroke_dict[pencil]
        if "s" in modify_input:
            flag = 1
        elif "c" in modify_input:
            flag = 1
        delete_doodle(x, y, pencil=pencil)
        angle = notebook.numinput("Rotation angle", "Enter the angle", default=0, minval=0, maxval=360)

        a1 = rotate_strokes(a1, angle)
        if "s" in modify_input:
            flag = 1
            scale_doodle(x, y)
        elif "c" in modify_input:
            flag = 1
            colour_doodle(x, y)
        else:
            for i in drawing_dict:
                if drawing_dict[i][0] == pencil:
                    border = drawing_dict[i][1]
                    break
            draw((pencil, border), x, y, doodle_strokes=a1)
    else:
        notebook.onclick(spawn_pencil)


def scale_doodle(x, y):
    print("scal")
    global border, a1, modify_input, flag
    pencil = req_pencil((x, y))
    print(pencil)
    if pencil is not None:
        if flag == 0:
            a1 = turtle_stroke_dict.get(pencil)
        if "c" in modify_input:
            flag = 1
        delete_doodle(x, y, pencil=pencil)
        factor = notebook.numinput("Scaling factor", "Enter the scaling factor", default=1, minval=0.1, maxval=5)
        a1 = scale_strokes(a1, factor)
        if "c" in modify_input:
            flag = 1
            colour_doodle(x, y)
        else:
            print("scal2")
            for i in drawing_dict:
                if drawing_dict[i][0] == pencil:
                    border = drawing_dict[i][1]
                    break
            print("scal3")
            draw((pencil, border), x, y, doodle_strokes=a1)


def colour_doodle(x, y):
    global border, a1
    pencil = req_pencil((x, y))
    if pencil is not None:
        if flag == 0:
            a1 = turtle_stroke_dict[pencil]
        delete_doodle(x, y, pencil=pencil)
        colour = notebook.textinput("Colour for the doodle", "Enter the the colour for doodle strokes "
                                                             "and doodle background, seperated by space, in rgb format")
        stroke_colour, fill_colour = colour.split(" ")
        r1, g1, b1 = (stroke_colour.strip("()")).split(",")
        r1 = int(r1)
        g1 = int(g1)
        b1 = int(b1)
        r2, g2, b2 = (fill_colour.strip("()")).split(",")
        r2 = int(r2)
        g2 = int(g2)
        b2 = int(b2)
        for i in drawing_dict:
            if drawing_dict[i][0] == pencil:
                border = drawing_dict[i][1]
                break
        draw((pencil, border), x, y, doodle_strokes=a1, stroke_colour=(r1, g1, b1), fill_colour=(r2, g2, b2))


def make_border_strokes(border_turtle, doodle_strokes, coordinates, border_colour, doodle_bg_colour):
    x, y = coordinates
    x_max, x_min, y_max, y_min = max_min(doodle_strokes)
    border_turtle.penup()
    border_turtle.goto(x + x_min, y + y_min)
    border_turtle.pendown()
    border_turtle.color(border_colour)
    border_turtle.fillcolor(doodle_bg_colour)
    border_turtle.begin_fill()
    for i in range(2):
        border_turtle.fd(x_max)
        border_turtle.left(90)
        border_turtle.fd(y_max)
        border_turtle.left(90)
    border_turtle.end_fill()


def make_doodle_strokes(pencil_turtle, doodle_strokes, coordinates, doodle_colour):
    x, y = coordinates
    pencil_turtle.color(doodle_colour)
    t_doodle_strokes = translate_strokes(doodle_strokes, (x, y))
    for doodle_stroke in t_doodle_strokes:
        pencil_turtle.penup()
        pencil_turtle.goto(doodle_stroke[0])
        pencil_turtle.pendown()
        for doodle_pos in doodle_stroke:
            pencil_turtle.goto(doodle_pos)

    notebook.onkeypress(modify_doodle, "m")
    notebook.listen()


def turtle_setting(pencil1, pencil2):
    pencil2.pensize(3)
    pencil1.pensize(3)
    pencil1.speed(10)
    pencil2.speed(10)
    pencil1.hideturtle()
    pencil2.hideturtle()
    return pencil1, pencil2


def draw(pencil_border, x, y, stroke_colour=(102, 252, 241), fill_colour=(31, 40, 51), doodle_strokes=None):
    """
    Calls both make_border_strokes and make_doodle_strokes functions to draw the doodle.
    :param pencil_border: The pencil turtle, which will draw the doodle.
    :param x: The x coordinate where the user clicked on the screen.
    :param y: The y coordinate where the user clicked on the screen.
    :param stroke_colour: The colour of the doodle strokes. Defaults to black
    :param fill_colour: The background colour of the doodle. Defaults to white.
    :param doodle_strokes: Defaults to None.
    """
    global a1
    pencil_turtle, border_turtle = pencil_border
    pencil_turtle, border_turtle = turtle_setting(pencil_turtle, border_turtle)
    if doodle_strokes is None:
        a1 = choose_doodle()
    update_area(pencil_turtle, a1, (x, y))
    turtle_stroke_dict[pencil_turtle] = a1
    print(turtle_stroke_dict)
    make_border_strokes(border_turtle, a1, (x, y), "white", fill_colour)
    make_doodle_strokes(pencil_turtle, a1, (x, y), stroke_colour)

    notebook.onclick(spawn_pencil)


def spawn_pencil(x, y):
    """
    Updates the drawing_dict and create turtle objects on click
    :param x: The x coordinate of the canvas, where user clicked
    :param y: The y coordinate of the canvas, where user clicked
    """
    global pencil_counter
    global notebook
    global drawing_dict
    pencil_counter = pencil_counter + 1
    drawing_dict[pencil_counter] = (turtle.Turtle(), turtle.Turtle())
    draw(drawing_dict[pencil_counter], x, y)


def main():
    """
    Starting point of the program, calls the spawn_pencil function
    """
    notebook.onclick(spawn_pencil)

    turtle.done()


if __name__ == "__main__":
    main()
