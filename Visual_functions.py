import os, sys, math, time, copy, pygame, random, colorsys
import math_functions as mechanical

def draw_text(text, coords, corner="topleft",
              colour=(164, 164, 255), font=pygame.font.Font("freesansbold.ttf", 15)):
    text_surface = font.render(text, True, colour)
    text_rectangle = text_surface.get_rect()
    text_rectangle.__setattr__(corner, coords)
    screen.blit(text_surface, text_rectangle)

def resolution(screen_pixel, screen_scale):
    visual.draw_text("({}, {})".format(*mechanical.list_round(*screen_pixel, 2)),
                     (screen_pixel[0], 0), "topright")

    visual.draw_text("({}m, {}m)".format(*mechanical.list_round(*screen_scale, 2)),
                     (screen_pixel[0], 20), "topright")

def time(t):
    visual.draw_text("t = {}{}".format(round(t, 2), "s"), (0, 0), "topleft")

def particle_count(particles, i_particles):
    visual.draw_text("{} projectiles".format(len(particles)+len(i_particles)), (0, 20), "topleft")

def mouse_pos(mouse_scale, mouse_pixel, screen_scale):
    num_value = mechanical.list_round(mouse_scale[0], mouse_scale[1] + screen_scale[1], 2)
    coords = (mouse_pixel[0], mouse_pixel[1] + 10)
    visual.draw_text("({}m, {}m)".format(*num_value), coords, "midtop")

def pause(screen_pixel):
    for i in range(2):
        pygame.draw.line(screen, (164, 164, 255),
                            (10*(i+1), screen_pixel[1] - 30),
                            (10*(i+1), screen_pixel[1] - 10), 5)

def to_canvas():
    screen.fill((0, 0, 0))
