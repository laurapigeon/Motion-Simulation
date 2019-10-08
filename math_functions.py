import os, sys, math, time, copy, pygame, random, colorsys

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

def to_scale(x, y, screen_vals, point=False):
    scale = screen_vals["scale"].value
    if point:
        x, y = sub_vector(*dot_product(*screen_pixel, 1/2), x, y)
    x, y = dot_product(x, -1*y, 1/scale)
    if point:
        pan_x, pan_y = screen_vals["pan_x"].value, screen_vals["pan_y"].value
        x, y = sub_vector(pan_x, pan_y, x, y)
    return x, y

def to_pixel(x, y, screen_vals, point=False):
    scale = screen_vals["scale"].value
    if point:
        pan_x, pan_y = screen_vals["pan_x"].value, screen_vals["pan_y"].value
        x, y = sum_vector(pan_x, pan_y, x, y)
    x, y = dot_product(x, -1*y, scale)
    if point:
        x, y = mechanical.sum_vector(*dot_product(*screen_pixel, 1/2), x, y)
    return x, y

def list_round(x, y, digits=0):
    if not digits:
        return int(x), int(y)
    else:
        return round(x, digits), round(y, digits)

def list_abs(x, y):
    return  abs(x), abs(y)

def sigmoid(x):
    return 1 / (1 + math.exp(-x))
