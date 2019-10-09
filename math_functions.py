import os, sys, math, time, copy, pygame, random, colorsys

import config

def resolve(v, θ):
    x = v * math.cos(θ)
    y = v * math.sin(θ)
    return x, y

def combine(x, y):
    v = math.hypot(x, y)
    θ = math.atan2(y, x)
    return v, θ


def sum_vector(x_1, y_1, x_2, y_2):
    return x_1 + x_2, y_1 + y_2

def sub_vector(x_1, y_1, x_2, y_2):
    return x_2 - x_1, y_2 - y_1

def dot_product(x, y, k):
    return x*k, y*k

def midpoint(x_1, y_1, x_2, y_2):
    s_x, s_y = sum_vector(x_1, y_1, x_2, y_2)
    return dot_product(s_x, s_y, 1/2)

def law_force(k, r, s_1, s_2):
    return k*s_1*s_2 / r**2

def list_abs(x, y):
    return abs(x), abs(y)

def list_round(x, y, digits=0):
    if not digits:
        return int(x), int(y)
    else:
        return round(x, digits), round(y, digits)

def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def to_scale(x, y, point=False):
    if point:
        x, y = sub_vector(*dot_product(*config.screen_pixel, 1/2), x, y)

    x, y = dot_product(x, -1*y, 1/config.screen_mods["zoom"].value)

    if point:
        pan_x, pan_y = config.screen_mods["pan_x"].value, config.screen_mods["pan_y"].value
        x, y = sub_vector(pan_x, pan_y, x, y)

    return x, y

def to_pixel(x, y, point=False):
    if point:
        pan_x, pan_y = config.screen_mods["pan_x"].value, config.screen_mods["pan_y"].value
        x, y = sum_vector(pan_x, pan_y, x, y)

    x, y = dot_product(x, -1*y, config.screen_mods["zoom"].value)

    if point:
        x, y = sum_vector(*dot_product(*config.screen_pixel, 1/2), x, y)

    return x, y
