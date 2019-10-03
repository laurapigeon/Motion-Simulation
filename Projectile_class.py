import os, sys, math, time, copy, pygame, random, colorsys
import math_functions as mechanical
import visual_functions as visual

class Projectile:
    charge = 0
    mass = 1
    radius = 0.1
    fixed = 0
    def __init__(self, P_xs, P_ys):
        self.P_xs, self.P_ys = P_xs, P_ys
        self.Q = charge
        self.m = mass
        self.r_s = radius
        self.fixed = fixed
        self.light_colour = self.get_colour(0.75)
        self.colour       = self.get_colour(0.5)
        self.dark_colour  = self.get_colour(0.25)

    def initiate(self, dt, P_x2s, P_y2s):
        self.t_0 = t
        dP_xs, dP_ys = mechanical.sub_vector(self.P_xs, self.P_ys, P_x2s, P_y2s)
        self.v_xs, self.v_ys = mechanical.dot_product(dP_xs, dP_ys, dt)

    def earth(self):
        self.F_xs, self.F_ys = mechanical.resolve(-1*self.m*g*values["gravity"][1],
                                                  math.radians(values["angle"][1]))

    def apply_force(self, F_s, θ_s):
        F_x2s, F_y2s = mechanical.resolve(F_s, θ_s)
        self.F_xs, self.F_ys = mechanical.sum_vector(self.F_xs, self.F_ys, F_x2s, F_y2s)

    def update(self, dt):
        if self.get_dead():
            projectiles.remove(self)

        if not self.fixed:
            dP_xs, dP_ys = mechanical.dot_product(self.v_xs, self.v_ys, dt)
            dv_xs, dv_ys = mechanical.dot_product(self.F_xs, self.F_ys, dt/self.m)

            self.P_xs, self.P_ys = mechanical.sum_vector(self.P_xs, self.P_ys, dP_xs, dP_ys)
            self.v_xs, self.v_ys = mechanical.sum_vector(self.v_xs, self.v_ys, dv_xs, dv_ys)

            if self.get_too_far():
                projectiles.remove(self)

    def get_pos(self):
        return mechanical.to_pixel(self.P_xs, self.P_ys, True)

    def get_dead(self):
        life_exists = values["life"][1]
        projectile_is_old = abs(t - self.t_0 > values["life"][1])
        return life_exists and projectile_is_old

    def get_visible(self):
        P_xp, P_yp = self.get_pos()
        horizontal = 0 < P_xp and P_xp < screen_pixel[0]
        vertical   = 0 < P_yp and P_yp < screen_pixel[1]
        return horizontal and vertical
    
    def get_too_far(self):
        P_xp, P_yp = self.get_pos()
        max_P = sys.maxsize/100
        return P_xp < -max_P or max_P < P_xp or P_yp < -max_P or max_P < P_yp

    def get_colour(self, L):
        colour = colorsys.hsv_to_rgb(mechanical.sigmoid(-self.Q/3),
                                     mechanical.sigmoid(self.m/4 - 2), L)
        return (colour[0]*255, colour[1]*255, colour[2]*255)

    def draw_mass(self):
        P_xp, P_yp = mechanical.list_round(*self.get_pos())

        r_p = round(self.r_s * values["space"][1])

        pygame.draw.circle(screen, self.colour, (P_xp, P_yp), r_p)
        if self.fixed:
            pygame.draw.circle(screen, self.dark_colour, (P_xp, P_yp), round(r_p / 2))
            

    def draw_vector(self, dt=1, mouse=False):
            P_x1p, P_y1p = self.get_pos()

            if mouse:
                P_x2p, P_y2p = mouse_pixel

            else:
                dP_xs, dP_ys = mechanical.dot_product(self.v_xs, self.v_ys, dt)
                dP_xp, dP_yp = mechanical.to_pixel(dP_xs, dP_ys)
                P_x2p, P_y2p = mechanical.sum_vector(P_x1p, P_y1p, dP_xp, dP_yp)

            r_p = round(self.r_s * values["space"][1])

            pygame.draw.line(screen, self.dark_colour, (P_x1p, P_y1p), (P_x2p, P_y2p), r_p)

    def label_values(self, value):
        P_xs, P_ys = mechanical.list_round(self.P_xs, self.P_ys + screen_scale[1], 2)
        P_xp, P_yp = mechanical.list_round(*self.get_pos(), 2)

        offset = 10
        if value == 1 or value == 4:
            visual.draw_text("({}m, {}m)".format(P_xs, P_ys),
                             (P_xp, P_yp+offset), "midtop", (self.light_colour))
            offset += 20

        if value == 2 or value == 4:
            visual.draw_text("{}kg".format(self.m),
                             (P_xp, P_yp+offset), "midtop", (self.light_colour))
            offset += 20

        if value == 3 or value == 4:
            visual.draw_text("{}C".format(self.Q),
                             (P_xp, P_yp+offset), "midtop", (self.light_colour))

    def label_vector(self, mouse=False):
        P_x1p, P_y1p = self.get_pos()

        if mouse:
            v_xp, v_yp = mechanical.sub_vector(P_x1p, P_y1p, P_x2p, P_y2p)
            v_xs, v_ys = mechanical.to_scale(v_xp, v_yp)
            v_s, θ_s = mechanical.combine(v_xs, v_ys)

        else:
            v_xp, v_yp = mechanical.to_pixel(self.v_xs, self.v_ys)
            P_x2p, P_y2p = mechanical.sum_vector(P_x1p, P_y1p, v_xp, v_yp)
            v_s, θ_s = mechanical.combine(self.v_xs, self.v_ys)

        P_xmp, P_ymp = mechanical.midpoint(P_x1p, P_y1p, P_x2p, P_y2p)

        visual.draw_text(str(round(v_s, 2)) + "ms-1",
                         (P_xmp, P_ymp), "center", self.light_colour)
        visual.draw_text(str(round(math.degrees(θ_s), 2)) + "°",
                             (P_x1p, P_y1p), "topleft", self.light_colour)
