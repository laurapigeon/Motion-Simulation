#region IMPORTS/INITS
import os, sys, math, time, copy, pygame, random, colorsys

pygame.init()
pygame.font.init()

from Particle_class import Particle
from Modifier_class import Modifier
import math_functions as mechanical
import visual_functions as visual

pygame.display.set_caption("Us Simulation")
screen_pixel = (1600, 900)
screen = pygame.display.set_mode((screen_pixel[0], screen_pixel[1]), pygame.RESIZABLE)
fullscreen = False

clock = pygame.time.Clock()
tick = 120

done = False
playing = True
saves = [(), (), (), (), (), (), (), (), (), ()]

val_mode = 0
val_menu = 0

t = 0
g = -9.80665

screen_scale = mechanical.to_scale(screen_pixel[0], -1 * screen_pixel[1])

i_particles = list()
particles   = list()

#endregion


def check_inputs():
    keys = pygame.key.get_pressed()
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
                done = True


        if event.type == pygame.KEYDOWN:
                
            if event.key == pygame.K_ESCAPE:

                if keys[pygame.K_LSHIFT]:
                    for modifier_name in modifiers:
                        modifiers[modifier_name].default()
                    val_mode = 0
                else:
                    done = True

            if event.key == pygame.K_p:
                playing = not playing

            if event.key == pygame.K_f:
                    if fullscreen:
                        screen = pygame.display.set_mode((screen_pixel[0], screen_pixel[1]), pygame.RESIZABLE)
                    else:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    fullscreen = not fullscreen

            if event.unicode in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
                if keys[pygame.K_c]:
                    save = copy.deepcopy((particles, i_particles, modifiers, t, playing))
                    saves[int(event.unicode)] = save

                elif keys[pygame.K_v]:
                    if saves[int(event.unicode)]:
                        save = copy.deepcopy(saves)[int(event.unicode)]
                        particles, i_particles, modifiers, t, playing = save

            if event.key == pygame.K_DOWN:
                val_mode = mechanical.bump(val_mode, 1, "mod", "inc", [0, len(modifiers) - 1])

            elif event.key == pygame.K_UP:
                val_mode = mechanical.bump(val_mode, 1, "mod", "dec", [0, len(modifiers) - 1])

            if event.key == pygame.K_RIGHT:
                val_menu = mechanical.bump(val_menu, 1, "mod", "inc", [0, 2])

            elif event.key == pygame.K_LEFT:
                val_menu = mechanical.bump(val_menu, 1, "mod", "dec", [0, 2])

            if event.key == pygame.K_PERIOD:
                t += 1 / tick
                mechanical.tick(1 / tick)

            elif event.key == pygame.K_COMMA:
                t -= 1 / tick
                mechanical.tick(-1 / tick)

            if event.key == pygame.K_DELETE:
                if keys[pygame.K_LSHIFT]:
                    for particle in particles[::-1]:
                        if not particle.get_visible(*screen.values()):
                            particles.remove(particle)

                elif keys[pygame.K_LCTRL]:
                    i_particles = []
                    particles = []
                    t = 0

                else:
                    for particle in particles[::-1]:
                        if not particle.fixed:
                            particles.remove(particle)

            elif event.key == pygame.K_BACKSPACE:
                if keys[pygame.K_LSHIFT]:
                    if particles:
                        del particles[0]
                    elif i_particles:
                        del i_particles[0]

                else:
                    if i_particles:
                        del i_particles[-1]
                    elif particles:
                        del particles[-1]


        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button in (1, 3):
                if i_particles == []:
                    if event.button == 1:
                        i_particles.append(Particle(*mouse_scale,
                                                    *particle_inits,
                                                    fixed=False))
                    elif event.button == 3:
                        fixed_particle = Particle(*mouse_scale,
                                                  *particle_inits,
                                                  fixed=True)

                        fixed_particle.initiate(1, *mouse_scale)
                        particles.append(fixed_particle)

                else:
                    if keys[pygame.K_LSHIFT]:
                        if event.button == 1:
                            i_particles.append(Particle(*mouse_scale,
                                                        *particle_inits,
                                                        fixed=False))
                        elif event.button == 3:
                            fixed_particle = Particle(*mouse_scale,
                                                      *particle_inits,
                                                      fixed=True)

                            fixed_particle.initiate(1, *mouse_scale)
                            particles.append(fixed_particle)

                    else:
                        for i_particle in i_particles:
                            i_particle.initiate(1, *mouse_scale)
                            particles.append(i_particle)
                        i_particles = []

            if event.button in (4, 5):
                modifier = modifiers.values[val_mode]
                magnitude = 1

                if keys[pygame.K_LSHIFT]:
                    magnitude -= 1
                if keys[pygame.K_LCTRL]:
                    magnitude += 1

                bump_type = ("inc", "dec")[event.button == 5]
                amount = modifier.scaling["amount"]

                modifier.value = modifier.bump(bump_type, magnitude)

                if val_mode == 0:
                    screen_scale = mechanical.to_scale(screen_pixel[0], -1 * screen_pixel[1])


        if event.type == pygame.VIDEORESIZE:
            screen_pixel = (event.w, event.h)
            screen_scale = mechanical.to_scale(screen_pixel[0], -1 * screen_pixel[1])
            screen = pygame.display.set_mode((screen_pixel[0], screen_pixel[1]), pygame.RESIZABLE)


def update_particles(tick, universals):
    for particle in particles[::-1]:
        particle.earth(universals["field_r"].value, universals["field_θ"].value)

    for x, particle in enumerate(particles):
        if not particle.fixed:
            for qarticle in particles:
                if particle != qarticle:

                    dx, dy = mechanical.sub_vector(particle.P_xs, particle.P_ys, 
                                                   qarticle.P_xs, qarticle.P_ys)
                    r, θ = mechanical.combine(dx, dy)

                    if r == 0:
                        r = 0.001

                    if universals["G_const"].value:
                        F = mechanical.law_force(universals["G_const"].value, r,
                                                 particle.m, qarticle.m)
                        particle.apply_force(F, θ)

                    if universals["k_e_const"].value:
                        F = mechanical.law_force(universals["k_e_const"].value, r,
                                                 particle.Q, qarticle.Q)
                        particle.apply_force(-F, θ)

    for particle in particles[::-1]:
        particle.update(tick, screen, preferences["life"].value, screen_vals)


def update_canvas(vis_vectors, vis_values):
    for i_particle in i_particles:
        if not i_particle.fixed:

            i_particle.draw_vector(dt=1, mouse=True)

            if vis_vectors >= 2:
                i_particle.label_vector(mouse=True)

        i_particle.draw_mass()

        if vis_values >= 1:
            i_particle.label_values(vis_values)


    for particle in particles:

        if not particle.fixed:

            if vis_vectors >= 1:
                particle.draw_vector(1)

            if vis_vectors >= 2:
                particle.label_vector()

        particle.draw_mass()

        if vis_values >= 1:
            particle.label_values(vis_values)

    if vis_values >= 1:
        visual.mouse_pos(mouse_scale, mouse_pixel, screen_scale)


    height = 20 * len(modifiers)
    for i, modifier in enumerate(modifiers.values()):
        marked = i == val_mode
        modifier.display(screen_pixel[0], screen_pixel[1]-height, marked=marked)
        height -= 20

    visual.resolution(screen_pixel)
    visual.time(t)
    visual.particle_count(particles, i_particles)

    if not playing:
        visual.pause(screen_pixel)


#region MODIFIER DEFINITIONS
scale = Modifier((64, "geo", (0.005, 0.05, 0.5), (None, None)), ("Screen scale", "px/m", 0))
pan_x = Modifier((0,  "lin", (0.1,   1,    10),  (None, None)), ("Screen X",     "m",    0))
pan_y = Modifier((0,  "lin", (0.1,   1,    10),  (None, None)), ("Screen Y",     "m",    0))
screen_vals = {"scale": scale, "pan_x": pan_x, "pan_y": pan_y}

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

modifiers = {**screen, **universals, **particle_inits, **preferences}

#endregion


while not done: #PROGRAM LOOP
    check_inputs()

    if playing:
        update_particles(universals["time_rate"][1] / tick, universals)
        t += universals["time_rate"][1] / tick

    update_canvas(*preferences)

    clock.tick(tick)
    pygame.display.flip()
