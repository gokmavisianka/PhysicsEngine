"""
MIT License

Copyright (c) 2023 Rasim Mert YILDIRIM

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import pygame
import numpy as np
import math
from random import randint, choice

pygame.init()
ON = True

def random_color(start=100, end=200):
    r = randint(start, end)
    g = randint(start ,end)
    b = randint(start, end)
    return r, g, b

def hypotenuse(x, y):
    return (x ** 2 + y ** 2) ** 0.5

def relative(first_vector, second_vector):
    return first_vector - second_vector

def normal(first_vector, second_vector):
    return second_vector - first_vector

def corners(Object):
    x, y = Object.linear.position
    width, height = Object.size / 2
    A = [x - width, y - height]
    B = [x + width, y - height]
    C = [x + width, y + height]
    D = [x - width, y + height]
    return np.array((A, B, C, D), dtype=float)



class Vector2D:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def magnitude(self):
        return hypotenuse(self.x, self.y)


class Linear:
    def __init__(self):
        self.position = np.array((0, 0), dtype=float)
        self.velocity = np.array((0, 0), dtype=float)
        self.acceleration = np.array((0, 0), dtype=float)


class Angular:
    def __init__(self):
        self.position = 0
        self.velocity = 1
        self.acceleration = 0
        

class Transform:
    @staticmethod
    def rotate(Object, angle, center=None):
        radians = math.radians(angle)
        cos = np.cos(radians)
        sin = np.sin(radians)
        if center is None:
            center = Object.linear.position
        x = Object.corners[:, 0] - center[0]
        y = Object.corners[:, 1] - center[1]
        Object.corners[:, 0] = x * cos - y * sin + center[0]
        Object.corners[:, 1] = x * sin + y * cos + center[1]

        
def edges(Object):
    return np.roll(Object.corners, -1, axis=0) - Object.corners

def normals(Object):
    return np.roll(Object.edges, -1, axis=0) - Object.edges


class Collision:
    def check(self, A, B):
        N = normal(B.linear.position, A.linear.position)
        distance = hypotenuse(*N)
        minimum_required_distance_for_collision = A.radius + B.radius
        if distance < minimum_required_distance_for_collision:
            return True
        else:
            return False

    def check_for_screen_borders(self, Object, elasticity=1):
        x, y = Object.linear.position
        if x - Object.radius <= 0:
            Object.linear.position[0] = Object.radius
            Object.linear.velocity[0] = abs(Object.linear.velocity[0]) * elasticity
        elif x + Object.radius >= screen.width:
            Object.linear.position[0] = screen.width - Object.radius
            Object.linear.velocity[0] = -abs(Object.linear.velocity[0]) * elasticity
        if y - Object.radius <= 0:
            Object.linear.position[1] = Object.radius
            Object.linear.velocity[1] = abs(Object.linear.velocity[1]) * elasticity
        elif y + Object.radius >= screen.height:
            Object.linear.position[1] = screen.height - Object.radius
            Object.linear.velocity[1] = -abs(Object.linear.velocity[1]) * elasticity
            
    @staticmethod
    def response(A, B, elasticity=1):
        # V: relative velocity, J: impulse, N: normal.
        V = relative(A.linear.velocity, B.linear.velocity)
        N = normal(B.linear.position, A.linear.position)
        J = -(1 + elasticity)*np.dot(V, N)/((1/A.mass + 1/B.mass)*np.dot(N, N))
        A.linear.velocity += np.dot(J, N) / A.mass
        B.linear.velocity -= np.dot(J, N) / B.mass


class Air:
    def __init__(self):
        self.viscosity = 1.81 * 10 ** (-5)  # (Newton * second) / (meter ^ 2)
        self.temperature = 20  # Celsius degrees


class Text:
    def __init__(self, base_string: str, function, color: tuple[int, int, int] = (255, 0, 0)):
        # base_string can be "FPS: " or "Coin: " to represent the remaining part.
        self.base_string = base_string
        self.color = color
        # function is used to get the remaining part (It can be fps value or amount of coins etc.) of the string.
        # So {base_string + remaining} will be shown on the screen.
        self.function = function
        # Size of the font can be changed.
        self.font = pygame.font.SysFont("Helvetica", 32)

    def show(self, display, position, string=None):
        if string is None:
            string = self.base_string
            remaining = self.function()
            # Check if the type of the remaining part is str. If not, Convert it to the str type before merging strings.
            if type(remaining) is str:
                string += remaining
            else:
                string += str(remaining)
        text = self.font.render(string, True, self.color)
        display.blit(text, position)


class Screen:
    def __init__(self, background_color: tuple[int, int, int], resolution: tuple[int, int] = (1000, 1000)):
        self.background_color = background_color
        self.width, self.height = resolution
        self.display = pygame.display.set_mode(resolution)
        self.FPS = self.FPS()

    def fill(self, color=None):
        if color is None:
            color = self.background_color
        # fill the screen with specific color.
        self.display.fill(color)

    @staticmethod
    def update():
        # Update the whole window.
        pygame.display.flip()

    class FPS:
        def __init__(self):
            self.clock = pygame.time.Clock()
            self.text = Text(base_string="FPS: ", function=self.get)

        def set(self, value):
            self.clock.tick(value)

        def get(self):
            return int(self.clock.get_fps())


class Circles:
    def __init__(self):
        self.elements = []

    def draw_all(self):
        for circle in self.elements:
            circle.update()
            circle.draw()


class Circle:
    def __init__(self, position, radius, color=(0, 50, 200)):
        self.linear = Linear()
        self.linear.position[:] = position
        self.radius = radius
        self.color = random_color()
        self.mass = 1
        self.moment = self.mass * self.radius ** 2

    def update(self):
        self.linear.velocity += self.linear.acceleration
        self.linear.position += self.linear.velocity

    def draw(self):
        pygame.draw.circle(screen.display, self.color, self.linear.position, self.radius)


class Game:
    @staticmethod
    def setup():
        r1 = Circle(position=(300, 300), radius=50)
        r2 = Circle(position=(498, 500), radius=50)
        r1.linear.velocity[0] = 25
        r2.linear.velocity[0] = -25
        r1.linear.velocity[1] = 23
        r2.linear.velocity[1] = -32
        circles.elements.append(r1)
        circles.elements.append(r2)

    @staticmethod
    def draw_and_update():
        screen.fill()
        circles.draw_all()
        screen.FPS.text.show(screen.display, position=(0, 0))
        screen.update()


game = Game()
circles = Circles()
screen = Screen(background_color=(255, 255, 255), resolution=(1000, 1000))
transform = Transform()
collision = Collision()
game.setup()

while ON:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_q]:
        ON = False
        pygame.quit()
        quit()
    screen.FPS.set(60)
    collision.check_for_screen_borders(circles.elements[0])
    collision.check_for_screen_borders(circles.elements[1])
    if collision.check(circles.elements[0], circles.elements[1]) is True:
        collision.response(circles.elements[0], circles.elements[1])
    game.draw_and_update()
