#!/usr/bin/env python3

import pygame as pg
import pymunk as pm
import math
import numpy as np
from utils import *
from classes import *

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 210,   0)
BLUE  = (  0,   0, 255)
SCREEN_WIDTH  = 1000
SCREEN_HEIGHT = 750

#sometimes goes thru walls a bit
#this is especially a problem bc then when you release after forcing into a wall, it's a huge force and launches it above the grasp line


#hold down r to rotate automatically move
#could not rotate tool and just move around
#make sure when hook is rlly skinny, hook part isn't so skinny u can hit w that side (not too long, but longer than width of tunnel)


#impulse slowly slows until it stops unless we re click to apply
#should be working when it's held down i think

#dim unchosen tools
#clean up code

#make white outside of walls





task_type = 1


pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pg.time.Clock()
FPS = 100


#TODO
#in setup, make list of tasks for each type
#something fun once ball is in goal
#set things up to run new trial after success

#consider ambiguous task

#eventually:
#rn the tool just crushes ball if it tries to - don't let it move if gonna crush it (this might be hard, maybe make a tiny square to check w polygons)
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

    #min_handle_width = 20
    #max_handle_width = 80

    #min_hook_length = 10
    #max_hook_length = 90


    handle_width = np.random.normal(50, 10, 1)[0]
    hook_length = np.random.normal(50, 15, 1)[0]

    return handle_width, handle_length, hook_width, hook_length



"""
do get tool_verts n times with appropriate pos so non-overlapping
we don't really want these tools to exist - want them to be chosen if we reset
maybe still exist out in the side
some side panal where you see them, can click to choose and it will show up in the tool zone

"""


def setup(task_type, trial):
    n_tools = 3
    tool_attrs = [generate_tool_attributes() for _ in range(n_tools)]
    tool_start_pos = (450,450)
    tool_start_angle = math.pi/2
    wall_height = 600
    edges = [get_rect_verts(5, 5, 10, wall_height - 5), get_rect_verts(SCREEN_WIDTH - 15, 5, 10, wall_height - 5), get_rect_verts(5 + 10, 5, SCREEN_WIDTH-30, 10), get_rect_verts(15, wall_height-10, SCREEN_WIDTH-30, 10)]
    
    #(walls, ball, grasp, goal) = get_hook_task()
    
    #hook task
    if task_type==1:
        return [GameState(wall_pos= edges + [get_rect_verts(500, 300, 150, 20), get_rect_verts(630, 200, 20, 100)],ball_pos=(530,290), tool_attrs=tool_attrs, tool_start_pos = tool_start_pos, tool_start_angle = tool_start_angle, grasp_pos=400, grasp_width=970, goal_pos=(700, 410, 50, 50))][trial]
                #GameState(wall_pos= edges + [get_rect_verts(500, 300, 150, 20), get_rect_verts(630, 200, 20, 100)],ball_pos=(530,290), tool_attrs=tool_attrs, tool_start_pos = tool_start_pos, tool_start_angle = tool_start_angle, grasp_pos=400, grasp_width=970, goal_pos=(700, 410, 50, 50)),
                #[trial]
    #poke task
    else:
        return [GameState(wall_pos= edges + [[(200,200),(220,200),(220,300),(200,300)],[(280,200),(300,200),(300,300),(280,300)]],ball_pos=(250,250), tool_attrs=tool_attrs, tool_start_pos = tool_start_pos, tool_start_angle = tool_start_angle, grasp_pos=350, grasp_width=970, goal_pos=(225, 120, 50, 50))][trial]
################ run game ###################
def run_game():
    num_trials = 3
    for trial in range(num_trials):
        game = setup(task_type, trial)
        success = False
        while True:
            #first check event queue for exits, clicks, mode change key presses
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                if game.active_tool != None:
                    if event.type == pg.MOUSEBUTTONDOWN:
                        game.active_tool.grasp(event.pos, game.grasp_boundary)
                    elif event.type == pg.KEYDOWN:
                        if event.key == pg.K_m:
                            game.active_tool.set_mode('move')
                        elif event.key == pg.K_f:
                            game.active_tool.flip()
                        #elif event.key == pg.K_r:
                        #    game.active_tool.set_mode('rotate')
                        elif event.key == pg.K_RETURN:
                            success=False
                            game.reset()
                else:
                    if event.type == pg.MOUSEBUTTONDOWN:
                        game.pick_tool(event.pos)

            #next check for key presses for movements
            keys = pg.key.get_pressed()
            if game.active_tool != None:
                if keys[pg.K_UP]:
                    if keys[pg.K_r]:
                        game.active_tool.rotate('u', game.wall_list, game.ball) 
                    else:
                        game.active_tool.move('u', game.wall_list, game.ball, game.grasp_boundary) 
                elif keys[pg.K_DOWN]:
                    if keys[pg.K_r]:
                        game.active_tool.rotate('d', game.wall_list, game.ball) 
                    else:
                        game.active_tool.move('d', game.wall_list, game.ball, game.grasp_boundary)
                elif keys[pg.K_RIGHT]:
                    if keys[pg.K_r]:
                        game.active_tool.rotate('r', game.wall_list, game.ball) 
                    else:
                        game.active_tool.move('r', game.wall_list, game.ball, game.grasp_boundary)
                elif keys[pg.K_LEFT]:
                    if keys[pg.K_r]:
                        game.active_tool.rotate('l', game.wall_list, game.ball) 
                    else:
                        game.active_tool.move('l', game.wall_list, game.ball, game.grasp_boundary)
                else:
                    game.active_tool.stop()

            #check if ball is in goal
            if game.goal.goal_loc.collidepoint(game.ball.body.position):
                game.ball.body._set_velocity((0,0))
                print("GOOOOAAAAAALLLLLLLL!!!!!")
                success = True

            #draw
            if success:
                screen.fill(GREEN)
            else:
                screen.fill(WHITE)
            
            game.draw(screen)

            pg.display.update()

            clock.tick(FPS)
            game.space.step(1/FPS)

run_game()
pg.quit()

