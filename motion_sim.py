#region IMPORTS/INITS
import os, sys, math, time, copy, pygame, random, colorsys

import config
from Particle_class import Particle
from Modifier_class import Modifier
import math_functions as mechanical
import visual_functions as visual

config.init()
#endregion


def check_inputs():
    global i_particles, particles
    global screen_vals
    global t, tick

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
                        config.screen = pygame.display.set_mode(config.screen_pixel, pygame.RESIZABLE)
                    else:
                        config.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
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
                        if not particle.get_visible():
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
                pos    = config.mouse_scale
                charge = config.particle_inits["charge"].value
                mass   = config.particle_inits["mass"].value
                radius = config.particle_inits["radius"].value

                if i_particles == []:
                    if event.button == 1:
                        i_particles.append(Particle(*pos, charge, mass, radius, fixed=False))
                    elif event.button == 3:
                        fixed_particle = Particle(*pos, charge, mass, radius, fixed=True)

                        fixed_particle.initiate(1, *pos)
                        particles.append(fixed_particle)

                else:
                    if keys[pygame.K_LSHIFT]:
                        if event.button == 1:
                            i_particles.append(Particle(*pos, charge, mass, radius, fixed=False))
                        elif event.button == 3:
                            fixed_particle = Particle(*pos, charge, mass, radius, fixed=True)

                            fixed_particle.initiate(1, *pos)
                            particles.append(fixed_particle)

                    else:
                        for i_particle in i_particles:
                            i_particle.initiate(1, *pos)
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

                modifier.bump(bump_type, magnitude)

                if modifier.name == "Screen zoom":
                    config.screen_scale = mechanical.to_scale(*screen_pixel)
                    #MUST UPDATE SCREEN SCALE FOR GLOBALS WHEN SCREEN ZOOM CHANGES

                if modifier.name in ("Screen zoom", "Screen X", "Screen Y"):
                    config.mouse_scale = mechanical.to_scale(*mouse_pixel, point=True)
                    #MUST UPDATE MOUSE SCALE FOR GLOBALS WHEN SCREEN ZOOM OR PAN CHANGES


        if event.type == pygame.VIDEORESIZE:
            screen_pixel = (event.w, event.h)
            config.screen_scale = mechanical.to_scale(*screen_pixel)
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)


        if event.type == pygame.MOUSEMOTION:
            mouse_pixel = pygame.mouse.get_pos()
            config.screen_scale = mechanical.to_scale(*mouse_pixel, point=True)


def update_particles(dt):
    global mouse_pixel
    global i_particles, particles
    global universals

    for particle in particles[::-1]:
        particle.earth()

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
        particle.update(dt, screen)


def update_canvas():
    global screen, screen_pixel, mouse_pixel   
    global i_particles, particles
    global preferences

    vis_vectors, vis_values = preferences["vis_vectors"].value, preferences["vis_values"].value

    visual.blank(screen)

    for i_particle in i_particles:
        if not i_particle.fixed:

            i_particle.draw_vector(dt=1, mouse=True)

            if vis_vectors >= 2:
                i_particle.label_vector(mouse=True)

        i_particle.draw_mass()

        if vis_values >= 1:
            i_particle.label_values(screen, vis_values)


    for particle in particles:

        if not particle.fixed:

            if vis_vectors >= 1:
                particle.draw_vector(dt=1)

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

    visual.resolution()
    visual.time()
    visual.particle_count()

    if not playing:
        visual.pause()


done = False
while not done: #PROGRAM LOOP
    check_inputs()

    if playing:
        update_particles(universals["time_rate"].value / tick)
        t += universals["time_rate"].value / tick

    update_canvas()

    clock.tick(tick)
    pygame.display.flip()
