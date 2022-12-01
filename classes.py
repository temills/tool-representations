
class Ball():
    def __init__(self, x, y, collision_type=1):
        self.body = pm.Body()
        self.body.position = x,y
        self.body.velocity = 0,0
        self.body.mass = 1000
        self.rad = 8
        self.shape = pm.Circle(self.body, 8)
        self.shape.density = 1
        self.shape.friction = 1
        self.shape.elasticity = 1
        space.add(self.body, self.shape)
        self.shape.collision_type = collision_type

    def draw(self):
        x,y = self.body.position
        #self.body.velocity = int(self.body.velocity[0]>0)*(-10) + self.body.velocity[0], int(self.body.velocity[1]>0)*(-10) + self.body.velocity[1]
        pg.draw.circle(screen, GREEN, (int(x),int(y)), 8)


class Wall():
    def __init__(self, vs):
        self.body = pm.Body(body_type=pm.Body.STATIC)
        self.shape = pm.Poly(self.body, vs)
        self.shape.elasticity = 1
        self.shape.friction = 1
        self.shape.density = 1
        space.add(self.body, self.shape)
    
    def draw(self):
        #pg.draw.polygon(screen, BLACK, [self.body.local_to_world(v) for v in self.shape.get_vertices()])
        pg.draw.polygon(screen, BLACK, [v for v in self.shape.get_vertices()])

class Goal():
    def __init__(self, left, top, width, height):
        self.goal_loc = pg.Rect(left, top, width, height)
    
    def draw(self):
        pygame.draw.rect(surface, color, self.goal_loc)

class GraspZone():
    def __init__(self, y):
        self.y = y
    
    def draw(self):
        pg.draw.line(screen, BLACK, (0, self.y), (SCREEN_WIDTH, self.y))

class ToolPart():
    def __init__(self, vs):
        self.body = pm.Body(body_type=pm.Body.KINEMATIC)
        self.shape = pm.Poly(self.body, vs)
        self.shape.friction = 1
        space.add(self.body, self.shape)

class Tool():
    def __init__(self, parts, collision_type=3):
        self.toolpart1 = ToolPart(parts[0])
        self.toolpart2 = ToolPart(parts[1])

        self.part_list = [self.toolpart1, self.toolpart2]
        self.mode = 'move'
        self.is_grasped = False
        self.grasp_point = pm.Body(body_type=pm.Body.KINEMATIC)

    def draw(self):       
        #stays the same as first grasp
        x,y = self.part_list[0].body.center_of_gravity
        for tp in self.part_list:
            #draw tool part
            pg.draw.polygon(screen, BLUE, [tp.body.local_to_world(v) for v in tp.shape.get_vertices()])
        #draw grasper
        if self.is_grasped:
            pg.draw.circle(screen, RED, self.grasp_point.position, 3)
    
    def grasp(self, cog, grasp_zone):
        if not self.is_grasped:
            if cog[1] > grasp_zone.y:
                self.is_grasped = True
                self.grasp_point._set_position(cog)
                space.add(self.grasp_point)
                for tp in self.part_list:
                    old_pos = tp.body.position
                    tp.body._set_center_of_gravity(cog)
                    tp.body._set_position(old_pos)
        
    def set_mode(self, mode):
        if mode in ['move', 'rotate']:
            self.mode = mode

    def make_move(self, dir, wall_list, ball, grasp_zone):
        if self.is_grasped:
            if self.mode=='move':
                self.move(dir, wall_list, ball, grasp_zone)
            else:
                self.rotate(dir, wall_list, ball)

    def move(self, dir, wall_list, ball, grasp_zone):
        if dir=='u':
            vx, vy = 0, -50
        elif dir=='d':
            vx, vy = 0, 50
        elif dir=='r':
            vx, vy = 50, 0
        elif dir=='l':
            vx, vy = -50, 0
        

        #first check if grasp pos will go above grasp zone, stop if so
        if(self.grasp_point.position[1] + (vy/100) < grasp_zone.y):
            self.stop()
            return

        #next check if any tool part will hit a wall, stop if so
        wall_polys = [[wall.body.local_to_world(v) for v in wall.shape.get_vertices()] for wall in wall_list]
        for tp in self.part_list:
            tp_poly = [(tp.body.local_to_world(v)[0] + (vx/100), tp.body.local_to_world(v)[1] + (vy/100))  for v in tp.shape.get_vertices()]
            #if(poly_circle_intersect([tp.body.local_to_world(v) for v in tp.shape.get_vertices()], ball.body.position[0], ball.body.position[1], ball.rad)):
            #    print("here")
            #    self.stop()
            #    return
            for wall_poly in wall_polys:
                if(do_polygons_intersect(tp_poly, wall_poly)):
                    self.stop()
                    return
        for tp in self.part_list:
            tp.body.velocity = vx, vy
        self.grasp_point.velocity = vx, vy

    def rotate(self, dir, wall_list, ball):
        if dir=='r':
            #calc vx and vy (or va?) according to grasp point
            va = .2
        elif dir=='l':
            #calc vx and vy (or va?) according to grasp point
            va = -.2
        else:
            return

        wall_polys = [[wall.body.local_to_world(v) for v in wall.shape.get_vertices()] for wall in wall_list]
        for tp in self.part_list:
            tp_poly = [tp.body.local_to_world(rotate_vertex(tp.body.center_of_gravity, v, va/40)) for v in tp.shape.get_vertices()]
            #if(poly_circle_intersect([tp.body.local_to_world(v) for v in tp.shape.get_vertices()], ball.body.position[0], ball.body.position[1], ball.rad)):
            #    self.stop()
            #    return
            for wall_poly in wall_polys:
                if(do_polygons_intersect(tp_poly, wall_poly)):
                    self.stop()
                    return
        for tp in self.part_list:
            tp.body.angular_velocity = va
            space.reindex_shapes_for_body(tp.body)
    
    def stop(self):
        self.grasp_point.velocity = 0,0
        for tp in self.part_list:
            tp.body.velocity = 0,0
            tp.body.angular_velocity = 0



class GameState():
    def __init__(self, wall_pos, ball_pos, tool_parts, grasp_pos, goal_pos):
        self.init_params = (wall_pos, ball_pos, tool_parts, grasp_pos, goal_pos)
        self.reset()

    def reset(self):
        (wall_pos, ball_pos, tool_pos, tool_parts, grasp_pos, goal_pos) = self.init_params
        self.ball = Ball(ball_pos[0],ball_pos[1])
        self.wall_list = [Wall(wp) for wp in wall_pos]
        self.tool = Tool(tool_parts)
        self.grasp_zone = GraspZone(grasp_pos)
        self.goal = pg.Rect(goal_pos)
        self.success = False

    def draw(self):
        pg.draw.rect(screen, (0,255,0), self.goal)
        self.ball.draw()
        for wall in self.wall_list:
            wall.draw()
        self.tool.draw()
        self.grasp_zone.draw()