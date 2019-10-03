import os, sys, math, time, copy, pygame, random, colorsys

pygame.init()
pygame.font.init()

from projectile_class import Projectile
import math_functions as mechanical
import visual_functions as visual

pygame.display.set_caption("Us Simulation")
screen_pixel = (1600, 900)
screen = pygame.display.set_mode((screen_pixel[0], screen_pixel[1]), pygame.RESIZABLE)
fullscreen = False

clock = pygame.time.Clock()
tick = 120


def tick(tick):
    for x, projectile in enumerate(projectiles):
        if not projectile.fixed:
            for prokectile in projectiles:
                if projectile != prokectile:

                    dx, dy = mechanical.sub_vector(projectile.P_xs, projectile.P_ys, 
                                                prokectile.P_xs, prokectile.P_ys)
                    r, θ = mechanical.combine(dx, dy)

                    if r == 0:
                        r = 0.001

                    if values["G"][1]:
                        F = mechanical.law_force(values["G"][1], r,
                                                projectile.m, prokectile.m)
                        projectile.apply_force(F, θ)

                    if values["k_e"][1]:
                        F = mechanical.law_force(values["k_e"][1], r,
                                                projectile.Q, prokectile.Q)
                        projectile.apply_force(-F, θ)

    for projectile in projectiles[::-1]:
        projectile.update(tick)


def to_canvas():
    for i_projectile in i_projectiles:
        if not i_projectile.fixed:

            i_projectile.draw_vector(dt=1, mouse=True)

            if values["vis_vectors"][1] >= 2:
                i_projectile.label_vector(mouse=True)

        i_projectile.draw_mass()

        if values["vis_values"][1] >= 1:
            i_projectile.label_values(values["vis_values"][1])


    for projectile in projectiles:

        if not projectile.fixed:

            if values["vis_vectors"][1] >= 1:
                projectile.draw_vector(1)

            if values["vis_vectors"][1] >= 2:
                projectile.label_vector()

        projectile.draw_mass()

        if values["vis_values"][1] >= 1:
            projectile.label_values(values["vis_values"][1])

    if values["vis_values"][1] >= 1:
        visual.mouse_pos()


    visual.values()
    visual.resolution()
    visual.time()
    visual.projectile_count()

    if not playing:
        visual.pause()


def change_modifier():
    


done = False
playing = True
cing = False
ving = False
shifting = False
ctrling = False
show_vectors = False
saves = [(), (), (), (), (), (), (), (), (), ()]

#            call            name        value        scaling [SML]        bounds        unit    dp menu
values = {"space":       ["Space",        64,  "geo", 0.005, 0.05, 0.5, [None, None], "px/m",     0, 0],
          "screenx":     ["Screen X",     0,   "lin", 0.1,   1,    10,  [None, None], "m",        0, 0],
          "screeny":     ["Screen Y",     0,   "lin", 0.1,   1,    10,  [None, None], "m",        0, 0],
          "time":        ["Time",         1,   "lin", 0.01,  0.1,  1,   [None, None], "*t",       2, 1],
          "gravity":     ["Gravity",      0,   "lin", 0.01,  0.1,  1,   [None, None], "*g",       2, 1],
          "angle":       ["Angle",        270, "mod", 1,     5,    30,  [0, 359],     "deg",      0, 1],
          "G":           ["G",            1,   "lin", 0.01,  0.1,  1,   [0, None],    "Nm^2kg-2", 2, 1],
          "k_e":         ["k_e",          1,   "lin", 0.01,  0.1,  1,   [0, None],    "Nm^2C-2",  2, 1],
          "life":        ["Life",         0,   "lin", 0.1,   1,    10,  [0, 120],     "s",        1, 2],
          "vis_vectors": ["Show vectors", 0,   "mod", 1,     1,    1,   [0, 3],       "",         0, 3],
          "vis_values":  ["Show values",  0,   "mod", 1,     1,    1,   [0, 4],       "",         0, 3]}

val_order = [a for a in values]
val_mode = 0
val_menu = 0
val_name = "space"

t = 0
g = -9.80665

screen_scale = mechanical.to_scale(screen_pixel[0], -1 * screen_pixel[1])

i_projectiles = list()
projectiles   = list()

while not done:

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
                    save = copy.deepcopy((projectiles, i_projectiles, values, t, playing))
                    saves[int(event.unicode)] = save

                elif ving:
                    if saves[int(event.unicode)]:
                        save = copy.deepcopy(saves)[int(event.unicode)]
                        projectiles, i_projectiles, values, t, playing = save

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
                    for projectile in projectiles[::-1]:
                        if not projectile.get_visible():
                            projectiles.remove(projectile)

                elif ctrling:
                    i_projectiles = []
                    projectiles = []
                    t = 0

                else:
                    for projectile in projectiles[::-1]:
                        if not projectile.fixed:
                            projectiles.remove(projectile)

            elif event.key == pygame.K_BACKSPACE:
                if shifting:
                    if projectiles:
                        del projectiles[0]
                    elif i_projectiles:
                        del i_projectiles[0]

                else:
                    if i_projectiles:
                        del i_projectiles[-1]
                    elif projectiles:
                        del projectiles[-1]

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
                projectile_values = (values["charge"][1], 
                                     values["mass"][1], 
                                     values["radius"][1])

                if i_projectiles == []:
                    if event.button == 1:
                        i_projectiles.append(Projectile(*mouse_scale,
                                                        *projectile_values,
                                                        fixed=False))
                    elif event.button == 3:
                        fixed_projectile = Projectile(*mouse_scale,
                                                      *projectile_values,
                                                      fixed=True)

                        fixed_projectile.initiate(1, *mouse_scale)
                        projectiles.append(fixed_projectile)

                else:
                    if shifting:
                        if event.button == 1:
                            i_projectiles.append(Projectile(*mouse_scale,
                                                            *projectile_values,
                                                            fixed=False))
                        elif event.button == 3:
                            fixed_projectile = Projectile(*mouse_scale,
                                                          *projectile_values,
                                                          fixed=True)

                            fixed_projectile.initiate(1, *mouse_scale)
                            projectiles.append(fixed_projectile)

                    else:
                        for i_projectile in i_projectiles:
                            i_projectile.initiate(1, *mouse_scale)
                            projectiles.append(i_projectile)
                        i_projectiles = []


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


    for projectile in projectiles[::-1]:
        projectile.earth()

    if playing:
        tick(values["time"][1] / tick)
        t += values["time"][1] / tick

    to_canvas()

    clock.tick(tick)
    pygame.display.flip()
