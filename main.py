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
            circle.draw()

    def update_all(self):
        for circle in self.elements:
            circle.update()


class Circle:
    def __init__(self, position, radius, color=(0, 50, 200)):
        self.linear = Linear()
        self.linear.position[:] = position
        self.linear.velocity[:] = (randint(-10, 10), randint(-10, 10))
        self.radius = radius
        self.color = random_color()
        self.mass = 1
        self.moment = self.mass * self.radius ** 2
        circles.elements.append(self)

    def update(self):
        self.linear.velocity += self.linear.acceleration
        self.linear.position += self.linear.velocity

    def draw(self):
        pygame.draw.circle(screen.display, self.color, self.linear.position, self.radius)


class GridMap:
    def __init__(self, size: tuple[int, int]):
        self.rows, self.columns = size
        self.cell_width = screen.width / self.columns
        self.cell_height = screen.height / self.rows
        self.dictionary = {}

    def update_keys(self, circles):
        for circle in circles:
            self.dictionary[circle] = (None, None)

    def update_values(self, circles):
        for circle in circles:
            x, y = circle.linear.position
            row = y // self.cell_height
            column = x // self.cell_width
            self.dictionary[circle] = (row, column)

    def find_neighboring_cells(self, row, column):
        neighboring_cells = [(row - 1, column), (row + 1, column),
                             (row, column - 1), (row, column + 1),
                             (row - 1, column - 1), (row + 1, column - 1),
                             (row - 1, column + 1), (row + 1, column + 1)]
        
        return neighboring_cells

    def find_circles_in_a_cell(self, row, column):
        circles = []
        for circle, position in self.dictionary.items():
            if position == (row, column):
                circles.append(circle)

        return circles

    def check_collision_for_all(self):
        for circle in self.dictionary:
            collision.check_for_screen_borders(circle)
        for row in range(self.rows):
            for column in range(self.columns):
                circles = self.find_circles_in_a_cell(row, column)
                if len(circles) != 0:
                    neighboring_cells = self.find_neighboring_cells(row, column)
                    if len(circles) > 1:
                        for circle_1 in circles:
                            for circle_2 in circles:
                                if circle_1 != circle_2:
                                    if collision.check(circle_1, circle_2) is True:
                                        collision.response(circle_1, circle_2)
                        for neighboring_cell in neighboring_cells:
                            n_row, n_column = neighboring_cell
                            neighboring_circles = self.find_circles_in_a_cell(n_row, n_column)
                            for circle in circles:
                                for neighboring_circle in neighboring_circles:
                                    if collision.check(circle, neighboring_circle) is True:
                                        collision.response(circle, neighboring_circle)
                    else:
                        circle = circles[0]
                        for neighboring_cell in neighboring_cells:
                            n_row, n_column = neighboring_cell
                            neighboring_circles = self.find_circles_in_a_cell(n_row, n_column)
                            for neighboring_circle in neighboring_circles:
                                if collision.check(circle, neighboring_circle) is True:
                                    collision.response(circle, neighboring_circle)
            
    
class Game:
    @staticmethod
    def setup():
        circle_1 = Circle(position=(300, 300), radius=50)
        circle_2 = Circle(position=(600, 600), radius=50)
        grid_map.update_keys(circles.elements)
        grid_map.update_values(circles.elements)

    @staticmethod
    def draw_and_update():
        screen.fill()
        circles.draw_all()
        screen.FPS.text.show(screen.display, position=(0, 0))
        screen.update()


game = Game()
circles = Circles()
screen = Screen(background_color=(255, 255, 255), resolution=(1000, 1000))
grid_map = GridMap(size=(10, 10))  # 20 = 1000 / 50, size = resolution / radius
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
    circles.update_all()
    grid_map.update_values(circles.elements)
    grid_map.check_collision_for_all()
    game.draw_and_update()
    
