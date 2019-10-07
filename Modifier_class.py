import os, sys, math, time, copy, pygame, random, colorsys

class Modifier:

    def __init__(self, value, visual):
        self.value = self.default = value[0]
        self.scaling = {"type":     value[1],
                        "amount":   value[2:4],
                        "bounds":   value[5,6]}
        self.name,
        self.unit,
        self.dp = visual

    def bump(self, bump_type):
        amount = self.scaling["amount"][bump_magnitude]
        identity = (1,-1)[bump_type == "dec"]
        modulo = self.scaling["bounds"][1] - self.scaling["bounds"][0] + 1

        if math_type == "lin":
            self.value += amount * identity
        elif math_type == "geo":
            self.value *= amount ** identity
        elif math_type == "mod":
            self.value = (self.value + amount * identity) % modulo

        if self.scaling["bounds"][0] != None:
            self.value = min(self.scaling["bounds"][0], self.value)
        elif self.scaling["bounds"][1] != None:
            self.value = max(self.scaling["bounds"][1], self.value)

    def display(self, P_xp, P_yp, marked=False):
        marker = ("", ">> ")[marked]
        num_value = str(round(self.name, self.dp)) + self.unit
        visual.draw_text(marker + "{}: {}".format(name, num_value),
                         (P_xp, P_yp), "bottomright")

    def default(self):
        self.value = self.default