#region IMPORTS/INITS
import os, sys, math, time, copy, pygame, random, colorsys

import config
from Particle_class import Particle
from Modifier_class import Modifier
import math_functions as mechanical
import visual_functions as visual

pygame.init()

#endregion


def check_inputs():
    global done

    keys = pygame.key.get_pressed()
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            done = True


        if event.type == pygame.KEYDOWN:
                
            if event.key == pygame.K_ESCAPE:

                if keys[pygame.K_LSHIFT]:
                    for modifier in mod_group.values():
                        modifier.default()
                    config.mod_mode = 0
                else:
                    done = True

            if event.key == pygame.K_p:
                playing = not playing

            if event.key == pygame.K_f:
                    if config.fullscreen:
                        config.screen = pygame.display.set_mode(config.screen_pixel, pygame.RESIZABLE)
                    else:
                        config.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    config.fullscreen = not config.fullscreen

            if event.unicode in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
                if keys[pygame.K_c]:
                    save = copy.deepcopy((config.particles, config.i_particles, modifiers, t, playing))
                    saves[int(event.unicode)] = save

                elif keys[pygame.K_v]:
                    if saves[int(event.unicode)]:
                        save = copy.deepcopy(saves)[int(event.unicode)]
                        config.particles, config.i_particles, modifiers, t, playing = save

            if event.key == pygame.K_DOWN:
                config.mod_mode.bump("inc", 1)

            elif event.key == pygame.K_UP:
                config.mod_mode.bump("dec", 1)

            if event.key == pygame.K_RIGHT:
                config.mod_menu.bump("inc", 1)
                config.mod_group = config.mod_groups[config.mod_menu.value]
                config.mod_mode.value = 0
                config.mod_mode.scaling["bounds"][1] = len(config.mod_group)-1

            elif event.key == pygame.K_LEFT:
                config.mod_menu.bump("dec", 1)
                config.mod_group = config.mod_groups[config.mod_menu.value]
                config.mod_mode.value = 0
                config.mod_mode.scaling["bounds"][1] = len(config.mod_group)-1

            if event.key == pygame.K_PERIOD:
                t += 1 / tick
                mechanical.tick(1 / tick)

            elif event.key == pygame.K_COMMA:
                t -= 1 / tick
                mechanical.tick(-1 / tick)

            if event.key == pygame.K_DELETE:
                if keys[pygame.K_LSHIFT]:
                    for particle in config.particles[::-1]:
                        if not particle.get_visible():
                            config.particles.remove(particle)

                elif keys[pygame.K_LCTRL]:
                    config.i_particles = list()
                    config.particles = list()
                    config.t = 0

                else:
                    for particle in config.particles[::-1]:
                        if not particle.fixed:
                            config.particles.remove(particle)

            elif event.key == pygame.K_BACKSPACE:
                index = -1
                if keys[pygame.K_LSHIFT]:
                    index += 1
                if config.i_particles:
                    del config.i_particles[index]
                elif config.particles:
                    del config.particles[index]


        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button in (1, 3):
                pos    = config.mouse_scale
                charge = config.particle_inits["p_charge"].value
                mass   = config.particle_inits["p_mass"].value
                radius = config.particle_inits["p_radius"].value

                if config.i_particles == []:
                    if event.button == 1:
                        config.i_particles.append(Particle(*pos, charge, mass, radius, fixed=False))
                    elif event.button == 3:
                        fixed_particle = Particle(*pos, charge, mass, radius, fixed=True)

                        fixed_particle.initiate(1, *pos)
                        config.particles.append(fixed_particle)

                else:
                    if keys[pygame.K_LSHIFT]:
                        if event.button == 1:
                            config.i_particles.append(Particle(*pos, charge, mass, radius, fixed=False))
                        elif event.button == 3:
                            fixed_particle = Particle(*pos, charge, mass, radius, fixed=True)

                            fixed_particle.initiate(1, *pos)
                            config.particles.append(fixed_particle)

                    else:
                        for i_particle in config.i_particles:
                            i_particle.initiate(1, *pos)
                            config.particles.append(i_particle)
                        config.i_particles = []

            if event.button in (4, 5):
                modifier = list(config.mod_group.values())[config.mod_mode.value]
                magnitude = 1

                if keys[pygame.K_LSHIFT]:
                    magnitude -= 1
                if keys[pygame.K_LCTRL]:
                    magnitude += 1

                bump_type = ("inc", "dec")[event.button == 5]
                amount = modifier.scaling["amount"]

                modifier.bump(bump_type, magnitude)

                if modifier.name == "Screen zoom":
                    config.screen_scale = mechanical.to_scale(*config.screen_pixel)
                    #MUST UPDATE SCREEN SCALE FOR CONFIG WHEN SCREEN ZOOM CHANGES

                if modifier.name in ("Screen zoom", "Screen X", "Screen Y"):
                    config.mouse_scale = mechanical.to_scale(*config.mouse_pixel, point=True)
                    #MUST UPDATE MOUSE SCALE FOR CONFIG WHEN SCREEN ZOOM OR PAN CHANGES


        if event.type == pygame.VIDEORESIZE:
            config.screen_pixel = (event.w, event.h)
            config.screen_scale = mechanical.to_scale(*config.screen_pixel)
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)


        if event.type == pygame.MOUSEMOTION:
            config.mouse_pixel = event.pos
            config.mouse_scale = mechanical.to_scale(*config.mouse_pixel, point=True)


def update_particles(dt):

    for particle in config.particles[::-1]:
        particle.earth()

    for x, particle in enumerate(config.particles):
        if not particle.fixed:
            for qarticle in config.particles:
                if particle != qarticle:

                    dx, dy = mechanical.sub_vector(particle.P_xs, particle.P_ys, 
                                                   qarticle.P_xs, qarticle.P_ys)
                    r, θ = mechanical.combine(dx, dy)

                    if r == 0:
                        r = 0.001

                    if config.G_const.value:
                        F = mechanical.law_force(config.G_const.value, r,
                                                 particle.m, qarticle.m)
                        particle.apply_force(F, θ)

                    if config.k_e_const.value:
                        F = mechanical.law_force(config.k_e_const.value, r,
                                                 particle.Q, qarticle.Q)
                        particle.apply_force(-F, θ)

    for particle in config.particles[::-1]:
        particle.update(dt)


def update_canvas():

    vis_vectors, vis_values = config.vis_vectors.value, config.vis_values.value

    visual.blank()

    for i_particle in config.i_particles:
        if not i_particle.fixed:

            i_particle.draw_vector(dt=1, mouse=True)

            if vis_vectors >= 2:
                i_particle.label_vector(mouse=True)

        i_particle.draw_mass()

        if vis_values >= 1:
            i_particle.label_values(screen, vis_values)


    for particle in config.particles:

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


    height = 20 * (len(config.mod_group)-1)
    for i, modifier in enumerate(config.mod_group.values()):
        marked = i == config.mod_mode.value
        modifier.display(config.screen_pixel[0], config.screen_pixel[1]-height, marked=marked)
        height -= 20

    visual.resolution()
    visual.time()
    visual.particle_count()

    if not config.playing:
        visual.pause()


done = False
while not done: #PROGRAM LOOP
    check_inputs()

    if config.playing:
        update_particles(config.time_rate.value / config.tick)
        config.t += config.time_rate.value / config.tick

    update_canvas()

    config.clock.tick(config.tick)
    pygame.display.flip()
