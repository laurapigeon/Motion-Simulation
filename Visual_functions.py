import os, sys, math, time, copy, pygame, random, colorsys
import math_functions as mechanical

def draw_text(text, coords, corner="topleft",
              colour=(164, 164, 255), font=pygame.font.Font("freesansbold.ttf", 15)):
    text_surface = font.render(text, True, colour)
    text_rectangle = text_surface.get_rect()
    text_rectangle.__setattr__(corner, coords)
    globals()["screen"].blit(text_surface, text_rectangle)

def resolution():
    draw_text("({}, {})".format(*mechanical.list_round(*globals()["screen_pixel"], 2)),
              (globals()["screen_pixel"][0], 0), "topright")

    draw_text("({}m, {}m)".format(*mechanical.list_round(*globals()["screen_scale"], 2)),
              (globals()["screen_pixel"][0], 20), "topright")

def time():
    draw_text("t = {}{}".format(round(globals()["t"], 2), "s"), (0, 0), "topleft")

def particle_count():
    draw_text("{} projectiles".format(len(globals()["particles"])+len(globals()["i_particles"])), (0, 20), "topleft")

def mouse_pos(mouse_scale, mouse_pixel, screen_scale):
    num_value = mechanical.list_round(mouse_scale[0], mouse_scale[1] + screen_scale[1], 2)
    coords = (mouse_pixel[0], mouse_pixel[1] + 10)
    draw_text("({}m, {}m)".format(*num_value), coords, "midtop")

def pause():
    for i in range(2):
        pygame.draw.line(globals()["screen"], (164, 164, 255),
                         (10*(i+1), globals()["screen_pixel"][1] - 30),
                         (10*(i+1), globals()["screen_pixel"][1] - 10), 5)

def blank():
    globals()["screen"].fill((0, 0, 0))
