#!/usr/bin/env python3
import numpy as np
from .utils import *
import json

#honestly not advisable to change these, each trial set up w this in mind
#and not sure it makes sense to figure out how to set up relative to these
display_width = 1000
display_height = 800
picker_height = 200
n_tools = 3

def generate_tool_attributes():
    """ method to generate tools according to distributions over features
        and constraints?
        handle thickness and hook length are varied
    """
    handle_length = 200
    hook_width = 20
    handle_width = np.random.normal(50, 10, 1)[0]
    hook_length = np.random.normal(50, 15, 1)[0]

    return handle_width, handle_length, hook_width, hook_length

def get_trial_info(task_type):
    trial_info = {}
    wall_height = display_height - picker_height
    edge_width = 10
    edges = [get_rect_verts(5, 5, edge_width, wall_height - 5), get_rect_verts(display_width - (5 + edge_width), 5, edge_width, wall_height - 5), get_rect_verts(5 + edge_width, 5, display_width-(2*(5+edge_width)), edge_width), get_rect_verts(edge_width + 5, wall_height-edge_width, display_width-(2*(5+edge_width)), edge_width)]
    
    #hook task
    if task_type==1:
        #this is one trial - we should make more
        trial_info["wall_pos"] = edges + [get_rect_verts(500, 300, 150, 20)] + [get_rect_verts(630, 200, 20, 100)]

        trial_info["ball_pos"] = (530,290)
        trial_info["ball_rad"] = 8
        trial_info["goal_pos"] = (700, 410, 50, 50)
        trial_info["tool_pos"] = (450,450)
        trial_info["tool_angle"] = math.pi/2 #should this be randomized?

        trial_info["poss_tool_attrs"] = [generate_tool_attributes() for _ in range(n_tools)]
        w_per_tool = (display_width - (2*(5 + edge_width))) / n_tools
        poss_tool_top = wall_height + 20
        poss_tool_left_start = 280 #could make this better ... but is it worth it
        trial_info["poss_tool_locs"] = [get_tool_vertices(trial_info["poss_tool_attrs"][i], poss_tool_left_start + (i*w_per_tool), poss_tool_top, trial_info["tool_angle"]) for i in range(n_tools)]

        trial_info["grasp_bound_y"] = 400
        trial_info["grasp_bound_min_x"] = (5 + edge_width)
        trial_info["grasp_bound_max_x"] = display_width - (5 + edge_width)

    #poke task
    else:
        trial_info["wall_pos"] = edges + [get_rect_verts(200,200,20,100)] + [get_rect_verts(280,200,20,100)]

        trial_info["ball_pos"] = (250,250)
        trial_info["ball_rad"] = 8
        trial_info["goal_pos"] = (225, 120, 50, 50)
        trial_info["tool_pos"] = (450,450)
        trial_info["tool_angle"] = math.pi/2 #should this be randomized?

        trial_info["poss_tool_attrs"] = [generate_tool_attributes() for _ in range(n_tools)]
        w_per_tool = (display_width - (2*(5 + edge_width))) / n_tools
        poss_tool_top = wall_height + 20
        poss_tool_left_start = 280 #could make this better ... but is it worth it
        trial_info["poss_tool_locs"] = [get_tool_vertices(trial_info["poss_tool_attrs"][i], poss_tool_left_start + (i*w_per_tool), poss_tool_top, trial_info["tool_angle"]) for i in range(n_tools)]

        trial_info["grasp_bound_y"] = 350
        trial_info["grasp_bound_min_x"] = (5 + edge_width)
        trial_info["grasp_bound_max_x"] = display_width - (5 + edge_width)

    return trial_info
