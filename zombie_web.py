#!/usr/bin/env python

"""
Zombie game:  test implementation of A* Search
derived from James Garnon's Serpent Duel's skeleton code

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
"""

import pyjsdl as pygame     #pyjsdl import
#import pygame
import random
#from numpy import ndarray as nd_array
#import pyjsdl as pygame     #pyjsdl import
#import pyjsdl.pyjsarray as np
#from numpy import ndarray as ndarray

#Global constants

class nd_array:
    def __init__(self, dim, value = 0):
        self.height = dim[0]
        self.width = dim[1]
        self.data = [[value for col in range(self.width)] for row in range(self.height)]
        #self.data = ndarray(dim)
        #self.data.fill(value)
    def fill(self, value = 0):
        #for row in range(self.height):
        #    for col in range(self.width):
        #        self.data[row][col] = value
        self.data = [[value for col in range(self.width)] for row in range(self.height)]

class Queue:
    """
    A simple implementation of a FIFO queue.
    """
    def __init__(self):
        self._items = []

    def __len__(self):
        return len(self._items)
    
    def __iter__(self):
        for item in self._items:
            yield item

    def __str__(self):
        return str(self._items)

    def enqueue(self, item):       
        self._items.append(item)

    def dequeue(self):
        return self._items.pop(0)

    def clear(self):
        self._items = []

class Thing:
    """ either a wall, zombie, or human """
    def __init__(self, category, row, col):
        self.category = category
        self.row = row
        self.col = col
        self.rest_time = 0
        self.life = LIFE

class ZombieGrid:
    def __init__(self, grid_height=48, grid_width=48):
        self.grid = nd_array((grid_height,grid_width))
        self.grid.fill(0)
        self.grid_height = grid_height
        self.grid_width = grid_width

    def set_value(self, row, col, value):
        self.grid.data[row][col] = value

    def get_value(self, row, col):
        return self.grid.data[row][col]

    def clear_grid(self):
        self.grid = nd_array((self.grid_height,self.grid_width), 0)

    def update_grid(self, things):
        for thing in things:
            self.set_value(thing.row, thing.col, thing.category)

    def four_neighbors(self, row, col):
        locs = []
        poss = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for pos in poss:
            coor = ((pos[0]+row)%HEIGHT, (pos[1]+col)%WIDTH)
            if self.get_value(coor[0], coor[1]) != WALL:
                locs.append(coor)
        return locs

    def eight_neighbors(self, row, col):
        locs = []
        poss = [(1, 0), (-1, 0), (0, 1), (0, -1), (-1, -1), (1, 1), (1, -1), (-1, 1)]
        for pos in poss:
            coor = ((pos[0]+row)%HEIGHT, (pos[1]+col)%WIDTH)
            if self.get_value(coor[0], coor[1]) != WALL:
                locs.append(coor)
        return locs

    def compute_distance_field(self, zombies, humans, entity_type):
        """
        Function computes a 2D distance field
        Distance at member of entity_queue is zero
        Shortest paths avoid obstacles and use distance_type distances
        """
        visited = nd_array((self.grid_height, self.grid_width), 0)
        max_dist = self.grid_height * self.grid_width
        dist_field = nd_array((self.grid_height, self.grid_width), max_dist)

        boundary = Queue()
        entity_list = humans

        if entity_type == ZOMBIE:
            entity_list = zombies

        for entity in entity_list:
            boundary.enqueue((entity.row,entity.col))
            visited.data[entity.row][entity.col] = 1
            dist_field.data[entity.row][entity.col] = 0
            
        while len(boundary) > 0:
            cell = boundary.dequeue()
            current_dist = dist_field.data[cell[0]][cell[1]]
            neighbors = []
            if entity_type == ZOMBIE:  # humans have to make a move
                neighbors = self.four_neighbors(cell[0], cell[1])
            else: # zombies have to make a move
                neighbors = self.eight_neighbors(cell[0], cell[1])
            for neighbor in neighbors:
                if visited.data[neighbor[0]][neighbor[1]]==0 and self.get_value(neighbor[0], neighbor[1]) != WALL:
                    visited.data[neighbor[0]][neighbor[1]] = 1
                    boundary.enqueue(neighbor)
                    dist_field.data[neighbor[0]][neighbor[1]] = current_dist + 1

        return dist_field

def move_things(things, grid, field, category):
    for thing in things:
        if thing.rest_time > 0:
            thing.rest_time -= 1
            continue
        if category == HUMAN: # human move
            locs = grid.four_neighbors(thing.row, thing.col)
        else: # zombie move
            locs = grid.eight_neighbors(thing.row, thing.col)
        if len(locs) > 0:
            loc_choices = []
            best_score = grid.grid_width*grid.grid_height
            if category == HUMAN:
                best_score = -1

            for loc in locs:
                score = field.data[loc[0]][loc[1]]

                if ((score < best_score) and (category == ZOMBIE)) or ((score > best_score) and (category == HUMAN)):
                    best_score = score
                    loc_choices = []
                    loc_choices.append(loc)
                elif score == best_score:
                    loc_choices.append(loc)
            if len(loc_choices) > 0:
                loc = random.choice(loc_choices)
                thing.row = loc[0]
                thing.col = loc[1]

def check_collision(zombies, humans):
    new_humans = []
    # debug:
    #for zombie in zombies:
    #    print "zombie position (", zombie.row,",",zombie.col,")"
    #for human in humans:
    #    print "human position (", human.row,",",human.col,")"
    for zombie in zombies:
        for human in humans:
            if (zombie.row == human.row) and (zombie.col == human.col):
                zombie.life = LIFE*2
                human.category = ZOMBIE

    while len(humans) > 0:
        human = humans.pop()
        if human.category == ZOMBIE:
            zombies.append(human)
        else:
            new_humans.append(human)
    while len(new_humans) > 0:
        human = new_humans.pop()
        humans.append(human)



def put_in_rest(things):
    # if there is overlap, randomly put in a delay
    N = len(things)
    if N <= 1:
        return
    for i in range(0,N):
        thing1 = things[i]
        for j in range(i+1, N):
            thing2 = things[j]
            if (thing1.row == thing2.row) and (thing1.col == thing2.col):
                thing1.rest_time = random.randint(1, REST_TIME)
                break

def check_life(zombies):
    new_zombies = []
    while len(zombies) > 0:
        zombie = zombies.pop()
        if zombie.life > 0:
            zombie.life -= 1
            new_zombies.append(zombie)
    while len(new_zombies) > 0:
        zombie = new_zombies.pop()
        zombies.append(zombie)

def split_things(things):
    # returns a list of walls, humans, and zombies
    walls = []
    zombies = []
    humans = []
    while len(things) > 0:
        thing = things.pop()
        if thing.category == WALL:
            walls.append(thing)
        elif thing.category == HUMAN:
            humans.append(thing)
        elif thing.category == ZOMBIE:
            zombies.append(thing)
    return walls, humans, zombies

class Matrix(object):
    """
    Game environment
    """
    def __init__(self, x, y, screen, background):
        self.x, self.y = x, y
        self.screen = screen
        self.background = background
        self.clock = pygame.time.Clock()
        self.update_rect = []
        self.clear_screen()
        self.grid = ZombieGrid(HEIGHT, WIDTH)
        self.active = False
        #self.things = [] # store all humans, zombies, walls (things) in a list
        self.walls = []
        self.humans = []
        self.zombies = []

    def initialize_things(self):
        walls = []
        zombies = []
        humans = []

        random_location = []
        while len(random_location) <= (NUM_HUMAN+NUM_ZOMBIE+NUM_WALL):  # generate unique locations
            row = random.randint(0, HEIGHT-1)
            col = random.randint(0, WIDTH-1)
            if (row, col) not in random_location:
                random_location.append((row,col))

        for i in range(0,NUM_WALL):
            loc = random_location[i]
            walls.append(Thing(WALL, loc[0], loc[1]))

        for i in range(NUM_WALL, NUM_WALL+NUM_ZOMBIE):
            loc = random_location[i]
            zombies.append(Thing(ZOMBIE, loc[0], loc[1]))

        for i in range(NUM_WALL+NUM_ZOMBIE, NUM_WALL+NUM_ZOMBIE+NUM_HUMAN):
            loc = random_location[i]
            humans.append(Thing(HUMAN, loc[0], loc[1]))

        self.walls = walls
        self.humans = humans
        self.zombies = zombies

    def start(self):
        """Zombie start."""
        self.active = True
        self.initialize_things()
        self.clear_screen()

    def clear_screen(self):
        """Screen update."""
        self.screen.blit(self.background, (0,0))
        #self.draw_edge()
        pygame.display.flip()

    def draw_edge(self):
        """Draw edge around the arena."""
        self.edges = []
        for rect in [ (0,0,self.x,5), (0,self.y-5,self.x,5), (0,0,5,self.y), (self.x-5,0,5,self.y-5) ]:
            edge_rect = pygame.Rect(rect)
            self.edges.append(pygame.draw.rect(self.screen, (43,50,58), edge_rect, 0))
            self.update_rect.append(edge_rect)

    def draw_rect(self, x, y, color):
        """ fills specific coordinate with color """
        box = pygame.Rect((y*UNIT_SIZE, x*UNIT_SIZE, UNIT_SIZE, UNIT_SIZE))
        pygame.draw.rect(self.screen, color, box, 0)
        self.update_rect.append(box)

    #pygame.draw.rect(screen, the_color, (j*s+extra, i*s+extra, s+1-extra, s+1-extra), the_width)

    def update_screen(self):
        """Screen update."""
#            self.update_rect.extend( self.serpent[serpent].segments.draw(self.screen) )

        for i in range(0, HEIGHT):
            for j in range(0, WIDTH):
                category = self.grid.get_value(i, j)
                if category != EMPTY:
                    if category == WALL:
                        the_color = WALL_COLOR
                    elif category == ZOMBIE:
                        the_color = RED_COLOR
                    elif category == HUMAN:
                        the_color = HUMAN_COLOR
                    matrix.draw_rect(i, j, the_color)
                else:
                    matrix.draw_rect(i, j, BLACK_COLOR)
        pygame.display.update(self.update_rect)
        self.update_rect = []

    def update(self):
        """zombie update."""
        if self.active:

            # randomly add new human to things
            new_human_flag = random.randint(0, NEW_HUMAN_PROB)
            if new_human_flag == 0:
                row = random.randint(0, HEIGHT-1)
                col = random.randint(0, WIDTH-1)
                loc = self.grid.eight_neighbors(row, col)
                if len(loc) > 0:
                    row = loc[0][0]
                    col = loc[0][1]   
                    self.humans.append(Thing(HUMAN, row, col))

            self.grid.clear_grid()
            self.grid.update_grid(self.walls)
            check_life(self.zombies)
            self.grid.update_grid(self.humans)
            self.grid.update_grid(self.zombies)
            check_collision(self.zombies, self.humans)
            put_in_rest(self.zombies)
            put_in_rest(self.humans)

            # draw final grid:
            self.update_screen()

            # move things:
            dist_field_human = self.grid.compute_distance_field(self.zombies, self.humans, HUMAN)
            dist_field_zombie = self.grid.compute_distance_field(self.zombies, self.humans, ZOMBIE)
            move_things(self.zombies, self.grid, dist_field_human, ZOMBIE)
            move_things(self.humans, self.grid, dist_field_zombie, HUMAN)


class Control(object):
    def __init__(self, matrix):
        self.matrix = matrix
        pygame.font.init()
        font = pygame.font.get_default_font()
        self.font = pygame.font.Font(font, 24)
        self.font2 = pygame.font.Font(font, 14)
        self.matrix_start = False
        pygame.event.set_blocked(pygame.MOUSEMOTION)
        self.quit = False
        self.pause = True
        self.pause_program('Zombie', 'Click to restart', '(C) 2014 HARDMARU')
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
            self.pause_program('Zombie', 'Click to restart', '(C) 2014 HARDMARU')
            self.pause = True
        else:
            if self.matrix_start:
                self.matrix.clear_screen()
                self.matrix.update_screen()
                self.matrix.active = True
            else:
                self.matrix.start()
                self.matrix_start = True
            self.pause = False
    def check_control(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.matrix_start = False
                self.matrix_control()
            elif event.type == pygame.QUIT:
                self.quit = True
        return self.quit


def setup(x=500,y=500,screen=None):
    pygame.display.init()   #pygame.init()
    pygame.display.set_caption('Zombie')
    if not screen:
        screen = pygame.display.set_mode((x,y))
    background = pygame.Surface((x,y))
    background.fill((0,0,0))
    matrix = Matrix(x,y,screen,background)
    control = Control(matrix)
    return matrix, control


def program_exec(matrix, control):
    matrix.update_rect = []
    matrix.update()
    pygame.display.update(matrix.update_rect)
    #matrix.clock.tick_busy_loop(500)
    quit = control.check_control()
    return quit


def run():      #pyjsdl executed function
    program_exec(matrix, control)

def run2():
    quit = False
    while (quit == False):
        quit = program_exec(matrix, control)

matrix, control = None, None

def main():
    global matrix
    global control

    global EMPTY
    global WALL
    global ZOMBIE
    global HUMAN

    global BLACK_COLOR
    global RED_COLOR
    global GREEN_COLOR
    global BLUE_COLOR
    global WHITE_COLOR
    global DARK_GRAY_COLOR
    global WALL_COLOR
    global HUMAN_COLOR
    global ZOMBIE_COLOR

    global HEIGHT
    global WIDTH
    global UNIT_SIZE

    global NUM_WALL
    global NUM_ZOMBIE
    global NUM_HUMAN
    global REST_TIME
    global LIFE
    global NEW_HUMAN_PROB

    EMPTY = 0
    WALL = 1
    ZOMBIE = 2
    HUMAN = 3

    BLACK_COLOR = (0, 0, 0)
    RED_COLOR = (255, 0, 0)
    GREEN_COLOR = (0, 255, 0)
    BLUE_COLOR = (0, 0, 255)
    WHITE_COLOR = (255, 255, 255)
    DARK_GRAY_COLOR = (50, 50, 50)
    WALL_COLOR = GREEN_COLOR
    HUMAN_COLOR = BLUE_COLOR
    ZOMBIE_COLOR = RED_COLOR

    HEIGHT = 20
    WIDTH = 30
    UNIT_SIZE = 16

    NUM_WALL = HEIGHT*WIDTH/4
    NUM_ZOMBIE = 3
    NUM_HUMAN = 10
    REST_TIME = 3
    LIFE = 80
    NEW_HUMAN_PROB = 12

    matrix, control = setup(WIDTH*UNIT_SIZE,HEIGHT*UNIT_SIZE)
    pygame.display.setup(run)     #pyjsdl setup
    #run2()


if __name__ == '__main__':
    main()

