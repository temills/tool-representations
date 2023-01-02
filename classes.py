import pymunk as pm
import pygame as pg
from .utils import *

class Ball():
    def __init__(self, x, y, game):
        self.body = pm.Body()
        self.body.position = x,y
        self.body.velocity = 0,0
        self.body.angular_velocity = 0
        self.rad = 8
        self.shape = pm.Circle(self.body, 8)
        #self.shape.density = 1
        self.shape.friction = 1
        self.shape.mass = 5
        self.shape.elasticity = 1
        self.shape.collision_type = 1
        game.space.add(self.body, self.shape)
        self.color = (0, 240, 0)

    def draw(self, screen):
        x,y = self.body.position
        pg.draw.circle(screen, self.color, self.body.position, self.rad)
        #pg.draw.circle(screen, self.color, (int(x),int(y)), self.rad)


class Wall():
    def __init__(self, vs, game):
        self.body = pm.Body(body_type=pm.Body.STATIC)
        self.shape = pm.Poly(self.body, vs)
        self.shape.elasticity = 1
        self.shape.friction = 1
        self.shape.density = 1
        game.space.add(self.body, self.shape)
        self.color = (0,0,0)
    
    def draw(self, screen):
        #pg.draw.polygon(screen, BLACK, [self.body.local_to_world(v) for v in self.shape.get_vertices()])
        pg.draw.polygon(screen, self.color, [v for v in self.shape.get_vertices()])


class Goal():
    def __init__(self, pos):
        (left, top, width, height) = pos
        self.goal_loc = pg.Rect(left, top, width, height)
        self.color = (0, 255, 0)
    
    def draw(self, screen):
        pg.draw.rect(screen, self.color, self.goal_loc)

class GraspBoundary():
    def __init__(self, y, width, game):
        self.y = y
        self.width = width
        self.color = (0,0,0)

        self.body = pm.Body(body_type=pm.Body.STATIC)
        self.shape = pm.Segment(self.body, (15, self.y), (15+self.width, self.y), 2)
        self.shape.elasticity = 1
        self.shape.friction = 1
        self.shape.density = 1
        self.shape.collision_type = 2
        game.space.add(self.body, self.shape)
        self.color = (0,0,0)

    
    def draw(self, screen):
        pg.draw.line(screen, self.color, (15, self.y), (15+self.width, self.y), 2)


class Tool():
    def __init__(self, parts, game):
        self.color = (0, 0, 255)
        self.game = game
        self.mode = 'move'
        self.is_grasped = False

        self.body = pm.Body()
        #self.body.position = 300,400
        game.space.add(self.body)

        self.shape_list = []
        for vs in parts:
            shape = pm.Poly(self.body, vs)
            shape.mass = 50
            shape.friction = 1
            shape.collision_type = 1
            self.shape_list.append(shape)
            game.space.add(shape)

        self.temp_shape = pm.Poly(self.body, [(300,450),(308,450),(308,458),(300,458)])
        self.temp_shape.mass = 50
        self.temp_shape.friction = 1
        self.temp_shape.collision_type = 3
        game.space.add(self.temp_shape)

        #for rotations
        self.grasp_point = pm.Body(body_type=pm.Body.KINEMATIC)
        self.game.space.add(self.grasp_point)
        #self.game.space.add(pm.constraints.PinJoint(self.grasp_point, self.body))
        self.rotator = pm.constraints.SimpleMotor(self.grasp_point, self.body, 0)
        self.game.space.add(self.rotator)
        #self.rotator.sleep()

    def draw(self, screen):       
        #stays the same as first grasp
        x,y = self.body.center_of_gravity
        for shape in self.shape_list:
            #draw tool part
            pg.draw.polygon(screen, self.color, [self.body.local_to_world(v) for v in shape.get_vertices()])
        #draw grasper
        if self.is_grasped:
            #pg.draw.circle(screen, (0, 255, 0), self.body.position, 3)
            #pg.draw.circle(screen, (0, 255 , 0), self.body.local_to_world(self.body.center_of_gravity), 3)
            pg.draw.polygon(screen, (255,0,0), [self.body.local_to_world(v) for v in self.temp_shape.get_vertices()])
            #pg.draw.circle(screen, (255, 0 , 0), self.grasp_point.position, 2)
    
    def grasp(self, cog, grasp_boundary):
        on_tool = False
        for shape in self.shape_list:
            if point_inside_poly([self.body.local_to_world(v) for v in shape.get_vertices()], cog[0], cog[1]):
                on_tool = True
        if on_tool and (cog[1] > grasp_boundary.y):
            self.is_grasped = True
            self.temp_shape.unsafe_set_vertices([self.body.world_to_local(v) for v in [(cog[0]-4, cog[1]-4), (cog[0]+4, cog[1]-4), (cog[0]+4, cog[1]+4), (cog[0]-4, cog[1]+4)]])
            old_pos = self.body.position
            self.body._set_center_of_gravity(self.body.world_to_local(cog))
            self.body._set_position(old_pos)
                
    def set_mode(self, mode):
        if mode in ['move', 'rotate']:
            self.mode = mode
    """
    def make_move(self, dir, wall_list, ball, grasp_boundary):
        if self.is_grasped:
            if self.mode=='move':
                self.move(dir, wall_list, ball, grasp_boundary)
            else:
                self.rotate(dir, wall_list, ball)
    """
    def move(self, dir, wall_list, ball, grasp_boundary):
        if not self.is_grasped:
            return
        self.rotator.rate = 0
        if dir=='u':
            vx, vy = 0, -500
        elif dir=='d':
            vx, vy = 0, 500
        elif dir=='r':
            vx, vy = 500, 0
        elif dir=='l':
            vx, vy = -500, 0
        self.body.apply_impulse_at_world_point((vx,vy), self.body.local_to_world(self.body.center_of_gravity))

    def rotate(self, dir, wall_list, ball):
        if not self.is_grasped:
            return
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
        #self.grasp_point.velocity = 0,0
        self.body.velocity = 0,0
        self.body.angular_velocity = 0
        #self.rotator.sleep()


class PivotJoint:
    def __init__(self, b, b2, space, a=(0, 0), a2=(0, 0), collide=True):
        joint = pm.constraints.PinJoint(b, b2, a, a2)
        joint.collide_bodies = collide
        space.add(joint)




class GameState():
    def __init__(self, wall_pos, ball_pos, tool_attrs, tool_start_pos, tool_start_angle, grasp_pos, grasp_width, goal_pos):
        self.space = pm.Space()
        self.init_params = (wall_pos, ball_pos, tool_attrs, tool_start_pos, tool_start_angle, grasp_pos, grasp_width, goal_pos)
        self.set_game()
        self.space.damping =  .4
        self.handler = self.space.add_collision_handler(1,2)
        self.handler.begin = self.collide
        self.handler2 = self.space.add_collision_handler(3,2)
        self.handler2.begin = self.collide2
    
    def collide2(self, space, arbiter, data):
        return True

    def collide(self, space, arbiter, data):
        return False
    
    def set_game(self):
        (wall_pos, ball_pos, tool_attrs, tool_start_pos, tool_start_angle, grasp_pos, grasp_width, goal_pos) = self.init_params
        self.ball = Ball(ball_pos[0],ball_pos[1], self)
        self.wall_list = [Wall(wp, self) for wp in wall_pos]
        self.poss_tool_attrs = tool_attrs
        self.poss_tool_locs = []
        self.tool_start_angle = tool_start_angle
        self.tool_start_pos = tool_start_pos
        w_per_tool = 950/len(self.poss_tool_attrs)
        for i, attr in enumerate(self.poss_tool_attrs):
            self.poss_tool_locs.append(get_tool_vertices(attr, 280 + (i*w_per_tool), 620, self.tool_start_angle))
        self.active_tool = None
        self.grasp_boundary = GraspBoundary(grasp_pos, grasp_width, self)
        self.goal = Goal(goal_pos)

    def reset(self):
        self.space.remove(self.ball.shape, self.ball.body)
        for shape in self.active_tool.shape_list:
            self.space.remove(shape)
        self.space.remove(self.active_tool.temp_shape)
        self.space.remove(self.active_tool.body)
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
                    self.active_tool = Tool(get_tool_vertices(self.poss_tool_attrs[i], self.tool_start_pos[0], self.tool_start_pos[1], self.tool_start_angle), self)
                    self.active_tool.grasp(click_pos, self.grasp_boundary)

    def draw(self, screen):
        pg.draw.rect(screen, (255, 229, 180), pg.Rect(15,15,970,585))
        self.goal.draw(screen)
        self.ball.draw(screen)
        for wall in self.wall_list:
            wall.draw(screen)
        if self.active_tool == None:
            for tool in self.poss_tool_locs:
                for tool_part in tool:
                    pg.draw.polygon(screen, (0,0,255), tool_part)
        else:
            self.active_tool.draw(screen)
            for tool in self.poss_tool_locs:
                for tool_part in tool:
                    pg.draw.polygon(screen, (0,0,255), tool_part)
        self.grasp_boundary.draw(screen)