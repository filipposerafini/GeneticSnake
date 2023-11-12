import snake
import nn
import pygame
import numpy as np
from pygame.locals import *

# FPS
DIFFICULTY = {
        'Easy' : 20,
        'Normal' : 30,
        'Hard': 40
        }

# Music
MUSIC = {
        'Menu' : 'resources/intro.wav',
        DIFFICULTY['Easy'] : 'resources/easy.wav',
        DIFFICULTY['Normal'] : 'resources/normal.wav',
        DIFFICULTY['Hard'] : 'resources/hard.wav',
        'Pause' : None,
        'Confirm' : None,
        'GameOver' : 'resources/game_over.wav'
        }

# Sounds
SOUNDS = {}

class Page(object):

    def __init__(self, surface):
        self.surface = surface
        self.surface.fill(snake.BLACK)
        self.buttons = {}
        self.keys = {
                'Sound' : K_n,
                'Music' : K_m
                }

    def update(self):
        return

    def get_button(self, mouse_pos):
        for button, rect in self.buttons.items():
            if rect.collidepoint(mouse_pos):
                return button

    def get_keys(self, key):
        for action, keys in self.keys.items():
            if isinstance(keys, list):
                if key in keys:
                    return action
            else:
                if key == keys:
                    return action

    def display_text(self, text, dimension, color, position, background=None, anchor='center'):
        font = pygame.font.Font('resources/font.otf', int(dimension))
        text_surface = font.render(text, True, color, background)
        rect = text_surface.get_rect()
        if anchor == 'center':
            rect.center = position
        elif anchor == 'left':
            rect.midleft = position
        elif anchor == 'right':
            rect.midright = position
        self.surface.blit(text_surface, rect)
        return rect

class Menu(Page):

    def __init__(self, surface):
        super(Menu, self).__init__(surface)
        width = self.surface.get_width()
        height = self.surface.get_height()
        self.display_text('Python', height / 3, snake.BLUE, (width / 4 + width / 12, 2 * height / 6))
        self.display_text('Viper', height / 3, snake.GREEN, (3 * width / 4 - width / 32, 2 * height / 6))
        self.display_text('versus', height / 8, snake.RED, (width / 2 + width / 40, 2 * height / 6 + height / 12))
        self.buttons['Single'] = self.display_text('Single Player', height / 12, snake.WHITE, (width / 4, 4 * height / 6))
        self.buttons['1v1'] = self.display_text('Two Players', height / 12, snake.WHITE, (width / 2, 4 * height / 6))
        self.buttons['AI'] = self.display_text('Player vs AI', height / 12, snake.WHITE, (3 * width / 4, 4 * height / 6))
        self.buttons['Settings'] = self.display_text(' Settings ', height / 12, snake.BLACK, (width / 3, 5 * height / 6), snake.WHITE)
        self.buttons['Leaderboard'] = self.display_text(' Leaderboard ', height / 12, snake.BLACK, (2 * width / 3, 5 * height / 6), snake.WHITE)
        self.keys['Single'] = K_1
        self.keys['1v1'] = K_2
        self.keys['AI'] = K_3
        self.keys['Settings'] = K_TAB
        self.keys['Leaderboard'] = K_l
        self.keys['Quit'] = K_ESCAPE

class Leaderboard(Page):

    def __init__(self, surface):
        super(Leaderboard, self).__init__(surface)
        width = self.surface.get_width()
        height = self.surface.get_height()
        self.buttons['Menu'] = self.display_text(' Leaderboard: ', height / 4, snake.BLACK, (width / 2, height / 4), background=snake.YELLOW)
        difficulty = ['Easy', 'Normal', 'Hard']
        for i in range (1, 4):
            self.display_text(str(i) + '.', height / 10, snake.YELLOW, (width / 12, height / 2 + (i + 1) * height / 10))
            self.display_text(difficulty[i - 1], height / 9, snake.RED, (i * width / 4, height / 2))
        self.scores = {
                DIFFICULTY['Easy']: [],
                DIFFICULTY['Normal']: [],
                DIFFICULTY['Hard']: []
                }
        self.keys['Menu'] = K_ESCAPE

    def update(self):
        super(Leaderboard, self).update()
        width = self.surface.get_width()
        height = self.surface.get_height()
        for j in range(0, len(self.scores.keys())):
            key = list(self.scores.keys())[j]
            score = self.scores[key]
            for i in range(0, min(len(score), 3)):
                self.display_text(str(score[i]), height / 10, snake.WHITE, ((j + 1) * width / 4, height / 2 + (i + 2) * height / 10))

class Settings(Page):

    def __init__(self, surface):
        super(Settings, self).__init__(surface)
        width = self.surface.get_width()
        height = self.surface.get_height()
        self.buttons['Menu'] = self.display_text(' Settings ', height / 4, snake.BLACK, (width / 2, height / 4), background=snake.YELLOW)
        self.display_text('Difficulty:', height / 7, snake.WHITE, (width / 3, 3 * height / 5))
        self.display_text('Audio:', height / 7, snake.WHITE, (width / 3 - width / 20, 4 * height / 5))
        self.keys['Menu'] = K_TAB
        self.difficulty = 0
        self.sound = True
        self.music = True
        self.load_settings()
        pygame.mixer.music.set_volume(1 if self.music else 0)

    def update(self):
        super(Settings, self).update()
        width = self.surface.get_width()
        height = self.surface.get_height()
        key = list(DIFFICULTY.keys())[self.difficulty]
        self.buttons['Difficulty'] = self.display_text('   ' + key + '   ', height / 7, snake.RED, (7 * width / 10, 3 * height / 5), snake.BLACK)

        if self.music:
            foreground = snake.WHITE
            background = snake.RED
        else:
            foreground = snake.RED
            background = snake.BLACK
        self.buttons['Music'] = self.display_text(' Music ', height / 9, foreground, (4 * width / 5, 4 * height / 5), background)

        if self.sound:
            foreground = snake.WHITE
            background = snake.RED
        else:
            foreground = snake.RED
            background = snake.BLACK
        self.buttons['Sound'] = self.display_text(' Sound ', height / 9, foreground, (3 * width / 5, 4 * height / 5), background)

    def load_settings(self):
        try:
            with open('resources/.settings', 'r') as f:
                for line in f:
                    settings = line.split(':')
                    if settings[0] == 'Difficulty':
                        self.difficulty = int(settings[1][:-1])
                    elif settings[0] == 'Music':
                        self.music = settings[1][:-1] == 'True'
                    elif settings[0] == 'Sound':
                        self.sound = settings[1][:-1] == 'True'
        except:
            pass

    def save_settings(self):
        with open('resources/.settings', 'w') as f:
            f.write('Difficulty:' + str(self.difficulty) + '\n')
            f.write('Music:' + str(self.music) + '\n')
            f.write('Sound:' + str(self.sound) + '\n')

class GameField(Page):

    def __init__(self, cell_size, surface):
        super(GameField, self).__init__(surface)
        width = self.surface.get_width()
        height = self.surface.get_height()
        self.cell_size = cell_size
        self.keys['Menu'] = K_ESCAPE
        self.keys['Pause'] = K_p
        self.keys['Viper'] = [K_d, K_s, K_a, K_w]
        self.keys['Python'] = [K_RIGHT, K_DOWN, K_LEFT, K_UP]
        self.game = None

    def update(self):
        super(GameField, self).update()
        self.surface.fill(snake.BLACK)
        width = self.surface.get_width()
        height = self.surface.get_height()
        pygame.draw.rect(screen, snake.WHITE, Rect(0, 0, width, height), self.cell_size)
        if not self.game == None:
            rect = self.display_text('Python: ' + str(self.game.snakes[0].score), height / 12, snake.BLUE, (2 * self.cell_size, 4 * self.cell_size), snake.BLACK, anchor='left')
            self.display_text('x' + str(self.game.snakes[0].lives), height / 18, snake.BLUE, (rect.right + self.cell_size, 4.39 * self.cell_size), snake.BLACK, anchor='left')
            if len(self.game.snakes) == 2:
                rect = self.display_text('Viper: ' + str(self.game.snakes[1].score), height / 12, snake.GREEN, (width - 2 * self.cell_size, 4 * self.cell_size), snake.BLACK, anchor='right')
                self.display_text('x' + str(self.game.snakes[1].lives), height / 18, snake.GREEN, (rect.left - self.cell_size, 4.39 * self.cell_size), snake.BLACK, anchor='right')
            self.game.draw(self.surface, self.cell_size)

class Pause(Page):

    def __init__(self, surface, game_surface):
        super(Pause, self).__init__(surface)
        width = self.surface.get_width()
        height = self.surface.get_height()
        self.surface.fill(snake.WHITE)
        self.game_surface = game_surface
        self.game_surface.set_alpha(220)
        self.surface.blit(self.game_surface, (0, 0))
        self.display_text('Paused', height / 3, snake.YELLOW, (width / 2, 2 * height / 5))
        self.buttons['Unpause'] = self.display_text('Resume', height / 8, snake.GREEN, (width / 2, 3 * height / 4))
        self.keys['Unpause'] = K_p

class Confirm(Page):

    def __init__(self, surface, game_surface):
        super(Confirm, self).__init__(surface)
        width = self.surface.get_width()
        height = self.surface.get_height()
        self.surface.fill(snake.WHITE)
        self.game_surface = game_surface
        self.game_surface.set_alpha(220)
        self.surface.blit(self.game_surface, (0, 0))
        self.display_text('Are you sure?', height / 4, snake.YELLOW, (width / 2, 2 * height / 5))
        self.buttons['Yes'] = self.display_text('Yes', height / 8, snake.GREEN, (2 * width / 5, 3 * height / 4))
        self.buttons['No'] = self.display_text('No', height / 8, snake.RED, (3 * width / 5, 3 * height / 4))
        self.keys['Yes'] = K_RETURN
        self.keys['No'] = K_ESCAPE

class GameOver(Page):

    def __init__(self, game, scores, surface, cell_size):
        super(GameOver, self).__init__(surface)
        width = self.surface.get_width()
        height = self.surface.get_height()
        self.keys['Menu'] = K_ESCAPE
        self.keys['Restart'] = K_RETURN
        self.game = game
        self.scores = scores
        self.display_text('Game Over!', height / 4, snake.RED, (width / 2, height / 5))
        if not self.game == None:
            if len(self.game.snakes) == 1:
                self.display_text('Score: ' + str(self.game.snakes[0].score), height / 8, snake.GREEN, (width / 2, 2 * height / 5))
                self.display_text('Leaderboard:', height / 10, snake.WHITE, (width / 2, 4 * height / 7))
                self.scores.append(self.game.snakes[0].score)
                self.scores = list(set(self.scores))
                self.scores.sort(reverse=True)
                for i in range(0, min(len(self.scores), 3)):
                    if self.scores[i] == self.game.snakes[0].score:
                        color = snake.YELLOW
                    else:
                        color = snake.WHITE
                    self.display_text(str(i + 1) + '. ', height / 15, color, (3 * width / 7, 1 * height / 2 + (i + 2) * height / 11))
                    self.display_text(str(self.scores[i]), height / 15, color, (4 * width / 7, 1 * height / 2 + (i + 2) * height / 11))
            else:
                total = []
                score_height = 3 * height / 7
                lives_height = 4 * height / 7
                line_height = 4 * height / 7 + height / 15
                total_height = 5 * height / 7
                self.display_text('Score:', height / 15, snake.BLUE, (width / 6, score_height))
                self.display_text(str(self.game.snakes[0].score), height / 15, snake.BLUE, (2 * width / 6, score_height))
                self.display_text('Lives:', height / 15, snake.BLUE, (width / 6, lives_height))
                self.display_text(str(self.game.snakes[0].lives * 20), height / 15, snake.BLUE, (2 * width / 6, lives_height))
                pygame.draw.line(self.surface, snake.WHITE, (width / 8, line_height), (3 * width / 8, line_height), 8)
                total.append(self.game.snakes[0].score + self.game.snakes[0].lives * 20)
                self.display_text('Total:', height / 15, snake.BLUE, (width / 6, total_height))
                self.display_text(str(total[0]), height / 15, snake.BLUE, (2 * width / 6, total_height))
                self.display_text('Score:', height / 15, snake.GREEN, (4 * width / 6, score_height))
                self.display_text(str(self.game.snakes[1].score), height / 15, snake.GREEN, (5 * width / 6, score_height))
                self.display_text('Lives:', height / 15, snake.GREEN, (4 * width / 6, lives_height))
                self.display_text(str(self.game.snakes[1].lives * 20), height / 15, snake.GREEN, (5 * width / 6, lives_height))
                pygame.draw.line(self.surface, snake.WHITE, (5 * width / 8, line_height), (7 * width / 8, line_height), 8)
                total.append(self.game.snakes[1].score + self.game.snakes[1].lives * 20)
                self.display_text('Total:', height / 15, snake.GREEN, (4 * width / 6, total_height))
                self.display_text(str(total[1]), height / 15, snake.GREEN, (5 * width / 6, total_height))
                if total[0] > total[1]:
                    self.display_text('Python Won!', height / 8, snake.BLUE, (width / 2, height - 4 * cell_size))
                elif total[0] < total[1]:
                    self.display_text('Viper Won!', height / 8, snake.GREEN, (width / 2, height - 4 * cell_size))
                else:
                    self.display_text('Draw!', height / 8, snake.YELLOW, (width / 2, 17 * height / 18))
        self.buttons['Menu'] = self.display_text('Return', height / 10, snake.WHITE, (2 * cell_size, height - 3 * cell_size), anchor='left')
        self.buttons['Restart'] = self.display_text('Restart', height / 10, snake.WHITE, (width - 2 * cell_size, height - 3 * cell_size), anchor='right')

class UserInterface:

    def __init__(self, screen, cell_size):
        self.screen = screen
        self.game = None
        self.pages = {}
        width = screen.get_width()
        height = screen.get_width()
        self.pages['Settings'] = Settings(self.screen)
        self.pages['Menu'] = Menu(self.screen)
        self.current_page = None
        self.update_flag = True
        self.clock = pygame.time.Clock()
        
    def change_page(self, page):
        if self.current_page == 'GameOver' and len(self.game.snakes) == 1:
            self.save_leaderboard(self.pages[self.current_page].scores, self.game.fps)
        elif self.current_page == 'Settings':
            self.pages[self.current_page].save_settings()
        self.play_music(page)
        self.current_page = page
        self.update()

    def handle_game(self, cell_size):
        python_flag = False
        viper_flag = False
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == KEYDOWN:
                pressed = self.pages[self.current_page].get_keys(event.key)
            else:
                continue
            if pressed == 'Python' and not python_flag:
                if self.game.snakes[0].change_direction(self.pages['Game'].keys['Python'].index(event.key)):
                    python_flag = True
            elif pressed == 'Viper' and len(self.game.snakes) == 2 and not viper_flag:
                if self.game.snakes[1].change_direction(self.pages['Game'].keys['Viper'].index(event.key)):
                    viper_flag = True
            elif pressed == 'Menu':
                self.pages['Confirm'] = Confirm(self.screen, self.screen.copy())
                self.change_page('Confirm')
            elif pressed == 'Pause':
                self.pages['Pause'] = Pause(self.screen, self.screen.copy())
                self.change_page('Pause')
            elif pressed == 'Sound':
                self.pages['Settings'].sound = not self.pages['Settings'].sound
                snake.mute_sounds(self.pages['Settings'].sound)
                self.pages['Settings'].save_settings()
            elif pressed == 'Music':
                self.pages['Settings'].music = not self.pages['Settings'].music
                pygame.mixer.music.set_volume(1 if self.pages['Settings'].music else 0)
                self.pages['Settings'].save_settings()
            else:
                continue

        if self.game.ai:
            player = self.game.snakes[1]
            inputs = player.get_inputs(self.game.apples[0])
            action = np.argmax(self.game.ai.compute_outputs(inputs))
            if action == 0:
                player.turn_right()
            elif action == 1:
                player.turn_left()

        if not self.game.update(self.clock):
            self.pages['GameOver'] = GameOver(self.game, self.load_leaderboard(self.game.fps), self.screen, cell_size)
            self.change_page('GameOver')
        return True

    def handle(self, cell_size):

        self.clock.tick(24)

        if self.pages[self.current_page].get_button(pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # while True:
            # event = pygame.event.wait()
        pressed = None
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == KEYDOWN:
                pressed = self.pages[self.current_page].get_keys(event.key)
                break
            elif event.type == MOUSEBUTTONDOWN:
                pressed = self.pages[self.current_page].get_button(event.pos)
                break
            else:
                continue

        if pressed == 'Single':
            self.game = snake.Game(1, list(DIFFICULTY.values())[self.pages['Settings'].difficulty])
            self.pages['Game'] = GameField(cell_size, self.screen)
            self.pages['Game'].game = self.game
            self.change_page('Game')
        elif pressed == '1v1':
            self.game = snake.Game(2, list(DIFFICULTY.values())[self.pages['Settings'].difficulty])
            self.pages['Game'] = GameField(cell_size, self.screen)
            self.pages['Game'].game = self.game
            self.change_page('Game')
        elif pressed == 'AI':
            self.game = snake.Game(2, list(DIFFICULTY.values())[self.pages['Settings'].difficulty], ai=nn.fromJSON('snake_ai.json'))
            self.pages['Game'] = GameField(cell_size, self.screen)
            self.pages['Game'].game = self.game
            self.change_page('Game')
        elif pressed == 'Settings':
            self.pages['Settings'] = Settings(self.screen)
            self.change_page('Settings')
        elif pressed == 'Leaderboard':
            self.pages['Leaderboard'] = Leaderboard(self.screen)
            self.pages['Leaderboard'].scores[DIFFICULTY['Easy']] = self.load_leaderboard(DIFFICULTY['Easy'])
            self.pages['Leaderboard'].scores[DIFFICULTY['Normal']] = self.load_leaderboard(DIFFICULTY['Normal'])
            self.pages['Leaderboard'].scores[DIFFICULTY['Hard']] = self.load_leaderboard(DIFFICULTY['Hard'])
            self.change_page('Leaderboard')
        elif pressed == 'Difficulty':
            self.pages['Settings'].difficulty = (self.pages['Settings'].difficulty + 1) % 3
        elif pressed == 'Sound':
            self.pages['Settings'].sound = not self.pages['Settings'].sound
            snake.mute_sounds(self.pages['Settings'].sound)
            self.pages['Settings'].save_settings()
        elif pressed == 'Music':
            self.pages['Settings'].music = not self.pages['Settings'].music
            pygame.mixer.music.set_volume(1 if self.pages['Settings'].music else 0)
            self.pages['Settings'].save_settings()
        elif pressed == 'Menu':
            self.pages['Menu'] = Menu(self.screen)
            self.change_page('Menu')
        elif pressed == 'Unpause':
            self.change_page('Game')
        elif pressed == 'Yes':
            self.pages['Menu'] = Menu(self.screen)
            self.change_page('Menu')
        elif pressed == 'No':
            self.change_page('Game')
        elif pressed == 'Restart':
            self.game = self.game.restart()
            self.pages['Game'] = GameField(cell_size, self.screen)
            self.pages['Game'].game = self.game
            self.change_page('Game')
        elif pressed == 'Quit':
            return False
        # else:
            # self.update_flag = False
        return True

    def update(self):
        self.pages[self.current_page].update()
        pygame.display.flip()

    def play_music(self, page):
        if not self.current_page == 'Settings' and not self.current_page == 'Leaderboard':
            if page == 'Game':
                if self.current_page == 'Pause' or self.current_page == 'Confirm':
                    pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.load(MUSIC[self.game.fps])
                    pygame.mixer.music.play(loops=-1)
            elif page == 'Pause' or page == 'Confirm':
                pygame.mixer.music.pause()
            elif not page == 'Settings' and not page == 'Leaderboard':
                pygame.mixer.music.load(MUSIC[page])
                pygame.mixer.music.play(loops=-1)

    def load_leaderboard(self, difficulty):
        scores = []
        try:
            if difficulty == DIFFICULTY['Easy']:
                file = 'resources/.easy'
            elif difficulty == DIFFICULTY['Normal']:
                file = 'resources/.normal'
            elif difficulty == DIFFICULTY['Hard']:
                file = 'resources/.hard'
            with open(file, 'r') as f:
                for line in f:
                    scores.append(int(line.strip()))
        except:
            scores = []
        return scores

    def save_leaderboard(self, scores, difficulty):
        if difficulty == DIFFICULTY['Easy']:
            file = 'resources/.easy'
        elif difficulty == DIFFICULTY['Normal']:
            file = 'resources/.normal'
        elif difficulty == DIFFICULTY['Hard']:
            file = 'resources/.hard'
        with open(file, 'w') as f:
            for s in scores[:3]:
                f.write(str(s) + '\n')

if __name__ == '__main__':

    # Init
    cell_size, screen = snake.init_screen('Python VS Viper')
    snake.init_sounds()

    running = True

    ui = UserInterface(screen, cell_size)
    ui.change_page('Menu')

    # Loop
    while running:
        if ui.current_page == 'Game':
            running = ui.handle_game(cell_size)
        else:
            running = ui.handle(cell_size)
        if ui.update_flag:
            ui.update()
        else:
            ui.update_flag = True
    else:
        pygame.mixer.music.set_volume(0)
        ui.pages['Settings'].save_settings()

    # Quit
    pygame.quit()
