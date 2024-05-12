from cmath import cos, sin
import math
import numpy
import pygame
import random
from vector import Vector, random_vector
import vector

pygame.init()


class Agent:
    def __init__(
        self,
        position: Vector,
        newPos: Vector,
        angle: float,
        sight: float,
        minDist: float,
        predator: bool,
        dx: float,
        dy: float,
        size: float,
        color: float
    ):
        self.position = position
        self.angle = angle
        self.sight = sight
        self.minDist = minDist
        self.newPos = newPos
        self.predator = predator
        self.dx = dx
        self.dy = dy
        self.size = size
        self.randomColor = color


delta_time = 0.0
clock = pygame.time.Clock()


# changeable variables ( for customization )
num_agents = 50
num_predators = 1
screen_x = 1000
screen_y = 600
max_speed = 3
predator_max_speed = 2
follow_mouse = False
backgroundAlpha = 50

screen = pygame.display.set_mode((screen_x, screen_y))
agent_array = numpy.empty(num_agents, dtype=Agent)
agentStartingAngle = random.random() * 180  # redundant
direction = Vector(0, 0)

pygame.mouse.set_visible(False)
backgroundPic = pygame.transform.scale(pygame.image.load(
    "background.png").convert_alpha(), (screen_x, screen_y))
backgroundRect = backgroundPic.get_rect(
    center=(screen_x / 2, screen_y / 2))


# make agents
for n in range(num_agents):

    agent_array[n] = Agent(
        Vector(
            random.random() * screen_x, random.random() * screen_y),
        Vector(0, 0),
        agentStartingAngle,
        100,
        20.0,  # TEMP
        False,
        random.random(),
        random.random(),
        10,
        random.random() * 100
    )


# set predators
totalPredators = 0
for n in agent_array:
    if (num_predators > 0):
        n.predator = True
        n.sight = n.sight*3
        totalPredators += 1
        if (totalPredators == num_predators):
            break

simRunning = True
agentStart = True


# ---------------------------------------------------------------------------------------------------
# Boid Functions ------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------

def distance(boid1: Agent, boid2: Agent):
    return math.sqrt((boid1.position.x - boid2.position.x) ** 2 + (boid1.position.y - boid2.position.y)**2)

def updateBoid(boid):
    group_center_x = 0
    group_center_y = 0

    average_dx = 0
    average_dy = 0

    avoid_boids_x = 0
    avoid_boids_y = 0

    avoid_predator_x = 0
    avoid_predator_y = 0

    numNeighbors = 0


    for otherBoid in agent_array:
        if boid != otherBoid:
            dist = distance(boid, otherBoid)
            if dist < boid.sight:
                group_center_x += otherBoid.position.x
                group_center_y += otherBoid.position.y

                average_dx += otherBoid.dx
                average_dy += otherBoid.dy

                numNeighbors += 1
                if dist < boid.minDist:
                    avoid_boids_x += boid.position.x - otherBoid.position.x
                    avoid_boids_y += boid.position.y - otherBoid.position.y

                if otherBoid.predator:
                    avoid_predator_x += boid.position.x - otherBoid.position.x
                    avoid_predator_y += boid.position.y - otherBoid.position.y

    if (numNeighbors):
        flyTowardsCenter(boid, group_center_x, group_center_y, numNeighbors)
        matchVelocity(boid, numNeighbors, average_dx, average_dy)
        avoidBoids(boid, avoid_boids_x, avoid_boids_y)
        if not boid.predator:
            avoidPredator(boid, avoid_predator_x, avoid_predator_y)
        else:
            chaseAgents(boid, group_center_x, group_center_y, numNeighbors)


def avoidPredator(boid: Agent, avoid_x, avoid_y):
    #degree to which avoid predator
    avoidFactor = 0.002

    #avoid predator
    boid.dx += avoid_x * avoidFactor
    boid.dy += avoid_y * avoidFactor


def avoidBoids(boid: Agent, avoid_x, avoid_y):
    #degree to which avoid other boids in vicinity
    avoidFactor = 0.003

    #avoid other boids
    boid.dx += avoid_x * avoidFactor
    boid.dy += avoid_y * avoidFactor

def flyTowardsCenter(boid, centerX, centerY, numNeighbors):
    #degree to which boids fly towards center
    centeringFactor = 0.0005

    #find center average of surrounding boids
    centerX = centerX / numNeighbors
    centerY = centerY / numNeighbors

    #fly towards defined center
    boid.dx += (centerX - boid.position.x) * centeringFactor
    boid.dy += (centerY - boid.position.y) * centeringFactor


def matchVelocity(boid, numNeighbors, average_dx, average_dy):
    #degree to which the boids align with one another
    matchingFactor = 0.05 

    #find average dir
    average_dx = average_dx / numNeighbors
    average_dy = average_dy / numNeighbors

    #align boid with defined average dir
    boid.dx += (average_dx - boid.dx) * matchingFactor
    boid.dy += (average_dy - boid.dy) * matchingFactor


def limitSpeed(boid):
    if not boid.predator:
        speedLimit = max_speed
    else:
        speedLimit = predator_max_speed

    speed = math.sqrt(boid.dx * boid.dx + boid.dy * boid.dy)

    if (speed > speedLimit):
        boid.dx = (boid.dx / speed) * speedLimit
        boid.dy = (boid.dy / speed) * speedLimit

def avoidEdge(boid):
    avoidFactor = 0.0027
    avoid_x = 0
    avoid_y = 0
    marginSight = boid.sight

    if boid.position.x < marginSight:
        avoid_x += boid.position.x
    if boid.position.x > screen_x - marginSight:
        avoid_x += boid.position.x - screen_x
    if boid.position.y < marginSight:
        avoid_y += boid.position.y
    if boid.position.y > screen_y - marginSight:
        avoid_y += boid.position.y - screen_y

    boid.dx += avoid_x * avoidFactor
    boid.dy += avoid_y * avoidFactor


def chaseAgents(boid, center_x, center_y, num_of_prey):

    chaseFactor = 0.004
    center_x = center_x / num_of_prey
    center_y = center_y / num_of_prey
    boid.dx += (center_x - boid.position.x) * chaseFactor
    boid.dy += (center_y - boid.position.y) * chaseFactor


def moveAgent(n: Agent):
    if agentStart:
        direction = Vector(n.dx, n.dy)


# checks for out of bounds

        if (n.position + direction).x >= screen_x or (
            n.position + direction
        ).x <= 0:
            n.newPos = Vector(
                screen_x - n.position.x, n.position.y)

        elif (n.position + direction).y >= screen_y or (
            n.position + direction
        ).y <= 0:
            n.newPos = Vector(
                n.position.x, screen_y - n.position.y)

        else:
            n.newPos = n.position + direction

        n.position = n.newPos

        if n.predator and follow_mouse:
            mousePos = pygame.mouse.get_pos()
            n.position.x = mousePos[0]
            n.position.y = mousePos[1]


def update():
    for n in agent_array:
        updateBoid(n)
        if not n.predator:
            limitSpeed(n)
            avoidEdge(n)
            moveAgent(n)
        if n.predator:
            limitSpeed(n)
            moveAgent(n)

    pass


def draw():

    backgroundPic.set_alpha(backgroundAlpha)

    screen.blit(backgroundPic, backgroundRect)

    for n in agent_array:
        if not n.predator:
            pygame.draw.ellipse(
                screen,
                (75 + n.randomColor, 75 + n.randomColor, 155 + n.randomColor),
                pygame.Rect(n.position.x, n.position.y, n.size, n.size))
        if n.predator:
            pygame.draw.ellipse(
                screen,
                (155 + n.randomColor, n.randomColor, n.randomColor),
                pygame.Rect(n.position.x, n.position.y, n.size, n.size))


while simRunning:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            simRunning = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                simRunning = False
            if event.key == pygame.K_1:
                max_speed += 0.5
            if event.key == pygame.K_2:
                max_speed -= 0.5
            if event.key == pygame.K_3:
                predator_max_speed += 0.5
            if event.key == pygame.K_4:
                predator_max_speed -= 0.5
            if event.key == pygame.K_f:
                follow_mouse = not follow_mouse
            if event.key == pygame.K_5:
                if backgroundAlpha > 10:
                    backgroundAlpha -= 10
                else:
                    backgroundAlpha = 0

            if event.key == pygame.K_6:
                if backgroundAlpha < 245:
                    backgroundAlpha += 10
                else:
                    backgroundAlpha = 255

    update()
    draw()

    pygame.display.flip()

    delta_time = 0.001 * clock.tick(144)


pygame.quit()
