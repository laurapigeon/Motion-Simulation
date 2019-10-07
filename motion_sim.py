import os, sys, math, time, copy, pygame, random, colorsys

pygame.init()
pygame.font.init()

from particle_class import Particle
from modifier_class import Modifier
import math_functions as mechanical
import visual_functions as visual

pygame.display.set_caption("Us Simulation")
screen_pixel = (1600, 900)
screen = pygame.display.set_mode((screen_pixel[0], screen_pixel[1]), pygame.RESIZABLE)
fullscreen = False

clock = pygame.time.Clock()
tick = 120


def check_inputs():
    mouse_pixel = pygame.mouse.get_pos()
    mouse_scale = mechanical.to_scale(*mouse_pixel, True)

    #pygame.key.get_pressed()
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:

                if shifting:
                    for i, name in enumerate(values):
                        value = values[name]
                        value[1] = (64, 0, 0, 1, 0, 270, 1, 1, 0, 1, 0.1, 0, 0, 0)[i]
                    val_mode = 0
                else:
                    done = True

            if event.key == pygame.K_p:
                playing = not playing

            if event.key == pygame.K_c:
                cing = True

            if event.key == pygame.K_v:
                ving = True

            if event.key == pygame.K_f:
                if fullscreen:
                    screen = pygame.display.set_mode((screen_pixel[0], screen_pixel[1]), pygame.RESIZABLE)
                else:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                fullscreen = not fullscreen

            if event.unicode in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
                if cing:
                    save = copy.deepcopy((particles, i_particles, values, t, playing))
                    saves[int(event.unicode)] = save

                elif ving:
                    if saves[int(event.unicode)]:
                        save = copy.deepcopy(saves)[int(event.unicode)]
                        particles, i_particles, values, t, playing = save

            if event.key == pygame.K_LSHIFT:
                shifting = True

            if event.key == pygame.K_LCTRL:
                ctrling  = True

            if event.key == pygame.K_DOWN:
                val_mode = mechanical.bump(val_mode, 1, "mod", "inc", [0, len(values) - 1])
                val_name = val_order[val_mode]
            elif event.key == pygame.K_UP:
                val_mode = mechanical.bump(val_mode, 1, "mod", "dec", [0, len(values) - 1])
                val_name = val_order[val_mode]

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
                if shifting:
                    for particle in particles[::-1]:
                        if not particle.get_visible():
                            particles.remove(particle)

                elif ctrling:
                    i_particles = []
                    particles = []
                    t = 0

                else:
                    for particle in particles[::-1]:
                        if not particle.fixed:
                            particles.remove(particle)

            elif event.key == pygame.K_BACKSPACE:
                if shifting:
                    if particles:
                        del particles[0]
                    elif i_particles:
                        del i_particles[0]

                else:
                    if i_particles:
                        del i_particles[-1]
                    elif particles:
                        del particles[-1]

            if event.key == pygame.K_LEFT:
                multiplier = [64, 1]


        if event.type == pygame.KEYUP:

            if event.key == pygame.K_c:
                cing = False
            if event.key == pygame.K_v:
                ving = False
            if event.key == pygame.K_LSHIFT:
                shifting = False
            if event.key == pygame.K_LCTRL:
                ctrling  = False


        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button in (1, 3):
                particle_values = (values["charge"][1], 
                                   values["mass"][1], 
                                   values["radius"][1])

                if i_particles == []:
                    if event.button == 1:
                        i_particles.append(particle(*mouse_scale,
                                                        *particle_values,
                                                        fixed=False))
                    elif event.button == 3:
                        fixed_particle = particle(*mouse_scale,
                                                      *particle_values,
                                                      fixed=True)

                        fixed_particle.initiate(1, *mouse_scale)
                        particles.append(fixed_particle)

                else:
                    if shifting:
                        if event.button == 1:
                            i_particles.append(particle(*mouse_scale,
                                                            *particle_values,
                                                            fixed=False))
                        elif event.button == 3:
                            fixed_particle = particle(*mouse_scale,
                                                          *particle_values,
                                                          fixed=True)

                            fixed_particle.initiate(1, *mouse_scale)
                            particles.append(fixed_particle)

                    else:
                        for i_particle in i_particles:
                            i_particle.initiate(1, *mouse_scale)
                            particles.append(i_particle)
                        i_particles = []


            if event.button in (4, 5):
                value = values[val_name]
                magnitude = 1

                if shifting:
                    magnitude -= 1
                if ctrling:
                    magnitude += 1

                inc_type = ("inc", "dec")[event.button == 5]
                amount = (value[3], value[4], value[5])[magnitude]

                values[val_name][1] = mechanical.bump(value[1], amount, value[2], inc_type, value[6])

                if val_mode == 0:
                    screen_scale = mechanical.to_scale(screen_pixel[0], -1 * screen_pixel[1])


        if event.type == pygame.VIDEORESIZE:
            screen_pixel = (event.w, event.h)
            screen_scale = mechanical.to_scale(screen_pixel[0], -1 * screen_pixel[1])
            screen = pygame.display.set_mode((screen_pixel[0], screen_pixel[1]), pygame.RESIZABLE)


def update_particles(tick):
    for particle in particles[::-1]:
        particle.earth()

    for x, particle in enumerate(particles):
        if not particle.fixed:
            for prokectile in particles:
                if particle != prokectile:

                    dx, dy = mechanical.sub_vector(particle.P_xs, particle.P_ys, 
                                                prokectile.P_xs, prokectile.P_ys)
                    r, θ = mechanical.combine(dx, dy)

                    if r == 0:
                        r = 0.001

                    if values["G"][1]:
                        F = mechanical.law_force(values["G"][1], r,
                                                particle.m, prokectile.m)
                        particle.apply_force(F, θ)

                    if values["k_e"][1]:
                        F = mechanical.law_force(values["k_e"][1], r,
                                                particle.Q, prokectile.Q)
                        particle.apply_force(-F, θ)

    for particle in particles[::-1]:
        particle.update(tick)


def update_canvas():
    for i_particle in i_particles:
        if not i_particle.fixed:

            i_particle.draw_vector(dt=1, mouse=True)

            if values["vis_vectors"][1] >= 2:
                i_particle.label_vector(mouse=True)

        i_particle.draw_mass()

        if values["vis_values"][1] >= 1:
            i_particle.label_values(values["vis_values"][1])


    for particle in particles:

        if not particle.fixed:

            if values["vis_vectors"][1] >= 1:
                particle.draw_vector(1)

            if values["vis_vectors"][1] >= 2:
                particle.label_vector()

        particle.draw_mass()

        if values["vis_values"][1] >= 1:
            particle.label_values(values["vis_values"][1])

    if values["vis_values"][1] >= 1:
        visual.mouse_pos()


    visual.values()
    visual.resolution()
    visual.time()
    visual.particle_count()

    if not playing:
        visual.pause()


done = False
playing = True
cing = False
ving = False
shifting = False
ctrling = False
show_vectors = False
saves = [(), (), (), (), (), (), (), (), (), ()]

val_mode = 0
val_menu = 0

space = Modifier((64, "geo", (0.005, 0.05, 0.5), (None, None)), ("Screen scale", "px/m", 0))
pan_x = Modifier((0,  "lin", (0.1,   1,    10),  (None, None)), ("Screen X",     "m",    0))
pan_x = Modifier((0,  "lin", (0.1,   1,    10),  (None, None)), ("Screen Y",     "m",    0))
screen_values = {"space": space, "pan_x": pan_x, "pan_y": pan_y}

time_rate = Modifier((1,   "lin", (0.01, 0.1, 1),  (None, None)), ("Time rate",      "*t",      2))
field_r   = Modifier((0,   "lin", (0.01, 0.1, 1),  (None, None)), ("Field strength", "ms-2",    2))
field_θ   = Modifier((270, "mod", (1,    5,   30), (0,    359)),  ("Field angle",    "degrees", 0))
G_const   = Modifier((1,   "lin", (0.01, 0.1, 1),  (0,    None)), ("G",              "Nm2kg-2", 2))
k_e_const = Modifier((1,   "lin", (0.01, 0.1, 1),  (0,    None)), ("k_e",            "Nm2C-2",  2))
universals = {"time_rate": time_rate, "field_r": field_r, "field_θ": field_θ, "G_const": G_const, "k_e_const" k_e_const}

p_charge = Modifier((0,   "lin", (0.1,  1,   10), (None, None)), ("Q", "C",  1))
p_mass   = Modifier((1,   "geo", (0.01, 0.1, 1),  (None, None)), ("M", "kg", 2))
p_radius = Modifier((0.1, "geo", (0.01, 0.1, 1),  (None, None)), ("r", "m",  2))
particle_inits = {"p_charge": p_charge, "p_mass": p_mass, "p_radius": p_radius}

life        = Modifier((0, "lin", (0.1, 1, 10), (0, None)), ("particle life",   "m", 1))
vis_vectors = Modifier((0, "mod", (1,   1, 1),  (0, 3)),    ("Vector detail",   "",  0))
vis_values  = Modifier((0, "mod", (1,   1, 1),  (0, 4)),    ("Value detail",    "",  0))
preferences = {"life": life, "vis_vectors": vis_vectors, "vis_values": vis_values}

t = 0
g = -9.80665

screen_scale = mechanical.to_scale(screen_pixel[0], -1 * screen_pixel[1])

i_particles = list()
particles   = list()

while not done:
    check_inputs()

    if playing:
        update_particles(values["time"][1] / tick)
        t += values["time"][1] / tick

    update_canvas()

    clock.tick(tick)
    pygame.display.flip()
