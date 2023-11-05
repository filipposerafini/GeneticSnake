import pygame
from pygame.locals import *
import math
import numpy as np
import nn
import sys
from operator import attrgetter

# Grid Size
CELL_COUNT = 40

# Colors
BLACK = (0, 0, 0)
DARK_GRAY = (16, 16, 16)
LIGHT_GRAY = (32, 32, 32)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# FPS
DEBUG_FPS = 10
FPS = 50

class Apple:

    def __init__(self, snake):
        retry = True
        while retry:
            retry = False
            self.x = np.random.randint(0, CELL_COUNT - 1)
            self.y = np.random.randint(0, CELL_COUNT - 1)
            for i in range(0, snake.length):
                if self.x == snake.x[i] and self.y == snake.y[i]:
                    retry = True

    def draw(self, surface, cell_size, color):
        body = pygame.Surface((cell_size, cell_size))
        body.fill(color)
        surface.blit(body, ((self.x + 1) * cell_size, (self.y + 1) * cell_size))

class Snake:

    def __init__(self, x=CELL_COUNT/2, y=CELL_COUNT/2, length=10):
        self.x = [x]
        self.y = [y]
        self.length = length
        self.direction = 0 if self.x[0] < CELL_COUNT / 2 else 2
        for i in range(1, self.length):
            self.x.append(self.x[0] - i if self.x[0] < CELL_COUNT / 2 else self.x[0] + i)
            self.y.append(self.y[0])
        self.apple = Apple(self)
        self.score = 0
        self.dead = False

    def turn_right(self):
        self.direction += 1
        if self.direction == 4:
            self.direction = 0

    def turn_left(self):
        self.direction -= 1
        if self.direction == -1:
            self.direction = 3

    def change_direction(self, x):
        if x == 1:
            self.turn_right()
        elif x == 2:
            self.turn_left()

    def move(self):
        for i in range(self.length - 1 , 0, -1):
            self.x[i] = self.x[i - 1]
            self.y[i] = self.y[i - 1]
        if self.direction == 0:
            self.x[0] += 1
        elif self.direction == 1:
            self.y[0] += 1
        elif self.direction == 2:
            self.x[0] -= 1
        elif self.direction == 3:
            self.y[0] -= 1

    def collide(self, x, y):
        if self.x[0] == x and self.y[0] == y:
            return True
        else:
            return False

    def add_piece(self, count):
        for i in range(0, count):
            self.x.append(self.x[self.length - 1])
            self.y.append(self.y[self.length - 1])
            self.length += 1

    def eat_apple(self):
        if self.collide(self.apple.x, self.apple.y):
            self.add_piece(1)
            return True
        return False

    def hit_self(self):
        for i in range(1, self.length):
            if self.collide(self.x[i], self.y[i]):
                return True
        return False

    def hit_border(self):
        if self.x[0] < 0 or self.x[0] > CELL_COUNT - 1:
            return True
        elif self.y[0] < 0 or self.y[0] > CELL_COUNT - 1:
            return True
        else:
            return False

    def get_distance(self, targetx, targety, direction):

        if direction == 0:
            if self.y[0] == targety and targetx > self.x[0]:
                return 1 - (targetx - self.x[0]) / CELL_COUNT
            else:
                return 0

        elif direction == 1:
            if self.x[0] == targetx and targety > self.y[0]:
                return 1 - (targety - self.y[0]) / CELL_COUNT
            else:
                return 0

        elif direction == 2:
            if self.y[0] == targety and targetx < self.x[0]:
                return 1 - (self.x[0] - targetx) / CELL_COUNT
            else:
                return 0

        elif direction == 3:
            if self.x[0] == targetx and targety < self.y[0]:
                return 1 - (self.y[0] - targety) / CELL_COUNT
            else:
                return 0
        else:
            return 0

    def get_inputs(self):
        
        #distance from apple
        apple_front = self.get_distance(self.apple.x, self.apple.y, self.direction)
        apple_left = self.get_distance(self.apple.x, self.apple.y, (self.direction - 1) % 4)
        apple_right = self.get_distance(self.apple.x, self.apple.y, (self.direction + 1) % 4)

        #distance from wall
        wall_front = 0
        wall_left = 0
        wall_right = 0

        if self.direction == 0:
            wall_front = self.x[0] / CELL_COUNT
            wall_right = self.y[0] / CELL_COUNT 
            wall_left = 1 - wall_right

        elif self.direction == 1:
            wall_front = self.y[0] / CELL_COUNT
            wall_left = self.x[0] / CELL_COUNT 
            wall_right = 1 - wall_left

        elif self.direction == 2:
            wall_front = 1 - self.x[0] / CELL_COUNT
            wall_left = self.y[0] / CELL_COUNT 
            wall_right = 1 - wall_left

        elif self.direction == 3:
            wall_front = 1 - self.y[0] / CELL_COUNT
            wall_right = self.x[0] / CELL_COUNT 
            wall_left = 1 - wall_right

        #distance from self
        self_front = 0
        self_left = 0
        self_right = 0

        for i in range(3, self.length):
            front = self.get_distance(self.x[i], self.y[i], self.direction)
            if front > self_front:
                self_front = front
            left = self.get_distance(self.x[i], self.y[i], (self.direction - 1) % 4)
            if left > self_left:
                self_left = left
            right = self.get_distance(self.x[i], self.y[i], (self.direction + 1) % 4)
            if right > self_right:
                self_right = right

        return [apple_front, apple_left, apple_right, wall_front, wall_left, wall_right, self_front, self_left, self_right]

    def draw(self, surface, cell_size, color):
        body = pygame.Surface((cell_size, cell_size))
        body.fill(color)
        for i in range(0, self.length):
            surface.blit(body, ((self.x[i] + 1) * cell_size, (self.y[i] + 1) * cell_size))

class Game:

    def __init__(self, show=True):
        self.show = show
        self.font = None
        if show:
            pygame.init()
            pygame.display.set_caption('Snake - The Genetic Algorithm')
            icon = pygame.image.load('resources/icon.png')
            pygame.display.set_icon(icon)
            self.font = pygame.font.Font('font.ttf', 30)


            self.cell_size = int(pygame.display.Info().current_w / 100)
            self.width = CELL_COUNT * self.cell_size + 2*self.cell_size
            self.height = CELL_COUNT * self.cell_size + 2*self.cell_size
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.HWSURFACE)
            self.clock = pygame.time.Clock()

            self.screen.fill(BLACK)

        self.snakes = []
        self.stop = False

    def best_snake(self):
        sorted_snakes = sorted(self.snakes, key=attrgetter('score'), reverse=True)
        for snake in sorted_snakes:
            if not snake.dead:
                return snake

    def update(self, fps):
        if fps is not None:
            self.clock.tick(fps)
        for snake in self.snakes:
            if not snake.dead:
                snake.move()
                if snake.hit_border():
                    snake.dead = True
                elif snake.hit_self():
                    snake.dead = True
                else:
                    if snake.eat_apple():
                        snake.score += 1
                        snake.apple = Apple(snake)
                    # else:
                        # snake.score -= 0.002

    def render(self, step=None):
        if not self.show:
            return
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, WHITE, Rect(0, 0, self.width, self.height), self.cell_size)
        
        best = self.best_snake()
        for snake in self.snakes:
            if not snake.dead and snake is not best:
                snake.draw(self.screen, self.cell_size, DARK_GRAY)
                snake.apple.draw(self.screen, self.cell_size, LIGHT_GRAY)
        if not best.dead:
            best.draw(self.screen, self.cell_size, GREEN)
            best.apple.draw(self.screen, self.cell_size, RED)
            
            score_surf = self.font.render(str(int(best.score)), True, YELLOW)
            score_rect = score_surf.get_rect()
            score_rect.topright = (CELL_COUNT * self.cell_size, 1.5 * self.cell_size)
            self.screen.blit(score_surf, score_rect)

        if step is not None:
            step_surf = self.font.render(str(step), True, LIGHT_GRAY)
            step_rect = step_surf.get_rect()
            step_rect.topright = (CELL_COUNT * self.cell_size, 3 * self.cell_size)
            self.screen.blit(step_surf, step_rect)

        pygame.display.flip()

    def is_stopped(self):
        if self.show:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        return True
        return False

    def play(self, fps, neural_net=None):
        while not self.stop:
            self.render()
            action = 2
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.end()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_RIGHT and neural_net is None:
                        action = 0
                        break
                    elif event.key == K_LEFT and neural_net is None:
                        action = 1
                        break
                    elif event.key == K_ESCAPE:
                        self.end()
                        return
                    elif event.key == K_RETURN:
                        self.reset()
                        self.snakes.append(Snake())
                        break
                else:
                    pass

            player = self.snakes[0]

            inputs = player.get_inputs()

            if neural_net:
                action = np.argmax(neural_net.compute_outputs(inputs))

            if action == 0:
                player.turn_right()
            elif action == 1:
                player.turn_left()
            self.update(fps)
            if player.dead:
                self.reset()
                self.snakes.append(Snake())
        else:
            self.end()

    def reset(self):
        self.snakes = []
        self.stop = False

    def end(self):
        pygame.quit()

if __name__ == '__main__':

    args = len(sys.argv)
    fps = FPS
    if args == 1:
        neural_net = None
        fps = DEBUG_FPS
    elif args == 2:
        filename = sys.argv[1]
        if filename.endswith('.json'):
            neural_net = nn.fromJSON(filename)
        else:
            print('usage: snake.py [snake_nn.json]')
            sys.exit()
    else:
        print('usage: snake.py [snake_nn.json]')
        sys.exit()

    game = Game()
    game.snakes.append(Snake())
    game.play(fps, neural_net)
