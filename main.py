import pygame
import os
import sys
import random


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()

    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


class Sprite(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.rect = None


screen_rect = (0, 0, 520, 800)
pygame.init()
screen_size = (520, 800)
screen = pygame.display.set_mode(screen_size)
FPS = 50
player = None
running = True

cats = [[] for i in range(12)]
clock = pygame.time.Clock()
cat_images = {
    '.': load_image('cat1.png'),
    '..': load_image('cat2.png'),
    '...': load_image('cat3.png'),
    '....': load_image('cat4.png')
}
cat_height = 50
cat_width = 50
sound = pygame.mixer.Sound("data/Achievement_Sound_Effect.wav")


class Particle(pygame.sprite.Sprite):
    fire = [load_image("star.png")]
    for scale in (10, 15, 25):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))
    fire.remove(fire[0])

    def __init__(self, pos, dx, dy):
        super().__init__(all_particles)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        self.gravity = 1

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(screen_rect):
            self.kill()


def create_particles(position):
    particle_count = 10
    numbers = range(-6, 6)
    for i in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, group):
        super().__init__(group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]

        self.left = 10
        self.top = 10
        self.cell_size = 30

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        x = self.left
        y = self.top
        pygame.draw.rect(screen, (0, 0, 0), (x, y, self.cell_size * self.width, self.cell_size * self.height), 0)
        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(screen, pygame.Color('white'),
                                 (x + 1, y + 1, self.cell_size - 2, self.cell_size - 2), 0)
                x += self.cell_size
            x = self.left
            y += self.cell_size

    def get_cell(self, pos):
        if pos[0] < self.left or pos[0] > self.left + self.width * self.cell_size:
            return None
        elif pos[1] < self.top or pos[1] > self.top + self.height * self.cell_size:
            return None
        pos1 = [0, 0]
        pos1[0] = (pos[0] - self.left) // self.cell_size
        pos1[1] = (pos[1] - self.top) // self.cell_size
        return tuple(pos1)

    def get_cat(self, pos):
        cell = self.get_cell(pos)
        if cell:
            for cat in cats[cell[1]]:
                if cat.rect.collidepoint(pos):
                    return cat


def terminate():
    pygame.quit()
    sys.exit()


class SpriteGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()


sprite_group = SpriteGroup()
all_particles = pygame.sprite.Group()
cat_gif1 = pygame.sprite.Group()
cat_gif2 = pygame.sprite.Group()


def final_screen(string):
    if string[0] == 'You lost':
        sad_cat = AnimatedSprite(load_image("sad_cat.png"), 4, 2, 100, 270, cat_gif2)
    else:
        happy_cat = AnimatedSprite(load_image("happy_cat.png"), 6, 3, 175, 347, cat_gif2)
    pygame.time.set_timer(pygame.USEREVENT + 2, 50)
    while True:
        fon = pygame.transform.scale(load_image('fon.png'), screen_size)
        screen.blit(fon, (0, 0))
        font = pygame.font.Font('data/OdinRounded-Yd82.ttf', 50)
        string_rendered = font.render(string[0], True, pygame.Color('white'))
        screen.blit(string_rendered, ((520 - string_rendered.get_width()) // 2, 140, 150, 40))
        font = pygame.font.Font('data/OdinRounded-Yd82.ttf', 40)
        if len(string) == 2:
            string_rendered = font.render(string[1], True, pygame.Color('white'))
            screen.blit(string_rendered, ((520 - string_rendered.get_width()) // 2, 210, 120, 40))
        else:
            string_rendered = font.render(string[1], True, pygame.Color('white'))
            screen.blit(string_rendered, ((520 - string_rendered.get_width()) // 2, 210, 120, 40))
            string_rendered = font.render(string[2], True, pygame.Color('white'))
            screen.blit(string_rendered, ((520 - string_rendered.get_width()) // 2, 260, 120, 40))
        font = pygame.font.Font('data/OdinRounded-Yd82.ttf', 40)
        string_rendered = font.render('Start again', True, pygame.Color('white'))
        rect2 = pygame.Rect(((520 - string_rendered.get_width()) // 2) - 6, 617, 205, 58)
        pygame.draw.rect(screen, "white", rect2, 5, border_radius=15)
        screen.blit(string_rendered, ((520 - string_rendered.get_width()) // 2, 630, 120, 40))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if rect2.collidepoint(event.pos):
                    global points, curlev, walking_cat, current_cat, cats, board
                    sprite_group.empty()
                    cats = [[] for _ in range(12)]
                    level_file = start_screen()
                    board = Board(8, 12)
                    board.set_view(65, 142, 50)
                    level_map = load_level(level_file)
                    curlev = generate_level(level_map)
                    current_cat = None
                    points = 0
                    sprite_group.update()
                    pygame.time.set_timer(pygame.USEREVENT + 1, 50)
                    cat_gif2.empty()
                    return
            elif event.type == pygame.USEREVENT + 2:
                cat_gif2.update()
        cat_gif2.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


class Cat(Sprite):
    def __init__(self, cat_type, pos_x, pos_y):
        super().__init__(sprite_group)
        self.image = cat_images[cat_type]
        self.rect = self.image.get_rect().move(
            board.left + cat_width * pos_x, board.top + cat_height * pos_y)
        self.board_pos = [pos_x, pos_y]
        self.length = len(cat_type)

    def move(self, direction):
        global count
        if direction == 'left' and self.board_pos[0] != 0:
            if board.board[self.board_pos[1]][self.board_pos[0] - 1] == 0:
                board.board[self.board_pos[1]][self.board_pos[0] - 1] = 1
                board.board[self.board_pos[1]][self.board_pos[0] + self.length - 1] = 0
                self.board_pos[0] -= 1
                self.rect = self.image.get_rect().move(
                    board.left + cat_width * self.board_pos[0], board.top + cat_height * self.board_pos[1])
                count -= 1

        elif direction == 'right' and self.board_pos[0] + self.length < 8:
            if board.board[self.board_pos[1]][self.board_pos[0] + self.length] == 0:
                board.board[self.board_pos[1]][self.board_pos[0]] = 0
                board.board[self.board_pos[1]][self.board_pos[0] + self.length] = 1
                self.board_pos[0] += 1
                self.rect = self.image.get_rect().move(
                    board.left + cat_width * self.board_pos[0], board.top + cat_height * self.board_pos[1])
                count += 1
    def up(self):
        if self.board_pos[1] > 1:
            for i in range(self.length):
                board.board[self.board_pos[1]][self.board_pos[0] + i] = 0
                board.board[self.board_pos[1] - 1][self.board_pos[0] + i] = 1
            cats[self.board_pos[1]].remove(self)
            self.board_pos[1] -= 1
            cats[self.board_pos[1]].append(self)
            self.rect = self.image.get_rect().move(
                board.left + cat_width * self.board_pos[0],
                board.top + cat_height * self.board_pos[1])

    def update(self):
        if self.board_pos[1] != 11:
            down = True
            while self.board_pos[1] != 11 and down:
                for i in range(self.length):
                    if board.board[self.board_pos[1] + 1][self.board_pos[0] + i] == 1:
                        down = False
                if down:
                    for i in range(self.length):
                        board.board[self.board_pos[1]][self.board_pos[0] + i] = 0
                        board.board[self.board_pos[1] + 1][self.board_pos[0] + i] = 1
                    cats[self.board_pos[1]].remove(self)
                    self.board_pos[1] += 1
                    cats[self.board_pos[1]].append(self)
                    self.rect = self.image.get_rect().move(
                        board.left + cat_width * self.board_pos[0], board.top + cat_height * self.board_pos[1])

    def delete(self):
        global points
        create_particles((self.rect.x, self.rect.y))
        for i in range(self.length):
            board.board[self.board_pos[1]][self.board_pos[0] + i] = 0
        points += self.length * 5
        self.kill()


def start_screen():
    fon = pygame.transform.scale(load_image('fon.png'), screen_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font('data/OdinRounded-Yd82.ttf', 55)
    rect1 = pygame.Rect(190, 200, 140, 55)
    rect2 = pygame.Rect(190, 280, 140, 55)
    rect3 = pygame.Rect(190, 360, 140, 55)
    string_rendered = font.render("Block slide", True, pygame.Color('white'))
    screen.blit(string_rendered, (145, 110))
    font = pygame.font.Font('data/OdinRounded-Yd82.ttf', 40)
    string_rendered = font.render("?", True, pygame.Color('white'))
    screen.blit(string_rendered, (480, 20))
    pygame.draw.circle(screen, pygame.Color('white'), (490, 35), 23, width=5)
    string_rendered = font.render('Level 1', True, pygame.Color('white'))
    screen.blit(string_rendered, (205, 210, 120, 40))
    pygame.draw.rect(screen, "white", rect1, 5, border_radius=15)
    pygame.draw.rect(screen, "white", rect2, 5, border_radius=15)
    pygame.draw.rect(screen, "white", rect3, 5, border_radius=15)
    string_rendered = font.render('Level 2', True, pygame.Color('white'))
    screen.blit(string_rendered, (205, 290, 120, 40))
    string_rendered = font.render('Level 3', True, pygame.Color('white'))
    screen.blit(string_rendered, (205, 370, 120, 40))
    rect4 = pygame.Rect(467, 12, 46, 46)
    rect5 = [60, 430, 120, 40]
    intro_written = False
    intro_text = ['How to play:', '- use mouse to select block', '- use arrows to move it',
                  '- press Enter to place']
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if rect1.collidepoint(event.pos):
                    return 'catmap1.txt'
                elif rect2.collidepoint(event.pos):
                    return 'catmap2.txt'
                elif rect3.collidepoint(event.pos):
                    return 'catmap3.txt'
                elif rect4.collidepoint(event.pos):
                    if not intro_written:
                        for line in intro_text:
                            font = pygame.font.Font('data/OdinRounded-Yd82.ttf', 35)
                            string_rendered = font.render(line, True, pygame.Color('white'))
                            screen.blit(string_rendered, rect5)
                            rect5[1] += 50
                            intro_written = True
                    else:
                        fon = pygame.transform.scale(load_image('fon.png'), screen_size)
                        screen.blit(fon, (0, 0))
                        font = pygame.font.Font('data/OdinRounded-Yd82.ttf', 55)
                        string_rendered = font.render("Block slide", True, pygame.Color('white'))
                        screen.blit(string_rendered, (145, 110))
                        font = pygame.font.Font('data/OdinRounded-Yd82.ttf', 40)
                        string_rendered = font.render("?", True, pygame.Color('white'))
                        screen.blit(string_rendered, (480, 20))
                        pygame.draw.circle(screen, pygame.Color('white'), (490, 35), 23, width=5)
                        string_rendered = font.render('Level 1', True, pygame.Color('white'))
                        screen.blit(string_rendered, (205, 210, 120, 40))
                        pygame.draw.rect(screen, "white", rect1, 5, border_radius=15)
                        pygame.draw.rect(screen, "white", rect2, 5, border_radius=15)
                        pygame.draw.rect(screen, "white", rect3, 5, border_radius=15)
                        string_rendered = font.render('Level 2', True, pygame.Color('white'))
                        screen.blit(string_rendered, (205, 290, 120, 40))
                        string_rendered = font.render('Level 3', True, pygame.Color('white'))
                        screen.blit(string_rendered, (205, 370, 120, 40))
                        rect4 = pygame.Rect(467, 12, 46, 46)
                        rect5 = [60, 430, 120, 40]
                        intro_written = False
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
        return [line[1:-1].split('/') for line in level_map]


def line_check():
    to_delete = []
    for line in cats:
        c = 0
        for cat in line:
            c += cat.length
        if c == 8:
            to_delete.append(line)
    if to_delete:
        sprite_group.update()
        all_particles.update()
        board.render(screen)
        sprite_group.draw(screen)
        all_particles.draw(screen)
        cat_gif1.draw(screen)
        pygame.display.flip()
        pygame.time.delay(350)
    return to_delete


def add_layer(n, level):
    global curlev
    x = 0
    c1 = []
    check_to_del()
    if board.board[1] == [0, 0, 0, 0, 0, 0, 0, 0]:
        for row in cats:
            cat_count = len(row)
            for _ in range(cat_count):
                row[0].up()
        if n == len(level):
            n = 0
            curlev = 0
        for cat in level[n]:
            if cat:
                c1.append(Cat(cat, x, 11))
                x += len(cat)
                for i in range(len(cat)):
                    board.board[11][x - i - 1] = 1
            else:
                x += 1
                board.board[11][x - 1] = 0
        cats[11] = c1
    else:
        if level_file == 'catmap1.txt':
            best_scores = 'data/best_scores1.txt'
        elif level_file == 'catmap2.txt':
            best_scores = 'data/best_scores2.txt'
        else:
            best_scores = 'data/best_scores3.txt'
        with open(best_scores, 'r') as file:
            scores = [int(i) for i in file.readlines()]
        message = ['You lost']
        if max(scores) <= points:
            message.append(f'New best score: {points}')
        else:
            message.append(f'Score: {points}')
            message.append(f'Best score: {max(scores)}')
        scores.append(points)
        with open(best_scores, 'w') as file:
            file.writelines([str(i) + '\n' for i in sorted(scores)])
        final_screen(message)


def check_to_del():
    row_del = line_check()
    layers_cleared = 0
    while row_del:
        for row in row_del:
            for cat in row:
                cat.delete()
            cats[cats.index(row)] = []
        for i in range(13):
            sprite_group.update()

        pygame.mixer.Sound.play(sound)
        pygame.mixer.music.stop()
        layers_cleared += 1
        row_del = line_check()


def generate_level(level):
    for n in range(5):
        x = 0
        c1 = []
        for cat in level[n]:
            if cat:
                c1.append(Cat(cat, x, 12 - n - 1))
                x += len(cat)
                for i in range(len(cat)):
                    board.board[12 - n - 1][x - i - 1] = 1
            else:
                x += 1
                board.board[12 - n - 1][x - 1] = 0
        cats[12 - n - 1] = c1
    return 4


level_file = start_screen()
board = Board(8, 12)
board.set_view(65, 142, 50)
level_map = load_level(level_file)
curlev = generate_level(level_map)
current_cat = None
walking_cat = AnimatedSprite(load_image("cat.png"), 5, 6, 160, 0, cat_gif1)
points = 0
sprite_group.update()
pygame.time.set_timer(pygame.USEREVENT+1, 50)
c = 0
count = 0
string_on_screen = False
while running:
    fon = pygame.transform.scale(load_image('fon.png'), screen_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font('data/OdinRounded-Yd82.ttf', 30)
    string_rendered = font.render(f'Points: {points}', True, pygame.Color('black'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = 40
    intro_rect.x = 10
    screen.blit(string_rendered, intro_rect)
    row_del = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                if current_cat:
                    current_cat.move("left")
            elif event.key == pygame.K_RIGHT:
                if current_cat:
                    current_cat.move("right")
            elif event.key == pygame.K_RETURN:
                string_on_screen = False
                sprite_group.update()
                count = 0
                sprite_group.draw(screen)
                check_to_del()
                for cat in reversed(list(sprite_group)):
                    cat.update()
                if board.board == [[0] * 8 for _ in range(12)]:
                    final_screen(['You won', f'Score: {points}'])
                add_layer(curlev, level_map)
                c += 1
                curlev += 1
                check_to_del()
                for cat in reversed(list(sprite_group)):
                    cat.update()
                sprite_group.update()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if count == 0:
                string_on_screen = False
                current_cat = board.get_cat(event.pos)
            else:
                string_on_screen = True
        elif event.type == pygame.USEREVENT + 1:
            cat_gif1.update()
    if string_on_screen:
        font = pygame.font.Font('data/OdinRounded-Yd82.ttf', 20)
        string_rendered = font.render(f'You have to press Enter before moving another block', True, pygame.Color('white'))
        screen.blit(string_rendered, (60, 750))
    check_to_del()
    all_particles.update()
    clock.tick(FPS)
    board.render(screen)
    sprite_group.draw(screen)
    all_particles.draw(screen)
    cat_gif1.draw(screen)
    pygame.display.flip()
pygame.quit()
