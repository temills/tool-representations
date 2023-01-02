#!/usr/bin/env python3

import pymunk as pm
import math
import numpy as np
from .utils import *
from .classes import *

game = None
did_init = False
trial = 0
task_type = 1
FPS = 100

#TODO
#sometimes goes thru walls a bit
#this is especially a problem bc then when you release after forcing into a wall, it's a huge force and launches it above the grasp line
#make sure when hook is rlly skinny, hook part isn't so skinny u can hit w that side (not too long, but longer than width of tunnel)
#impulse slowly slows until it stops unless we re click to apply
    #should be working when it's held down i think
#dim unchosen tools
#clean up code
#in setup, make list of tasks for each type
#something fun once ball is in goal
#consider ambiguous task

def init_game(trial_info):
    global game
    game = GameState(wall_pos = trial_info["wall_pos"],
                     ball_pos = trial_info["ball_pos"],
                     ball_rad = trial_info["ball_rad"],
                     goal_pos = trial_info["goal_pos"],
                     tool_pos = trial_info["tool_pos"],
                     tool_angle = trial_info["tool_angle"],
                     poss_tool_attrs = trial_info["poss_tool_attrs"],
                     poss_tool_locs = trial_info["poss_tool_locs"],
                     grasp_bound_y = trial_info["grasp_bound_y"],
                     grasp_bound_min_x = trial_info["grasp_bound_min_x"],
                     grasp_bound_max_x = trial_info["grasp_bound_max_x"])

#await may or may not be working but im still confused

def reformat_input(user_input):
    print(user_input)
    for k, v in user_input.items():
        if k not in ['click_x', 'click_y']:
            user_input[k] = v[0] == '1'
    if(user_input["click"]):
        user_input['click_x'] = float(user_input['click_x'][0])
        user_input['click_y'] = float(user_input['click_y'][0])
    return user_input

################ run game ###################
def update_game(user_input):
    global game
    game.wall_test = False
    user_input = reformat_input(user_input)

    if game.active_tool == None:
        if user_input["click"]:
            game.pick_tool([user_input["click_x"], user_input["click_y"]])
        if user_input["Enter"]:
            game.reset()
    else:
        if user_input["click"]:
            game.active_tool.grasp([user_input["click_x"],user_input["click_y"]], game.grasp_boundary)
        if user_input["Enter"]:
            game.reset()
        
        #flip tool
        #if user_input['f']:
            #game.active_tool.flip()

        #next check for key presses for movements
        move = False
        #first check for rotation, in rotation first stop movements left/right/up/down before rotating
        #then if no rotation check for movement,stop in all directions other than move

        if user_input['ArrowUp']:
            move = True
            if user_input['r']:
                game.active_tool.rotate('u', game.wall_list, game.ball)
            else:
                game.active_tool.move('u', game.wall_list, game.ball, game.grasp_boundary) 
        if user_input['ArrowDown']:
            move = True
            if user_input['r']:
                game.active_tool.rotate('d', game.wall_list, game.ball)
            else:
                game.active_tool.move('d', game.wall_list, game.ball, game.grasp_boundary) 
        if user_input['ArrowLeft']:
            move = True
            if user_input['r']:
                game.active_tool.rotate('l', game.wall_list, game.ball)
            else:
                game.active_tool.move('l', game.wall_list, game.ball, game.grasp_boundary) 
        if user_input['ArrowRight']:
            move = True
            if user_input['r']:
                game.active_tool.rotate('r', game.wall_list, game.ball)
            else:
                game.active_tool.move('r', game.wall_list, game.ball, game.grasp_boundary) 
        if not move:
            game.active_tool.stop()

    #step game
    game.space.step(3/FPS)

    return game.get_state()