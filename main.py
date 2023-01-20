import sys
import itertools
import random

import numpy
import pygame

# Constants
G = 6.673 * (10 ** -11)

offset_x = 0
offset_y = 0
zoom = 1

# Settings
FPS = 120

drag = 0.000001
coll_loss = 0.000001

res_x = 2560
res_y = 1440

zoom_factor = 0.98

# Colors
white = pygame.Color(255, 255, 255)
black = pygame.Color(0, 0, 0)
gray = pygame.Color(128, 128, 128)
green = pygame.Color(0, 128, 0)

bodies = []
traces = []
# trails = [] TO-DO

# Switches
trace = False
edges = True
gravity = True
collision_color = False

usr_id = 999999999

# Initiate Game
screen = pygame.display.set_mode((res_x, res_y), pygame.DOUBLEBUF | pygame.OPENGL | pygame.NOFRAME)
screen_rect = screen.get_rect()
screen.set_alpha(None)

display = pygame.Surface((res_x, res_y))
display_rect = display.get_rect()
display.set_colorkey(black)

pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])

pygame.init()
screen = pygame.display.set_mode((res_x, res_y))
pygame.display.set_caption('Space')
fpsClock = pygame.time.Clock()
id_iter = itertools.count()


class Body:

    def __init__(self, c=gray, r=25, p=(0, 0), v=(0, 0)):
        """
        c -- color (default gray)
        r -- radius (default 25)
        p -- cartesian position x, y (default 0, 0)
        ap -- afterimage position x, y (default 0, 0)
        v -- velocity x,y (default 0.0)
        s -- size
        m -- mass
        """

        self.id = next(id_iter)

        self.c = c
        self.r = r
        self.fr = r * zoom
        self.p = p
        self.ap = p
        self.v = v
        self.m = 2 * (10 ** 9) * numpy.pi * (self.r ** 2)

    def draw(self):

        pygame.draw.circle(display, self.c, cptosp(self.p), self.fr)

    def tracer(self):
        # Velocity cant be zero and radius has to be bigger than 1.5
        if self.v[0] != 0 and self.v[1] != 0 and self.fr >= 1.5 and trace:
            traces.append(Trace(self.p, numpy.subtract(self.c, (35, 35, 35, 0)), self.fr, self.v))

    def zoom(self, zoom_factor):
        self.r = self.r / zoom_factor
        self.fr = self.r * zoom
        self.v = numpy.divide(self.v, zoom_factor)
        self.m = 2 * (10 ** 9) * numpy.pi * (self.r ** 2)

        # Deletes traces when zooming
        return []

    def gravity(self):
        for body in bodies:
            if self == body:
                continue

            disx, disy = numpy.subtract(body.p, self.p)
            d = numpy.sqrt((disx ** 2) + (disy ** 2))

            sumr = self.r + body.r

            angle = numpy.arctan2(disy, disx)

            # Collision detection
            if d <= sumr and self.id != usr_id and body.id != usr_id:
                self.collision(body, angle)

                if collision_color:
                    self.c = numpy.random.randint(40, 255, 3)
                    body.c = numpy.random.randint(40, 255, 3)
                break

            if gravity:
                f = G * body.m * self.m / (d ** 2)
                self.v += f * numpy.array([numpy.cos(angle), numpy.sin(angle)]) / self.m

        limit = 60
        self.v = numpy.clip(self.v, -limit, limit)
        self.p += self.v * (1 - drag)

    # Teleports body to the other side of the screen if it hits the edge.
    def edge(self):
        p = cptosp(self.p)

        if p[0] <= 0:
            self.p = sptocp((res_x, res_y - p[1]))
        elif p[0] >= res_x:
            self.p = sptocp((0, res_y - p[1]))

        if p[1] <= 0:
            self.p = sptocp((res_x - p[0], res_y))
        elif p[1] >= res_y:
            self.p = sptocp((res_x - p[0], 0))

    def collision(self, body, angle):
        velocities = numpy.array([self.v, body.v])
        collision_matrix = numpy.array([[(self.m - body.m) / (self.m + body.m), 2 * body.m / (self.m + body.m)],
                                        [2 * self.m / (self.m + body.m), (body.m - self.m) / (self.m + body.m)]])
        new_velocities = numpy.dot(collision_matrix, velocities)
        self.v = new_velocities[0] - (new_velocities[0] * coll_loss)
        body.v = new_velocities[1] - (new_velocities[1] * coll_loss)

    # Some bodies do this weird merge when they get too close to each other.
    # This function fixes that even if it is very resource intensive
    def overlap(self):
        for body in bodies:

            if body == self:
                continue

            disx, disy = numpy.subtract(body.p, self.p)

            d = numpy.sqrt((disx ** 2) + (disy ** 2))
            sumr = self.r + body.r

            if d >= sumr:
                continue

            angle = numpy.arctan2(disy, disx)

            # Disposition if overlapping (px - (radia - distance * cos(angle), py - (radia - distance * sin(angle)
            self.p = numpy.subtract(self.p, ((sumr - d) * numpy.cos(angle), (sumr - d) * numpy.sin(angle)))


class Trace:
    def __init__(self, p, c, fr, v):
        """
        p -- cartesian position x, y (default 0, 0)
        c -- color (default gray)
        fr -- fake radius (default 25)
        v -- velocity x,y (default 0.0)
        """

        self.p = p
        self.c = c
        self.fr = fr
        self.v = v

        if 1 < int(-self.v[0]):
            vx = random.randint(1, int(-self.v[0])) / 12
        else:
            vx = random.randint(int(-self.v[0]), 1) / 12
        if 1 < int(-self.v[1]):
            vy = random.randint(1, int(-self.v[1])) / 12
        else:
            vy = random.randint(int(-self.v[1]), 1) / 12

        self.v = vx, vy
        self.fr = random.randint(1, int(self.fr / 1.5))

    def update(self):
        self.p = numpy.add(self.v, self.p)
        self.fr -= 0.5

    def draw(self):
        pygame.draw.circle(display, self.c, cptosp(self.p), self.fr)


def sptocp(p):
    cartesianx = (p[0] - offset_x - res_x / 2) / zoom
    cartesiany = (p[1] - offset_y - res_y / 2) / -zoom

    return cartesianx, cartesiany


def cptosp(p):
    screenx = res_x / 2 + zoom * p[0] + offset_x
    screeny = res_y / 2 - zoom * p[1] + offset_y

    return screenx, screeny


def reset():
    bodies = []
    traces = []

    bodies.append(Body(p=(0, 300), v=(3, 0), r=5, c=white))
    bodies.append(Body(p=(0 + 150, 200), v=(3, 0), r=5, c=white))
    bodies.append(Body(p=(0, 0), r=75))

    return bodies, traces, itertools.count(0)


bodies, traces, id_iter = reset()

# Flags and temps
firstpos = 0
s_pressed = False
focused_body = None

# Game Loop
while True:
    fpsClock.tick(FPS)
    display.fill((15, 15, 15))
    m_spos = pygame.mouse.get_pos()
    m_cpos = sptocp(m_spos)

    # Move usr body to cursor position
    if bodies[-1].id == usr_id:
        try:
            bodies[-1].p = m_cpos
        except AttributeError:
            pass

    # Screen drag
    if firstpos != 0:
        offset_x, offset_y = numpy.add(numpy.subtract(m_spos, firstpos), (oldoffset_x, oldoffset_y))

    # Adjust focus
    if focused_body != None:
        offset_x = -focused_body.p[0]
        offset_x *= zoom
        offset_y = focused_body.p[1]
        offset_y *= zoom

    # Quit Handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        # Toggle between Insert and Focus mode
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_s:
                s_pressed = not s_pressed
                focused_body = None

        # Reset
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_e:
                focused_body = None
                bodies, traces, id_iter = reset()

        # Focus mode
        if s_pressed:
            if event.type == pygame.KEYUP:
                # Switch between bodies
                if event.key == pygame.K_d:
                    if focused_body == None:
                        focused_body = bodies[0]
                    elif focused_body.id != len(bodies)-1:
                        focused_body = bodies[focused_body.id+1]
                    else:
                        focused_body = bodies[0]

                elif event.key == pygame.K_a:
                    if focused_body == None:
                        focused_body = bodies[-1]
                    elif focused_body.id != 0:
                        focused_body = bodies[focused_body.id-1]
                    else:
                        focused_body = bodies[-1]

            # Finding body per click
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for body in bodies:
                        dx, dy = numpy.abs(numpy.subtract(m_cpos, body.p))
                        R = body.r
                        if dx + dy <= R:
                            focused_body = body
                        elif dx ** 2 + dy ** 2 <= R ** 2:
                            focused_body = body
                # Little bit of debugging on right click
                elif event.button == 3:
                    print(fpsClock.get_fps())
                    print(len(traces))

        # Interaction mode
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    bodies.append(Body(p=m_cpos, c=black, r=2))
                    bodies[-1].m = (2 * (10 ** 9) * numpy.pi * (90 ** 2))
                    bodies[-1].id = usr_id

                elif event.button == 3:
                    bodies.append(Body(p=m_cpos, c=black, r=2))
                    bodies[-1].m = -(2 * (10 ** 9) * numpy.pi * (90 ** 2))
                    bodies[-1].id = usr_id

            if event.type == pygame.MOUSEBUTTONUP and bodies[-1].id == usr_id:
                if event.button != 4 and event.button != 5:
                    bodies.remove(bodies[-1])

        # Drag screen
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 2:
                oldoffset_x = offset_x
                oldoffset_y = offset_y
                firstpos = m_spos

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                firstpos = 0

        # Zoom
        if event.type == pygame.MOUSEWHEEL and not edges:
            if event.y == 1:
                for body in bodies:
                    zoom /= zoom_factor
                    offset_x /= zoom_factor
                    offset_y /= zoom_factor
                    traces = body.zoom(zoom_factor)
            if event.y == -1:
                for body in bodies:
                    zoom /= (1 / zoom_factor)
                    offset_x /= (1 / zoom_factor)
                    offset_y /= (1 / zoom_factor)
                    traces = body.zoom((1 / zoom_factor))

    # Delete small traces
    for trace in traces:
        trace.update()
        if trace.fr <= 0.99:
            traces.remove(trace)

    # Update bodies
    for body in bodies:
        # Get Position and Velocity
        body.gravity()

        # Edge Detection
        if edges:
            body.edge()

        # Overlap Protection
        body.overlap()

        # Tracing
        if body.id != usr_id:
            body.tracer()

    # Draws traces
    for trace in traces:
        trace.draw()

    # Draws bodies
    for body in bodies:
        body.draw()

    screen.blit(display, (0, 0))
    pygame.display.update()
    pygame.display.flip()
