import os, sys, math, time, copy, pygame, random, colorsys

from Modifier_class import Modifier
import math_functions as mechanical


pygame.display.set_caption("Simulation")
screen_pixel = (1600, 900)
screen = pygame.display.set_mode(screen_pixel, pygame.RESIZABLE)
fullscreen = False

clock = pygame.time.Clock()
tick = 120

#region MODIFIER DEFINITIONS
zoom  = Modifier((64, "geo", (0.005, 0.05, 0.5), (None, None)), ("Screen zoom",  "px/m", 0))
pan_x = Modifier((0,  "lin", (0.1,   1,    10),  (None, None)), ("Screen X",     "m",    0))
pan_y = Modifier((0,  "lin", (0.1,   1,    10),  (None, None)), ("Screen Y",     "m",    0))
screen_mods = {"zoom": zoom, "pan_x": pan_x, "pan_y": pan_y}

time_rate = Modifier((1,   "lin", (0.01, 0.1, 1),  (None, None)), ("Time rate",      "*t",      2))
field_r   = Modifier((0,   "lin", (0.01, 0.1, 1),  (None, None)), ("Field strength", "ms-2",    2))
field_θ   = Modifier((270, "mod", (1,    5,   30), (0,    359)),  ("Field angle",    "degrees", 0))
G_const   = Modifier((1,   "lin", (0.01, 0.1, 1),  (0,    None)), ("G",              "Nm2kg-2", 2))
k_e_const = Modifier((1,   "lin", (0.01, 0.1, 1),  (0,    None)), ("k_e",            "Nm2C-2",  2))
life      = Modifier((0,   "lin", (0.1,  1,   10), (0,    None)), ("particle life",  "m",       1))
universals = {"time_rate": time_rate, "field_r": field_r, "field_θ": field_θ,
            "G_const": G_const, "k_e_const": k_e_const, "life": life}

p_charge = Modifier((0,   "lin", (0.1,  1,   10), (None, None)), ("Q", "C",  1))
p_mass   = Modifier((1,   "geo", (0.01, 0.1, 1),  (None, None)), ("M", "kg", 2))
p_radius = Modifier((0.1, "geo", (0.01, 0.1, 1),  (None, None)), ("r", "m",  2))
particle_inits = {"p_charge": p_charge, "p_mass": p_mass, "p_radius": p_radius}

vis_vectors = Modifier((0, "mod", (1, 1, 1), (0, 3)), ("Vector detail", "", 0))
vis_values  = Modifier((0, "mod", (1, 1, 1), (0, 4)), ("Value detail",  "", 0))
preferences = {"vis_vectors": vis_vectors, "vis_values": vis_values}

modifiers = {**screen_mods, **universals, **particle_inits, **preferences}
mod_groups = (screen_mods, universals, particle_inits, preferences)

mod_menu = Modifier((0, "mod", (1, 1, 1), [0, len(mod_groups)-1]), ("", "", 0))
mod_group = mod_groups[mod_menu.value]
mod_mode = Modifier((0, "mod", (1, 1, 1), [0, len(mod_group)-1]), ("", "", 0))
#endregion

screen_scale = mechanical.to_scale(*screen_pixel)

mouse_pixel = pygame.mouse.get_pos()
mouse_scale = mechanical.to_scale(*mouse_pixel, point=True)

playing = True
saves = [(), (), (), (), (), (), (), (), (), ()]
t = 0

i_particles = list()
particles = list()
