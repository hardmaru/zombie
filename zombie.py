# test version for zombie apocolapyse using pygame

import pygame
import numpy as np
import random

EMPTY = 0
WALL = 1
ZOMBIE = 2
HUMAN = 3

black_color = pygame.Color(0, 0, 0)
red_color = pygame.Color(160, 0, 0)
green_color = pygame.Color(0, 255, 0)
blue_color = pygame.Color(0, 0, 255)
white_color = pygame.Color(255, 255, 255)
dark_gray_color = pygame.Color(50, 50, 50)
wall_color = pygame.Color(50, 150, 150)
human_color = pygame.Color(0, 25, 200)

HEIGHT = 50
WIDTH = 60
NUM_WALL = HEIGHT*WIDTH/3
NUM_ZOMBIE = 1
NUM_HUMAN = 99
REST_TIME = 10
LIFE = 100
NEW_HUMAN_PROB = 50

(screen_x_size, screen_y_size) = (WIDTH*10+1, HEIGHT*10+1)

class Queue:
    """
    A simple implementation of a FIFO queue.
    """

    def __init__(self):
        """ 
        Initialize the queue.
        """
        self._items = []

    def __len__(self):
        """
        Return the number of items in the queue.
        """
        return len(self._items)
    
    def __iter__(self):
        """
        Create an iterator for the queue.
        """
        for item in self._items:
            yield item

    def __str__(self):
        """
        Return a string representation of the queue.
        """
        return str(self._items)

    def enqueue(self, item):
        """
        Add item to the queue.
        """        
        self._items.append(item)

    def dequeue(self):
        """
        Remove and return the least recently inserted item.
        """
        return self._items.pop(0)

    def clear(self):
        """
        Remove all items from the queue.
        """
        self._items = []

class ZombieGrid:
    def __init__(self, grid_height=48, grid_width=48, grid_color=pygame.Color(0, 255, 0)):
        self.grid = np.zeros((grid_height,grid_width))
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.grid_color = grid_color

    def set_value(self, row, col, value):
        self.grid[row][col] = value

    def get_value(self, row, col):
        return self.grid[row][col]

    def clear_grid(self):
        self.grid = np.zeros((self.grid_height,self.grid_width))

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
        visited = np.zeros((self.grid_height, self.grid_width))
        dist_field = np.ones((self.grid_height, self.grid_width))
        max_dist = self.grid_height * self.grid_width
        dist_field *= max_dist

        boundary = Queue()
        entity_list = humans

        if entity_type == ZOMBIE:
            entity_list = zombies

        for entity in entity_list:
            boundary.enqueue((entity.row,entity.col))
            visited[entity.row][entity.col] = 1
            dist_field[entity.row][entity.col] = 0
            
        while len(boundary) > 0:
            cell = boundary.dequeue()
            current_dist = dist_field[cell[0]][cell[1]]
            neighbors = []
            if entity_type == ZOMBIE:  # humans have to make a move
                neighbors = self.four_neighbors(cell[0], cell[1])
            else: # zombies have to make a move
                neighbors = self.eight_neighbors(cell[0], cell[1])
            for neighbor in neighbors:
                if visited[neighbor[0]][neighbor[1]]==0 and self.get_value(neighbor[0], neighbor[1]) != WALL:
                    visited[neighbor[0]][neighbor[1]] = 1
                    boundary.enqueue(neighbor)
                    dist_field[neighbor[0]][neighbor[1]] = current_dist + 1

        return dist_field

    def display(self):
        s = 10
        for i in range(0, self.grid_height):
            for j in range(0, self.grid_width):
                the_color = self.grid_color
                the_width = 0
                the_thing = self.grid[i][j]
                extra = 1
                if the_thing == WALL:
                    the_color = wall_color
                elif the_thing == ZOMBIE:
                    the_color = red_color
                elif the_thing == HUMAN:
                    the_color = human_color
                else:
                    the_width = 1
                    extra = 0
                pygame.draw.rect(screen, the_color, (j*s+extra, i*s+extra, s+1-extra, s+1-extra), the_width)

    def display_field(self, field):
        s = 10
        field2 = field.copy()
        field2[field2==3000]=0
        max_field2 = field2.max()
        field2 /= max_field2
        field2 *= 127
        field2 = np.floor(field2)
        field2[field==3000]=255
        for i in range(0, self.grid_height):
            for j in range(0, self.grid_width):
                #intensity = int(math.floor(255*field[i][j]/max_field))
                intensity = int(field2[i][j])
                the_color = pygame.Color(intensity, intensity, intensity)
                the_width = 0
                extra =1
                pygame.draw.rect(screen, the_color, (j*s+extra, i*s+extra, s+1-extra, s+1-extra), the_width)

class Thing:
    def __init__(self, category, row, col):
        self.category = category
        self.row = row
        self.col = col
        self.rest_time = 0
        self.life = LIFE

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
                score = field[loc[0]][loc[1]]

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
                zombie.life = LIFE*10
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

screen = pygame.display.set_mode((screen_x_size,screen_y_size))
pygame.display.set_caption('zombie vs human')
screen.fill(black_color)

grid = ZombieGrid(HEIGHT, WIDTH, dark_gray_color)

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

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    new_human_flag = random.randint(0, NEW_HUMAN_PROB)
    if new_human_flag == 0:
        row = random.randint(0, HEIGHT-1)
        col = random.randint(0, WIDTH-1)
        loc = grid.eight_neighbors(row, col)
        if len(loc) > 0:
            row = loc[0][0]
            col = loc[0][1]   
            humans.append(Thing(HUMAN, row, col))
    screen.fill(black_color)
    grid.clear_grid()
    grid.update_grid(walls)
    check_life(zombies)
    grid.update_grid(humans)
    grid.update_grid(zombies)
    check_collision(zombies, humans)
    put_in_rest(zombies)
    put_in_rest(humans)
    grid.display()
    pygame.display.flip()

    dist_field_human = grid.compute_distance_field(zombies, humans, HUMAN)
    dist_field_zombie = grid.compute_distance_field(zombies, humans, ZOMBIE)
    move_things(zombies, grid, dist_field_human, ZOMBIE)
    move_things(humans, grid, dist_field_zombie, HUMAN)
    #pygame.time.delay(30)
    #screen.fill(black_color)
    #grid.display_field(dist_field_human)
    #pygame.display.flip()
    #pygame.time.delay(500)

