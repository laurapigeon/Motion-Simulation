import os, sys, math, time, copy, pygame, random, colorsys

pygame.init()
pygame.font.init()
pygame.display.set_caption("Us Simulation")
screen_pixel = (1600, 900)
screen = pygame.display.set_mode((screen_pixel[0], screen_pixel[1]), pygame.RESIZABLE)
clock = pygame.time.Clock()
tick = 120


class Projectile:

    def __init__(self, P_xs, P_ys, charge, mass, radius, fixed=False):
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


class mechanical:

    @staticmethod
    def resolve(v, θ):
        x = v * math.cos(θ)
        y = v * math.sin(θ)
        return x, y

    @staticmethod
    def combine(x, y):
        v = math.hypot(x, y)
        θ = math.atan2(y, x)
        return v, θ

    @staticmethod
    def sum_vector(x_1, y_1, x_2, y_2):
        return x_1 + x_2, y_1 + y_2

    @staticmethod
    def sub_vector(x_1, y_1, x_2, y_2):
        return x_2 - x_1, y_2 - y_1

    @staticmethod
    def dot_product(x, y, k):
        return x*k, y*k

    @staticmethod
    def midpoint(x_1, y_1, x_2, y_2):
        s_x, s_y = mechanical.sum_vector(x_1, y_1, x_2, y_2)
        return mechanical.dot_product(s_x, s_y, 1/2)

    @staticmethod
    def law_force(k, r, s_1, s_2):
        return k*s_1*s_2 / r**2

    @staticmethod
    def to_scale(x, y, P=False):
        if P:
            x, y = mechanical.sub_vector(*mechanical.dot_product(*screen_pixel, 1/2), x, y)
        x, y = mechanical.dot_product(x, -1*y, 1/values["space"][1])
        if P:
            x, y = mechanical.sub_vector(values["screenx"][1], values["screeny"][1], x, y)
        return x, y

    @staticmethod
    def to_pixel(x, y, P=False):
        if P:
            x, y = mechanical.sum_vector(values["screenx"][1], values["screeny"][1], x, y)
        x, y = mechanical.dot_product(x, -1*y, values["space"][1])
        if P:
            x, y = mechanical.sum_vector(*mechanical.dot_product(*screen_pixel, 1/2), x, y)
        return x, y

    @staticmethod
    def list_round(x, y, digits=0):
        if not digits:
            return int(x), int(y)
        else:
            return round(x, digits), round(y, digits)

    @staticmethod
    def list_abs(x, y):
        return  abs(x), abs(y)

    @staticmethod
    def bump(value, amount, math_type, bump_type, bounds):
        if math_type == "lin" and bump_type == "inc":
            value += amount
        elif math_type == "lin" and bump_type == "dec":
            value -= amount

        elif math_type == "geo" and bump_type == "inc":
            value *= 1 + amount
        elif math_type == "geo" and bump_type == "dec":
            value /= 1 + amount

        elif math_type == "mod" and bump_type == "inc":
            value = (value + amount) % (bounds[1] - bounds[0] + 1)
        elif math_type == "mod" and bump_type == "dec":
            value = (value - amount) % (bounds[1] - bounds[0] + 1)

        if bounds[0] != None and value <= bounds[0]:
            return bounds[0]
        elif bounds[1] != None and value >= bounds[1]:
            return bounds[1]
        else:
            return value

    def sigmoid(x):
        return 1 / (1 + math.exp(-x))

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


class visual:

    @staticmethod
    def draw_text(text, coords, corner="topleft",
                  colour=(164, 164, 255), font=pygame.font.Font("freesansbold.ttf", 15)):
        text_surface = font.render(text, True, colour)
        text_rectangle = text_surface.get_rect()
        text_rectangle.__setattr__(corner, coords)
        screen.blit(text_surface, text_rectangle)

    @staticmethod
    def values():
        for i, name in enumerate(values):
            value = values[name]
            marker = ("", ">> ")[val_mode == i]
            num_value = str(round(value[1], value[8]))
            unit = value[7]
            coords = (screen_pixel[0], screen_pixel[1] + 20*i - 20*(len(values)-1))
            visual.draw_text(marker + "{}: {}".format(name, num_value + unit),
                             coords, "bottomright")

    @staticmethod
    def resolution():
        visual.draw_text("({}, {})".format(*mechanical.list_round(*screen_pixel, 2)),
                         (screen_pixel[0], 0), "topright")

        visual.draw_text("({}m, {}m)".format(*mechanical.list_round(*screen_scale, 2)),
                         (screen_pixel[0], 20), "topright")

    @staticmethod
    def time():
        visual.draw_text("t = {}{}".format(round(t, 2), "s"), (0, 0), "topleft")

    @staticmethod
    def projectile_count():
        visual.draw_text("{} projectiles".format(len(projectiles)+len(i_projectiles)), (0, 20), "topleft")

    @staticmethod
    def mouse_pos():
        num_value = mechanical.list_round(mouse_scale[0], mouse_scale[1] + screen_scale[1], 2)
        coords = (mouse_pixel[0], mouse_pixel[1] + 10)
        visual.draw_text("({}m, {}m)".format(*num_value),
                         coords, "midtop")

    @staticmethod
    def pause():
        for i in range(2):
            pygame.draw.line(screen, (164, 164, 255),
                             (10*(i+1), screen_pixel[1] - 30),
                             (10*(i+1), screen_pixel[1] - 10), 5)

    @staticmethod
    def to_canvas():
        screen.fill((0, 0, 0))

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
          "charge":      ["Charge",       0,   "lin", 0.01,  0.1,  1,   [None, None], "C",        2, 2],
          "mass":        ["Mass",         1,   "lin", 0.01,  0.1,  1,   [0.1, None],  "kg",       2, 2],
          "radius":      ["Radius",       0.1, "geo", 0.005, 0.05, 0.5, [None, None], "m",        2, 2],
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
        mechanical.tick(values["time"][1] / tick)
        t += values["time"][1] / tick

    visual.to_canvas()

    clock.tick(tick)
    pygame.display.flip()
