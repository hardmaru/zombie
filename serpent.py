#!/usr/bin/env python
from __future__ import division

"""
Serpent Duel
Copyright (C) 2010 James Garnon

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Serpent Duel Applet Demo
Interphase Pack

Pyjsdl Module
Download Site: http://gatc.ca
"""


import pyjsdl as pygame     #pyjsdl import
#import pygame
import random


class Matrix(object):
    """
    Serpent Duel enviroment.
    """
    def __init__(self, x, y, screen, background):
        self.x, self.y = x, y
        self.screen = screen
        self.background = background
        self.clock = pygame.time.Clock()
        self.level = 2
        self.speed = 2
        self.mode = {'Serpent1':'AI', 'Serpent2':'AI'}
        self.ctrl = {'Pad':'Serpent1', 'Key1':'Serpent1', 'Key2':None}
        self.points = {'Serpent1':0, 'Serpent2':0}
        self.match = 0
        self.auto = True
        self.controls = {}
        self.dirn = {}
        self.dirn['U'] = {'U':'U', 'D':'D', 'L':'L', 'R':'R'}
        self.dirn['D'] = {'U':'D', 'D':'U', 'L':'R', 'R':'L'}
        self.dirn['L'] = {'U':'R', 'D':'L', 'L':'D', 'R':'U'}
        self.dirn['R'] = {'U':'L', 'D':'R', 'L':'U', 'R':'D'}
        self.serpent_control = self.serpent_control_scr
        self.update_rect = []
        self.clear_screen()
        self.active = False

    def start(self):
        """Serpent Duel start."""
        self.treat = pygame.sprite.RenderUpdates()
        self.serpent = {'Serpent1':None, 'Serpent2':None}
        for serpent in self.mode:
            if self.mode[serpent] in ('USER', 'AI'):
                self.serpent_initiate(serpent)
            else:
                self.match = 0
        self.auto = not 'USER' in self.mode.values()
        self.clear_screen()
        for serpent in self.points:
            self.points[serpent] = 0
        self.active = True

    def clear_screen(self):
        """Screen update."""
        self.screen.blit(self.background, (0,0))
        self.draw_edge()
        pygame.display.flip()

    def draw_edge(self):
        """Draw edge around the arena."""
        self.edges = []
        for rect in [ (0,0,self.x,5), (0,self.y-5,self.x,5), (0,0,5,self.y), (self.x-5,0,5,self.y-5) ]:
            edge_rect = pygame.Rect(rect)
            self.edges.append(pygame.draw.rect(self.screen, (43,50,58), edge_rect, 0))
            self.update_rect.append(edge_rect)

    def update_screen(self):
        """Screen update."""
        if self.treat:
            self.treat.clear(self.screen, self.background)
            self.update_rect.extend( self.treat.draw(self.screen) )
        for serpent in self.serpent:
            if not self.serpent[serpent]:
                continue
            self.serpent[serpent].segments.clear(self.screen, self.background)
            self.update_rect.extend( self.serpent[serpent].segments.draw(self.screen) )
        pygame.display.update(self.update_rect)
        self.update_rect = []

    def set_active(self, state=None, pause=False):
        """Activate Serpent Duel."""
        if state is None:
            self.active = not self.active
        else:
            self.active = state
        if self.active:
            if not pause:
                self.start()

    def set_mode(self, serpent, mode):
        """Set serpent control mode."""
        self.mode[serpent] = mode

    def set_control_mode(self, mode):
        """Set control perspective mode."""
        if mode == 'SCR':
            self.serpent_control = self.serpent_control_scr
        elif mode == 'USR':
            self.serpent_control = self.serpent_control_usr

    def set_difficulty(self, level):
        """Set serpent speed."""
        self.level = level
        self.speed = { 1:1, 2:2, 3:5, 4:10 }[level]

    def set_control(self, serpent, control):
        """Set serpent controls."""
        for ctr in self.ctrl:
            if self.ctrl[ctr] == serpent:
                self.ctrl[ctr] = None
        if control == 'Pad/Key1':
            self.ctrl['Pad'] = serpent
            self.ctrl['Key1'] = serpent
        elif control != '-':
            self.ctrl[control] = serpent

    def serpent_control_scr(self, direction, ctrl='Pad'):
        """Serpent control."""
        try:
            self.serpent[self.ctrl[ctrl]].control(direction)
        except:
            pass

    def serpent_control_usr(self, direction, ctrl='Pad'):
        """Serpent control."""
        try:
            dirn = self.serpent[self.ctrl[ctrl]].direction
            direction = self.dirn[dirn][direction]
            self.serpent[self.ctrl[ctrl]].control(direction)
        except:
            pass

    def serpent_initiate(self, identity):
        """Initiate serpent."""
        if identity == 'Serpent1':
            self.serpent['Serpent1'] = Serpent(self, (self.x//2)+50,(self.y//3)+30, identity, self.speed, self.mode['Serpent1'])
        else:
            self.serpent['Serpent2'] = Serpent(self, (self.x//2)-50,(self.y//3)+30, identity, self.speed, self.mode['Serpent2'])

    def pause(self):
        tm = pygame.time.wait(100)

    def update(self):
        """Serpent Duel update."""
        if self.active:
            if not self.treat:
                self.treat.clear(self.screen, self.background)
                self.update_rect.extend( self.treat.draw(self.screen) )
                if self.serpent and random.random() > 0.95:
                    self.treat.add( Treat(self) )
                    self.treat.clear(self.screen, self.background)
                    self.update_rect.extend( self.treat.draw(self.screen) )
            self.treat.update()
            for serpent in self.serpent:
                if not self.serpent[serpent]:
                    continue
                if not self.serpent[serpent].alive:
                    if not self.match and not self.auto:
                        self.active = False
                    else:
                        self.serpent_initiate(self.serpent[serpent].identity)
                        self.draw_edge()
                self.serpent[serpent].update()
                self.serpent[serpent].segments.clear(self.screen, self.background)
                self.update_rect.extend( self.serpent[serpent].segments.draw(self.screen) )
        else:   
            self.pause()


class Serpent(object):
    """
    Serpent.
    """
    def __init__(self, matrix, x, y, identity, speed, mode):
        self.matrix = matrix
        self.identity = identity
        self.mode = mode
        self.x, self.y = x, y
        self.speed = speed
        self.DIR = { 'U':(0,-1), 'D':(0,1), 'L':(-1,0), 'R':(1,0) }
        self.DEG = { 'U':0, 'D':180, 'L':90, 'R':-90 }
        if self.identity == 'Serpent1':
            self.direction = 'R'
        else:
            self.direction = 'L'
        self.new_direction = None
        self.step, self.growing, self.rate = 0, 0, 0
        self.segments = pygame.sprite.RenderUpdates()
        self.segment_spares = []
        self.serpent_body = {}
        self.grow(self.x, self.y, self.DIR[self.direction])
        self.serpent_body[0].image = self.serpent_body[0].images[self.identity+'_head'][self.direction]
        self.scan_rect = pygame.sprite.Sprite()
        self.scan_rect.rect = pygame.Rect(0,0,10,10)
        self.scan_detect = False
        self.pause = 20
        self.active = True
        self.alive = True

    def grow(self, x, y, direction, number=5):
        """Serpent generate."""
        for num in range(0,number*10,10):
            if not self.segment_spares:
                self.segment_spares.append(Segment(self.identity, (0,0)))
            segment = self.segment_spares.pop()
            segment.x, segment.y = ((x-(direction[0]*num)),(y-(direction[1]*num)))
            segment.x_pre, segment.y_pre = segment.x, segment.y
            segment.rect.__setattr__('center',(segment.x,segment.y))
            segment.direction = direction
            segment.speed = self.speed
            self.segments.add(segment)
            self.serpent_body[len(self.serpent_body)] = segment

    def control(self, direction):
        """Serpent Control."""
        for dirn in ( ('L','R'),('U','D') ):
            if (direction in dirn) and (self.direction not in dirn):
                self.new_direction = direction
                self.last_move = direction

    def move(self):
        """Serpent move."""
        if self.mode == 'AI':
            self.move_auto()
        self.step += 1
        if self.step >= 10/self.speed:
            for i in range(len(self.serpent_body)-1, 0, -1):
                self.serpent_body[i].direction = self.serpent_body[i-1].direction
            if self.new_direction:
                self.direction = self.new_direction
                self.serpent_body[0].direction = self.DIR[self.direction]
                self.serpent_body[0].image = self.serpent_body[0].images[self.identity+'_head'][self.direction]
                self.new_direction = None
            self.step = 0
        self.segments.update()

    def move_auto(self):
        """Serpent automatic move."""
        def collide(direction):
            direction = self.DIR[direction]
            self.scan_rect.rect.x = self.serpent_body[0].x+(direction[0]*10) - (self.scan_rect.rect.width//2)
            self.scan_rect.rect.y = self.serpent_body[0].y+(direction[1]*10) - (self.scan_rect.rect.height//2)
            collide = False
            for serpent in self.matrix.serpent:
                if not self.matrix.serpent[serpent]:
                    continue
                if pygame.sprite.spritecollideany(self.scan_rect, self.matrix.serpent[serpent].segments):
                    collide = True
                    return collide
            if self.scan_rect.rect.collidelist(self.matrix.edges) != -1:
                collide = True
                return collide
            return collide
        try:
            treat = [treat for treat in self.matrix.treat][0]
        except IndexError:
            treat = None
        if treat and not self.new_direction:
            x, y = self.serpent_body[0].x, self.serpent_body[0].y
            if x <= treat.x and y <= treat.y:
                direct = ('R','D')
            elif x <= treat.x and y >= treat.y:
                direct = ('R','U')
            elif x >= treat.x and y <= treat.y:
                direct = ('L','D')
            elif x >= treat.x and y >= treat.y:
                direct = ('L','U')
            if self.direction not in direct:
                new_direction = []
                for direction in direct:
                    if not collide(direction):
                        new_direction.append(direction)
                if new_direction:
                    self.control(random.choice(new_direction))
        if collide(self.direction):
            self.new_direction = None
            new_direction = []
            if self.direction in ('U','D'):
                for direction in ('L','R'):
                    if not collide(direction):
                        new_direction.append(direction)
            elif self.direction in ('L','R'):
                for direction in ('U','D'):
                    if not collide(direction):
                        new_direction.append(direction)
            if new_direction:
                self.control(random.choice(new_direction))
            self.scan_detect = True
        else:
            self.scan_detect = False

    def growth(self):
        """Serpent growth."""
        if pygame.sprite.spritecollide(self.serpent_body[0], self.matrix.treat, False, pygame.sprite.collide_mask):
            points = 0
            treat = [treat for treat in self.matrix.treat][0]
            if treat.identity == 'Food':
                if self.growing >= 0:
                    self.growing += 5
                else:
                    points += 5
            elif treat.identity == 'Bonus':
                if len(self.serpent_body) > 5 and self.growing >= 0:
                    self.growing = -(len(self.serpent_body)-5)
                    self.rate = 0
                points += 10
            if points:
                self.set_points(points)
            self.matrix.treat.empty()
        if self.growing:
            self.rate += 1
            if self.rate > 10/self.speed:
                points = 0
                if self.growing > 0:
                    tail = self.serpent_body[len(self.serpent_body)-1]
                    self.grow(tail.x-(tail.direction[0]*10), tail.y-(tail.direction[1]*10), tail.direction, number=1)
                    self.growing -= 1
                    points += 1
                else:
                    tail = len(self.serpent_body)-1
                    self.segment_spares.append(self.serpent_body[tail])
                    self.segments.remove(self.serpent_body[tail])
                    del self.serpent_body[tail]
                    self.growing += 1
                    points += 1
                self.rate = 0
                if points:
                    self.set_points(points)

    def set_points(self, points):
        """Set serpent points."""
        self.matrix.points[self.identity] += points
        if self.matrix.match and not self.matrix.auto:
            if self.matrix.points[self.identity] >= self.matrix.match and not self.growing:
                self.matrix.set_active(False)

    def collision(self):
        """Check serpent collision."""
        if self.mode == 'AI' and not self.scan_detect:
            return
        for serpent in self.matrix.serpent:
            if not self.matrix.serpent[serpent]:
                continue
            for segment in pygame.sprite.spritecollide(self.serpent_body[0], self.matrix.serpent[serpent].segments, False):
                if segment not in (self.serpent_body[0], self.serpent_body[1]):
                    return True
        if self.serpent_body[0].rect.collidelist(self.matrix.edges) != -1:
            return True
        return False

    def update(self):
        """Serpent update."""
        if self.active:
            self.move()
            self.growth()
            self.active = not self.collision()
            if not self.active:
                self.serpent_body[0].image = self.serpent_body[0].images[self.identity+'_ko'][self.direction]
                if (self.matrix.match or self.matrix.auto):
                    if len(self.serpent_body) > 5:
                        penalty = 5+(len(self.serpent_body)//5)
                        if self.matrix.points[self.identity] - penalty < 0:
                            penalty = self.matrix.points[self.identity]
                        self.set_points(-penalty)
        else:
            if not self.matrix.match and not self.matrix.auto:
                self.alive = False
            else:
                self.pause -= 1
                if not self.pause:
                    self.segment_spares.extend(self.segments.sprites())
                    self.segments.empty()
                    self.alive = False


class Segment(pygame.sprite.Sprite):
    """
    Serpent segment.
    """
    images = None
    mask = None
    def __init__(self, serpent, position, direction=None, speed=0):
        pygame.sprite.Sprite.__init__(self)
        self.type = {'Serpent1':(0,0,255), 'Serpent2':(255,0,0)}
        if not Segment.images:
            Segment.images = {}
            for species in ('Serpent1', 'Serpent2'):
                Segment.images[species] = pygame.Surface((10,10))
                pygame.draw.circle(Segment.images[species], self.type[species], (5,5), 6, 0)
                Segment.images[species].set_colorkey((0,0,0))
                segment_head = Segment.images[species].copy()
                pygame.draw.line(segment_head, (0,255,0), (2,2), (0,5), 3)
                pygame.draw.line(segment_head, (0,255,0), (7,2), (9,5), 3)
                segment_ko = Segment.images[species].copy()
                pygame.draw.circle(segment_ko, (0,255,0), (2,3), 2, 1)
                pygame.draw.circle(segment_ko, (0,255,0), (8,3), 2, 1)
                Segment.images[species+'_head'] = {}
                Segment.images[species+'_ko'] = {}
                deg = { 'U':0, 'D':180, 'L':90, 'R':-90 }
                for dirn in ('U','D','L','R'):
                    Segment.images[species+'_head'][dirn] = pygame.transform.rotate(segment_head, deg[dirn])
                    Segment.images[species+'_ko'][dirn] = pygame.transform.rotate(segment_ko, deg[dirn])
            Segment.mask = pygame.mask.from_surface(Segment.images['Serpent1'])
        self.x, self.y = position
        self.direction = direction
        self.speed = speed
        self.image = Segment.images[serpent]
        self.rect = self.image.get_rect(center=(self.x,self.y))
        self.x_pre, self.y_pre = self.x, self.y
        self.mask = Segment.mask

    def update(self):
        """Serpent segment update."""
        self.x += self.direction[0]*self.speed
        self.y += self.direction[1]*self.speed
        self.rect.move_ip(self.x-self.x_pre, self.y-self.y_pre)
        self.x_pre, self.y_pre = self.x, self.y


class Treat(pygame.sprite.Sprite):
    """
    Serpent nourishment.
    """
    images = None
    mask = None
    def __init__(self, matrix):
        pygame.sprite.Sprite.__init__(self)
        self.matrix = matrix
        if not Treat.images:
            Treat.images = {}
            Treat.mask = {}
            Treat.images['Food'] = pygame.Surface((15,15))
            pygame.draw.circle(Treat.images['Food'], (0,255,0), (7,7), 5, 0)
            Treat.images['Food'].set_colorkey((0,0,0))
            Treat.images['Bonus'] = pygame.Surface((15,15))
            pygame.draw.circle(Treat.images['Bonus'], (255,0,0), (7,10), 5, 0)
            pygame.draw.arc(Treat.images['Bonus'], (0,255,0), (-7,0,15,15), 0, 1, 1)
            Treat.images['Bonus'].set_colorkey((0,0,0))
            Treat.mask['Food'] = pygame.mask.from_surface(Treat.images['Food'])
            Treat.mask['Bonus'] = pygame.mask.from_surface(Treat.images['Bonus'])
        placed = False
        while not placed:
            x, y = random.randrange(20,self.matrix.x-20), random.randrange(20,self.matrix.y-20)
            self.x, self.y = x, y
            if random.random() > 0.1+(matrix.clock.get_time()/300.0):
                self.identity = 'Food'
                self.duration = random.randrange(800,2000)
            else:
                self.identity = 'Bonus'
                self.duration = random.randrange(400,800)
            self.duration //= matrix.level
            self.image = Treat.images[self.identity]
            self.rect = self.image.get_rect(center=(x,y))
            self.mask = Treat.mask[self.identity]
            disrupt = False
            for serpent in self.matrix.serpent:
                if not self.matrix.serpent[serpent]:
                    continue
                if pygame.sprite.spritecollideany(self, self.matrix.serpent[serpent].segments):
                    disrupt = True
                    break
            if not disrupt:
                placed = True

    def update(self):
        """Nourishment update."""
        self.duration -= 1
        if not self.duration:
            self.matrix.treat.remove(self)


class Control(object):
    def __init__(self, matrix):
        self.matrix = matrix
        pygame.font.init()
        font = pygame.font.get_default_font()
        self.font = pygame.font.Font(font, 24)
        self.font2 = pygame.font.Font(font, 14)
        self.matrix_start = False
        self.quit_request = False
        pygame.event.set_blocked(pygame.MOUSEMOTION)
        self.quit = False
        self.pause = True
        self.pause_program('Serpent Duel', 'Click to run/pause', '[r]estart [p]ause [q]uit')
    def pause_program(self, text1, text2=None, text3=None):
        self.matrix.screen.fill((0,0,0))
        text = self.font.render(text1, True, (100,100,100))
        size = self.font.size(text1)
        self.matrix.screen.blit(text, (self.matrix.x//2-size[0]//2, (self.matrix.y//2-size[1]//2)-12))
        if text2:
            text = self.font2.render(text2, True, (100,100,100))
            size = self.font2.size(text2)
            self.matrix.screen.blit(text, (self.matrix.x//2-size[0]//2, (self.matrix.y//2-size[1]//2)+25))
        if text3:
            text = self.font2.render(text3, True, (100,100,100))
            size = self.font2.size(text3)
            self.matrix.screen.blit(text, (self.matrix.x//2-size[0]//2, (self.matrix.y//2-size[1]//2)+40))
        pygame.display.flip()
        self.matrix.active = False
    def matrix_control(self):
        if not self.pause:
            self.pause_program('Serpent Duel', 'Click to run/pause', '[r]estart [p]ause [q]uit')
            self.pause = True
        else:
            if self.matrix_start:
                self.matrix.clear_screen()
                self.matrix.update_screen()
                self.matrix.active = True
            else:
                self.matrix.start()
                self.matrix_start = True
            self.quit_request = False
            self.pause = False
    def check_control(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.matrix_control()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.matrix_control()
                elif event.key == pygame.K_r:
                    self.pause = False
                    self.quit_request = False
                    self.matrix.start()
                elif event.key == pygame.K_q:
                    self.pause_program('Serpent Duel', 'Quit (y/n)?')
                    self.pause = True
                    self.quit_request = True
                elif event.key in (pygame.K_y, pygame.K_n):
                    if self.quit_request:
                        if event.key == pygame.K_n:
                            self.matrix_control()
                        else:
                            self.matrix.screen.fill((0,0,0))
                            pygame.display.flip()
                            pygame.time.delay(10)
                            pygame.quit()
                            self.quit = True
            elif event.type == pygame.QUIT:
                self.quit = True
        return self.quit


def setup(x=500,y=500,screen=None):
    pygame.display.init()   #pygame.init()
    pygame.display.set_caption('Serpent Duel')
    if not screen:
        screen = pygame.display.set_mode((x,y))
    background = pygame.Surface((x,y))
    background.fill((50,50,50))
    for line in range(0,300,25):
        pygame.draw.line(background, (43,50,58), (0,line), (400,line), 1)
    for line in range(0,400,25):
        pygame.draw.line(background, (43,50,58), (line,0), (line,300), 1)
    matrix = Matrix(x,y,screen,background)
    control = Control(matrix)
    return matrix, control


def program_exec(matrix, control):
    matrix.update_rect = []
    matrix.update()
    pygame.display.update(matrix.update_rect)
    matrix.clock.tick(30)
    quit = control.check_control()
    return quit


def run():      #pyjsdl executed function
    program_exec(matrix, control)


matrix, control = None, None


def main():
    global matrix, control
    matrix, control = setup(400,300)
    pygame.display.setup(run)     #pyjsdl setup


if __name__ == '__main__':
    main()

