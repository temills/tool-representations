#!/usr/bin/env python3

import pygame as pg
import pymunk as pm
import math
import numpy as np
from utils import *

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 210,   0)
BLUE  = (  0,   0, 255)
SCREEN_WIDTH  = 1000
SCREEN_HEIGHT = 600

pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pg.time.Clock()
FPS = 100
space = pm.Space()
space.damping =  .5

#TODO
#in setup, make list of tasks for each type with params dependent on generated tool (can change to some average tool)
#consider game structure, how to access space / tools/walls/ball (thru game?)
#something fun once ball is in goal
#set things up to run new trial after success

#consider ambiguous task

#eventually:
#rn the tool just crushes ball if it tries to - don't let it move if gonna crush it (this might be hard, maybe make a tiny square to check w polygons)
#allow subsequent grasps?
#track object shapes, positions, and rotations
#will draw w js canvas



def generate_tool_attributes():
    """ method to generate tools according to distributions over features
        let's start off just with handle thickness and hook length
        for some tasks, handle thickness will matter for others, hook length (or angle)
        task type 1 will be 
    """
    handle_length = 200
    hook_width = 20

    min_handle_width = 20
    max_handle_width = 80

    min_hook_length = 5
    max_hook_length = 95


    handle_width = np.random.normal(50, 10, 1)[0]
    hook_length = np.random.normal(50, 15, 1)[0]

    return handle_width, handle_length, hook_width, hook_length

def get_tool_vertices(tool_attributes, left1, top1, angle):
    #w/h for handle and hook tool parts
    (w1,h1,h2,w2) = tool_attributes

    #position handle tool part
    vs1 = [(left1,top1), (left1+w1,top1), (left1+w1, top1+h1), (left1, top1+h1)]

    #position hook tool part
    left2 = left1 + w1
    top2 = top1
    vs2_unrotated = [(left2, top2), (left2 + w2, top2), (left2 + w2, top2 + h2), (left2, top2 + h2)]
    vs2 = rotate_polygon(vs2_unrotated[0], vs2_unrotated, 0.3)

    #rotate all tool parts
    vs1 = rotate_polygon((left1, top1), vs1, angle)
    vs2 = rotate_polygon((left1, top1), vs2, angle)
    return [vs1, vs2]

def setup(n):
    (w1,h1,h2,w2) = generate_tool_attributes()
    tool_verts = get_tool_vertices((w1,h1,h2,w2), 350, 450, math.pi/2)
    #in tasks, do we want to set walls/ball position based on tool attributes?
    #(add randomness but insure task is solvable in desired way)

    #hook task
    if n==1:
        return GameState(wall_pos=[[(500,300),(600,300),(600,320),(500,320)],[(580,200),(600,200),(600,300),(580,300)]],ball_pos=(530,290), tool_parts=tool_verts, grasp_pos=400,goal_pos=(700, 410, 50, 50))
    #poke task
    else:
        return GameState(wall_pos=[[(200,200),(220,200),(220,300),(200,300)],[(280,200),(300,200),(300,300),(280,300)]],ball_pos=(250,250), tool_parts=tool_verts, grasp_pos=350, goal_pos=(225, 150, 50, 50))

################ run game ###################
def run_game():
    game = setup(2)
    
    while True:
        #first check event queue for exits, clicks, mode change key presses
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            elif event.type == pg.MOUSEBUTTONDOWN:
                #this is how we're checking if click is on tool, but we can do this differently if we get rid of screen (check if in each tool part)
                if screen.get_at(event.pos)[:3] == BLUE:
                    game.tool.grasp(event.pos, game.grasp_zone)
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_m:
                    game.tool.set_mode('move')
                elif event.key == pg.K_r:
                    game.tool.set_mode('rotate')
                elif event.key == pg.K_RETURN:
                    global space
                    space = pm.Space()
                    space.damping =  .3
                    game.reset()

        #next check for key presses for movements
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:
            game.tool.make_move('u', game.wall_list, game.ball, game.grasp_zone)
        elif keys[pg.K_DOWN]:
            game.tool.make_move('d', game.wall_list, game.ball, game.grasp_zone)
        elif keys[pg.K_RIGHT]:
            game.tool.make_move('r', game.wall_list, game.ball, game.grasp_zone)
        elif keys[pg.K_LEFT]:
            game.tool.make_move('l', game.wall_list, game.ball, game.grasp_zone)
        else:
            game.tool.stop()

        #check if ball is in goal
        if game.goal.collidepoint(game.ball.body.position):
            game.ball.body._set_velocity((0,0))
            print("GOOOOAAAAAALLLLLLLL!!!!!")
            game.success = True

        #draw
        if game.success:
            screen.fill(GREEN)
        else:
            screen.fill(WHITE)
        game.draw()

        pg.display.update()

        clock.tick(FPS)
        space.step(1/FPS)

run_game()
pg.quit()

