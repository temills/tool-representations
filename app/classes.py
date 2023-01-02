import pymunk as pm
import pygame as pg
from .utils import *

class Ball():
    def __init__(self, x, y, rad, game):
        self.body = pm.Body()
        self.body.position = x,y
        self.body.velocity = 0,0
        self.body.angular_velocity = 0
        self.rad = rad
        self.shape = pm.Circle(self.body, rad)
        #self.shape.density = 1
        self.shape.friction = 1
        self.shape.mass = 5
        self.shape.elasticity = 1
        self.shape.collision_type = 4
        game.space.add(self.body, self.shape)
        self.color = (0, 240, 0)


class Wall():
    def __init__(self, vs, game):
        self.body = pm.Body(body_type=pm.Body.STATIC)
        self.shape = pm.Poly(self.body, vs)
        self.shape.elasticity = 1
        self.shape.friction = 1
        self.shape.density = 1
        self.shape.collision_type = 5
        game.space.add(self.body, self.shape)
        self.color = (0,0,0)


class Goal():
    def __init__(self, pos):
        (left, top, width, height) = pos
        self.goal_loc = pg.Rect(left, top, width, height)
        self.color = (0, 255, 0)
    
class GraspBoundary():
    def __init__(self, y, min_x, max_x, game):
        self.y = y
        self.min_x = min_x
        self.max_x = max_x
        self.color = (0,0,0)

        self.body = pm.Body(body_type=pm.Body.STATIC)
        self.shape = pm.Segment(self.body, (min_x, self.y), (max_x, self.y), 2)
        self.shape.elasticity = 1
        self.shape.friction = 1
        self.shape.density = 1
        self.shape.collision_type = 2
        game.space.add(self.body, self.shape)
        self.color = (0,0,0)


class Tool():
    def __init__(self, parts, game):
        self.color = (0, 0, 255)
        self.game = game

        self.body = pm.Body()
        game.space.add(self.body)
        #attach tool parts to body
        self.shape_list = []
        for vs in parts:
            shape = pm.Poly(self.body, vs)
            shape.mass = 50
            shape.friction = 1
            shape.collision_type = 1
            self.shape_list.append(shape)
            game.space.add(shape)

            self.is_grasped = False
            self.grasp_point = pm.Poly(self.body, [(0, 0), (8, 0), (8, 8), (0, 8)])
            self.grasp_point.mass = 50
            self.grasp_point.friction = 1
            self.grasp_point.collision_type = 3
            self.game.space.add(self.grasp_point)

        #for rotations
        self.rotate_point = pm.Body(body_type=pm.Body.KINEMATIC)
        self.rotate_point.collision_type = 6
        self.game.space.add(self.rotate_point)
        self.rotator = pm.constraints.SimpleMotor(self.rotate_point, self.body, 0)
        self.game.space.add(self.rotator)
    
    def grasp(self, cog, grasp_boundary):
        on_tool = False
        for shape in self.shape_list:
            if point_inside_poly([self.body.local_to_world(v) for v in shape.get_vertices()], cog[0], cog[1]):
                on_tool = True
        if on_tool and (cog[1] > grasp_boundary.y):
            #do we really need this +/- 4?
            self.is_grasped = True
            self.grasp_point.unsafe_set_vertices([self.body.world_to_local(v) for v in [(cog[0]-4, cog[1]-4), (cog[0]+4, cog[1]-4), (cog[0]+4, cog[1]+4), (cog[0]-4, cog[1]+4)]])
            old_pos = self.body.position
            self.body._set_center_of_gravity(self.body.world_to_local(cog))
            self.body._set_position(old_pos)
                
    def move(self, dir, wall_list, ball, grasp_boundary):
        self.rotator_rate = 0
        #self.rotator.rate = 0
        if dir=='u':
            vx, vy = 0, -800
        elif dir=='d':
            vx, vy = 0, 800
        elif dir=='r':
            vx, vy = 800, 0
        elif dir=='l':
            vx, vy = -800, 0
        self.body.apply_impulse_at_world_point((vx,vy), self.body.local_to_world(self.body.center_of_gravity))

    def rotate(self, dir, wall_list, ball):
        if dir=='r':
            self.rotator.rate = -1
        elif dir=='l':
            self.rotator.rate = 1
        else:
            self.rotator.rate = 0

    def flip(self):
        for shape in self.shape_list:
            print(shape.get_vertices())
            print([self.body.local_to_world(v) for v in shape.get_vertices()])
            print(self.body.center_of_gravity[0])
            print(self.body.local_to_world(self.body.center_of_gravity)[0])
            hyp_flip = flip_polygon_vertical([self.body.local_to_world(v) for v in shape.get_vertices()], self.body.local_to_world(self.body.center_of_gravity)[0])
            print(hyp_flip)
            shape.unsafe_set_vertices([self.body.world_to_local(v) for v in hyp_flip])
        
        """
            get hypothetical flip and see if hits walls or ball
            if not, flip
        """

    def stop(self):
        self.body.velocity = 0,0
        self.body.angular_velocity = 0
        self.rotator.rate = 0



class GameState():
    def __init__(self, wall_pos, ball_pos, ball_rad, goal_pos, tool_pos, tool_angle, poss_tool_attrs, poss_tool_locs, grasp_bound_y, grasp_bound_min_x, grasp_bound_max_x):
        #store initial param values and set vars to these values
        self.space = pm.Space()
        self.init_params = (wall_pos, ball_pos, ball_rad, goal_pos, tool_pos, tool_angle, poss_tool_attrs, poss_tool_locs, grasp_bound_y, grasp_bound_min_x, grasp_bound_max_x)
        self.set_game()
        
        #like friction
        self.space.damping =  .4

        #set handler to correctly deal with collisions with grasp bound
        #tool is 1
        #ball is 4
        #grasp point is 3
        #rotator is 6
        #grasp bound is 2
        #wall is 5
        self.ball_grasp_bound_handler = self.space.add_collision_handler(4,2)
        self.ball_grasp_bound_handler.begin = self.no_collide
        self.tool_grasp_bound_handler = self.space.add_collision_handler(1,2)
        self.tool_grasp_bound_handler.begin = self.no_collide
        self.grasp_point_grasp_bound_handler = self.space.add_collision_handler(3,2)
        self.grasp_point_grasp_bound_handler.begin = self.yes_collide

        self.wall_test = False
        self.tool_wall_handler = self.space.add_collision_handler(6,1)
        self.tool_wall_handler.begin = self.tool_wall
        #self.tool_ball_handler = self.space.add_collision_handler(3,)
        #self.tool_ball_handler.begin = self.tool_ball


    def tool_wall(self, space, arbiter, data):
        print("idk!!!!!!!!!!!!!!")
        self.wall_test = True
        return False
    #def tool_ball(self, space, arbiter, data):
    #    print("tool and ball")
    #    return True

    def yes_collide(self, space, arbiter, data):
        return True

    def no_collide(self, space, arbiter, data):
        return False
    
    def set_game(self):
        (wall_pos, ball_pos, ball_rad, goal_pos, tool_pos, tool_angle, poss_tool_attrs, poss_tool_locs, grasp_bound_y, grasp_bound_min_x, grasp_bound_max_x) = self.init_params
        self.ball = Ball(ball_pos[0],ball_pos[1], ball_rad, self)
        self.wall_list = [Wall(wp, self) for wp in wall_pos]
        self.poss_tool_attrs = poss_tool_attrs
        self.poss_tool_locs = poss_tool_locs
        self.tool_angle = tool_angle
        self.tool_pos = tool_pos
        self.success = False
        self.active_tool = None
        self.active_tool_idx = -1
        self.grasp_boundary = GraspBoundary(grasp_bound_y, grasp_bound_min_x, grasp_bound_max_x, self)
        self.goal = Goal(goal_pos)

    def reset(self):
        self.space.remove(self.ball.shape, self.ball.body)
        for shape in self.active_tool.shape_list:
            self.space.remove(shape)
        self.space.remove(self.active_tool.grasp_point)
        self.space.remove(self.active_tool.body)
        #should remove rotator too?
        self.set_game()

    def pick_tool(self, click_pos):
        """check if click was on any tools
            if so, set active tool
            and add to screen
        """
        for i, tool in enumerate(self.poss_tool_locs):
            for tool_part in tool:
                if point_inside_poly(tool_part, click_pos[0], click_pos[1]):
                    #click was on this tool
                    #set active tool
                    self.active_tool_idx = i
                    self.active_tool = Tool(get_tool_vertices(self.poss_tool_attrs[i], self.tool_pos[0], self.tool_pos[1], self.tool_angle), self)
                    self.active_tool.grasp(click_pos, self.grasp_boundary)
    
    def get_success(self):
        success = False
        if self.goal.goal_loc.collidepoint(self.ball.body.position):
            self.ball.body._set_velocity((0,0))
            success = True
        return success

    def get_state(self):
        #don't need to return unchanging info: ball size, list of tools and their dims, walls, grasp boundary, goal
        is_grasped = False
        active_tool_vertices = []
        grasp_pos = []
        if self.active_tool_idx >= 0:
            for shape in self.active_tool.shape_list:
                active_tool_vertices.append([self.active_tool.body.local_to_world(v) for v in shape.get_vertices()])
            if self.active_tool.is_grasped:
                is_grasped = True
                grasp_pos = self.active_tool.body.local_to_world(self.active_tool.grasp_point.get_vertices()[0])

        success = self.get_success()

        #which tool is active, active tool vertices, ball pos, is in goal
        return {'active_tool_idx': self.active_tool_idx, 'active_tool_vertices': active_tool_vertices, 'is_grasped': is_grasped, 'grasp_pos': grasp_pos, 'ball_pos': self.ball.body.position, 'success': success, 'wall_test':self.wall_test}