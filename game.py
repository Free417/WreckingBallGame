import pygame
from pygame.locals import *
from pygame.math import Vector2
from physics_objects import Polygon, Wall, Circle, UniformCircle, UniformPolygon
import contact 
import math
import time
from forces import Gravity
import random

# Initialize pygame and open window
pygame.init()
width, height = 800, 600
window = pygame.display.set_mode([width, height])

# Set timing variables
fps = 60
dt = 1/fps
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont('timesnewroman', 20)

# Variables
highscore = 0
current_score = 0
grabbing_player = False
stage = 1
lives = 3
timer = 1500
timePassed = -1
spawnTimer = 100
defaultEnemySpeed = 10
defaultMaxObjectRecovery = 1
startScreen = True
CENTER = Vector2(width/2, height/2)
GRAV_SPEED = 100

square_local_points = [ [0,0], [20,0], [20,20], [0,20]]
square_local_points.reverse()

triangle_local_points = [[-20, 0], [0, 40], [20, 0]]

pentagon_local_points = [[0,0], [0, -70 / 5], [66.57/5, -91.63/5], [107.73/5, -35/5], [66.57/5, 21.63/5]]
pentagon_local_points.reverse()

stick_local_points = [[-20, 0], [-20, 5], [20, 5], [20, 0]]

trapezoid_local_points = [[0,0], [20,0], [30,30], [5,30]]
trapezoid_local_points.reverse()

# set objects
objects = []
enemies = []
player = []
weapon = []
walls = []
objective = []
enemiesToDestroy = []

availableShapes = []

# Create a surface to use as the overlay
overlay_surface = pygame.Surface((width, height))

# Set the transparency level of the surface to 50%
overlay_surface.set_alpha(128)

# Fill the surface with a gray color
overlay_surface.fill((128, 128, 128))

player.append(Circle(window=window, pos=(400,250), vel = (0,0), mass= 100, radius=5, color=(255, 0, 255)))
player[0].contact_type = "Cable"
weapon.append(Circle(window=window, pos=(400,350), vel = (0,0), mass=100, radius=8, color=(0, 255, 0)))
walls.append(Wall(window=window, start_point=(0,600), end_point=(800,600), color=(0,255,0), reverse=True))
walls.append(Wall(window=window, start_point=(0,600), end_point=(0,0), color=(0,255,0)))
walls.append(Wall(window=window, start_point=(800,600), end_point=(800,0), color=(0,255,0), reverse=True))
walls.append(Wall(window=window, start_point=(0,0), end_point=(800,0), color=(0,255,0)))

# walls.append(Wall(window=window, start_point=(-50,650), end_point=(850,650), color=(0,255,0), reverse=True))
# walls.append(Wall(window=window, start_point=(-50,650), end_point=(-50,-50), color=(0,255,0)))
# walls.append(Wall(window=window, start_point=(850,650), end_point=(850,-50), color=(0,255,0), reverse=True))
# walls.append(Wall(window=window, start_point=(-50,-50), end_point=(850,-50), color=(0,255,0)))

objective.append(Circle(window=window, pos=(400,300), vel = (0,0), mass=math.inf, radius=40, color=(255, 255, 0)))
objective[0].lastTimeHit = -1

gravity_objects = weapon.copy()

objects = objective + player + weapon + enemies + walls

gravity = Gravity([0,GRAV_SPEED], objects_list=gravity_objects)

def ResetRound(clearEnemies = True):
    #Globals cuz I hate passing in vars
    global availableShapes
    global player
    global objects
    global stage
    global spawnTimer

    availableShapes.clear()

    if(clearEnemies):
        #Reset objects list to not include any enemies
        objects = objective + player + weapon + walls

    if stage >= 1:
        spawnTimer = 70
        availableShapes.append("Square")
        availableShapes.append("Square")
        availableShapes.append("Square")
        availableShapes.append("Square")
        availableShapes.append("Square")
        availableShapes.append("Square")
        availableShapes.append("Square")
        availableShapes.append("Square")
    if stage >= 2:
        spawnTimer = 50
        availableShapes.append("Triangle")
        availableShapes.append("Triangle")
    if stage >= 3:
        spawnTimer = 40
        availableShapes.append("Pentagon")
        availableShapes.append("Pentagon")
        availableShapes.append("Pentagon")
    if stage >= 4:
        spawnTimer = 35
        availableShapes.append("Stick")
    if stage >= 5:
        spawnTimer = 30
        availableShapes.append("Trapezoid")
        availableShapes.append("Trapezoid")
        availableShapes.append("Trapezoid")
        availableShapes.append("Trapezoid")
    SpawnShape()

def SpawnShape():
    global stage
    global availableShapes
    global enemies
   
    if(len(availableShapes) <= 0):
        print("No shapes to spawn")
        return

    #Pick a random shape
    randomPick = random.randrange(0,len(availableShapes))
    shapeString = availableShapes[randomPick]

    #Give it random values
    randomizedAvel = random.randint(-5, 5)
    randomColor = (random.randint(50, 200), random.randint(50, 200), random.randint(50,200))
    

    shapeToSpawn = False
    # print("Spawning " + shapeString)
    if shapeString == "Square":
        Square = UniformPolygon(window, density= 0.05, local_points = square_local_points, pos= (100, 100), avel = randomizedAvel, vel = Vector2(0,0), color = randomColor)
        Square.name = shapeString 
        Square.maxObjectRecovery = defaultMaxObjectRecovery
        Square.enemySpeed = defaultEnemySpeed
        shapeToSpawn = Square
        
    elif shapeString == "Triangle":
        Triangle = UniformPolygon(window, density= 0.05, local_points = triangle_local_points, pos= (100, 100), avel = 0, vel = Vector2(0,0), color = randomColor)
        Triangle.name = shapeString
        Triangle.maxObjectRecovery = defaultMaxObjectRecovery
        Triangle.enemySpeed = 50
        shapeToSpawn = Triangle

    elif shapeString == "Pentagon":
        Pentagon = UniformPolygon(window, density=0.07, local_points= pentagon_local_points, pos = (100,100), avel = randomizedAvel, vel = Vector2(0,0), color = randomColor)
        Pentagon.name = shapeString
        Pentagon.maxObjectRecovery = defaultMaxObjectRecovery
        Pentagon.enemySpeed = random.randint(5, 15)
        shapeToSpawn = Pentagon

    elif shapeString == "Stick":
        if(randomizedAvel >= 0):
            randomizedAvel = 5
        else:
            randomizedAvel = -5
        Stick = UniformPolygon(window, density=0.3, local_points= stick_local_points, pos = (100,100), avel = randomizedAvel,  vel = Vector2(0,0), color = randomColor)
        Stick.name = shapeString
        Stick.maxObjectRecovery = defaultMaxObjectRecovery
        Stick.enemySpeed = 5
        shapeToSpawn = Stick

    elif shapeString == "Trapezoid":
        Trapezoid = UniformPolygon(window, density=0.04, local_points= trapezoid_local_points, pos = (100,100), avel = randomizedAvel,  vel = Vector2(0,0), color = randomColor)
        Trapezoid.name = shapeString
        Trapezoid.maxObjectRecovery = defaultMaxObjectRecovery
        Trapezoid.enemySpeed = 14
        shapeToSpawn = Trapezoid
    else:
        # print("Unidentified shape " + str(shapeString) + " in shapes to spawn")
        return
    
    #Check if there's a shape to spawn (there should be)
    if(shapeToSpawn == False): 
        print("Somethings gone horribly wrong with spawning")
        return
    
    #Find valid position for the Shape to Spawn
    successfulPolygon = False
    iterations = 0
    while(successfulPolygon == False):
        iterations += 1
        if(iterations > 50):
            print("Couldn't find a valid placement")
            return

        x = 0
        y = 0
        #Spawn out of the left or right sides
        if(random.randrange(0, 2) == 0):
            y = random.randrange(0, height)
            if(random.randrange(0, 2) == 0): #left
                x = 0
            else: #right
                x = width 
    
        else: #Spawn out of the top or bottom
            x = random.randrange(0, width)
            if(random.randrange(0, 2) == 0):
                y = 0
            else:
                y = height

        shapeToSpawn.set_pos(Vector2(x, y))
        successfulPolygon = True
        for i in objects:
            if(i in walls):
                continue
            c = contact.generate(shapeToSpawn, i, Resolve= False)
            if c.overlap > 0:
                successfulPolygon = False
    objects.append(shapeToSpawn)
    enemies.append(shapeToSpawn)

# game loop
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    mouse_frame = Vector2(0,0)
    # update the display
    pygame.display.update()
    # delay for correct timing
    clock.tick(fps)
    window.fill((0,0,0))

    if(not startScreen):
        timePassed += 1

    if(timePassed % spawnTimer == 0):
        SpawnShape()

    # EVENT loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            if(startScreen):
                startScreen = False
                grabbing_player = True
                stage = 1
                current_score = 0
                ResetRound()
                lives = 3
                pygame.mouse.set_visible(False)
                pygame.mouse.set_pos(CENTER)
                ResetRound()

            #if (mouse_pos - player[0].pos).magnitude() < player[0].radius:
            #    player[0].mass = 100
            #    pygame.mouse.set_visible(False)
            #    pygame.mouse.set_pos(CENTER)
            #    grabbing_player = True
        
        #elif event.type == MOUSEBUTTONDOWN and event.button == 1 and grabbing_player == True:
            # player[0].mass = math.inf
            # player[0].vel = Vector2(0,0)
            # pygame.mouse.set_visible(True)
            # pygame.mouse.set_pos(player[0].pos)
            # grabbing_player = False

    

    if grabbing_player == True:
        mouse_frame = pygame.mouse.get_pos() - CENTER
        mouse_frame = Vector2(mouse_frame[0], mouse_frame[1])
        player[0].vel = mouse_frame*10
        pygame.mouse.set_pos(CENTER)
    
    key = pygame.key.get_pressed()

    # PHYSICS
    for o in objects:
        o.clear_force()

     # update objects
    for o in objects:
        o.update(dt)

    gravity.apply()
    if (player[0].pos - weapon[0].pos).magnitude() > 50:
        c = contact.generate(weapon[0], player[0], len = 50)
        if c.overlap > 0:
            c = contact.generate(player[0], weapon[0], resolve=True, restitution=0, len= 50)

    for i in range(len(objects)):
            for j in range(len(objects)):
                if i != j:
                    c = contact.generate(objects[i], objects[j])
                    if c.overlap > 0:
                        if player.count(objects[i]):
                            if walls.count(objects[j]):
                                c = contact.generate(player[0], objects[j], resolve=True, restitution=0.2)
                        elif weapon.count(objects[i]):
                            if walls.count(objects[j]):
                                c = contact.generate(weapon[0], objects[j], resolve=True, flipNormals = True, restitution=0.2)
                            elif enemies.count(objects[j]):
                                c = contact.generate(weapon[0], objects[j], resolve=True, flipNormals = True, restitution=0.2)
                            # elif player.count(objects[j]):
                            #     c = contact.generate(weapon[0], player[0], len = 50)
                            #     #c = contact.generate(player[0], weapon[0], len= 50)
                            #     if c.overlap > 0:
                            #         c = contact.generate(player[0], weapon[0], resolve=True, restitution=0, len= 50)
                        if enemies.count(objects[i]):
                            if objective.count(objects[j]): #If enemy is touching objective
                                enemiesToDestroy.append(objects[i])
                                lives -= 1
                            elif enemies.count(objects[j]):
                                c = contact.generate(objects[i], objects[j], resolve = True, restitution = 0.2)   
                            elif walls.count(objects[j]):
                                #print("Dot is " + str(objects[i].vel * objects[j].normal))
                                if(objects[i].vel * objects[j].normal < -3):
                                    if(startScreen):
                                        continue
                                    if(objects[i].name == "Square"):
                                        current_score += 2
                                    elif(objects[i].name == "Triangle"):
                                        current_score += 4
                                    elif(objects[i].name == "Pentagon"):
                                        current_score += 6
                                    elif(objects[i].name == "Stick"):
                                        current_score += 15
                                    elif(objects[i].name == "Trapezoid"):
                                        current_score += 4
                                    else:
                                        print("Unidentified object " + objects[i].name)
                                    
                                    


                                    enemiesToDestroy.append(objects[i])
    




    while(len(enemiesToDestroy) > 0):
        enemyToRemove = enemiesToDestroy.pop()
        if(enemyToRemove in enemies):
            enemies.remove(enemyToRemove)
        if(enemyToRemove in objects):
            objects.remove(enemyToRemove)
                                                     
    # if (player[0].pos - weapon[0].pos).magnitude() > 50:
    #     player[0].contact_type = "Cable"
    #     c = contact.generate(player[0], weapon[0], len= 50)
    #     if c.overlap > 0:
    #         c = contact.generate(player[0], weapon[0], resolve=True, restitution=0, len= 50)
    #     #player[0].contact_type = "Circle"
    
   

    # maxSpeed = 100
    # if(weapon[0].vel.x > maxSpeed or weapon[0].vel.y > maxSpeed):
    #     normalVel = weapon[0].vel.normalize()
    #     if(weapon[0].vel.x > weapon[0].vel.y):
    #         multiplyNum = 10 / normalVel.x 
    #     else:
    #         multiplyNum = 10 / normalVel.y
    #     weapon[0].vel = Vector2(normalVel.x * multiplyNum, normalVel.y * multiplyNum)
        

    

    #Update the enemy velocity so they always try to move towards the center at their max speed
    for o in enemies:
        velToObjective = objective[0].pos - o.pos
        velToObjective = velToObjective.normalize()
        changeOfVel = velToObjective * o.enemySpeed - o.vel

        #Clamp the change of velocity to be between -1 and 1 (so they dont recover too fast)
        changeOfVel.x = max(min(changeOfVel.x, o.maxObjectRecovery), -o.maxObjectRecovery)
        changeOfVel.y = max(min(changeOfVel.y, o.maxObjectRecovery), -o.maxObjectRecovery)

        o.vel += changeOfVel

    

    # collisions
    overlap = False
    contacts = []

    # check for contact with any other objects



    #Draw cable between player and weapon
    pygame.draw.line(window, color = (255,255,255), start_pos = player[0].pos, end_pos = Vector2(weapon[0].pos.x, weapon[0].pos.y), width = 1)
    # draw objects
    
    for o in objects:
        o.draw()

    # Blit the surface onto the window to display the overlay
    if(startScreen):
        start_text = font.render("Click anywhere to start the game", 1, (0,0,255))
        start_rect = start_text.get_rect(center=(width / 2, height / 2 - 100))
        window.blit(start_text, start_rect)
        window.blit(overlay_surface, (0, 0))

    if current_score > 60 and current_score < 150 and stage == 1:
        stage = 2
        lives+=1
        ResetRound()
    if current_score > 150 and current_score < 250 and stage == 2:
        stage = 3
        lives+=1
        ResetRound()
    if current_score > 210 and current_score < 320 and stage == 3:
        stage = 4
        lives+=1
        ResetRound()
    if current_score > 440 and stage == 4:
        stage = 5
        lives+=1
        ResetRound()

    if lives > 0:
        lives_text = font.render(f"Remaining Lives: {lives}", 1, (0,0,255))
        lives_rect = lives_text.get_rect(center=(90,20))
        window.blit(lives_text, lives_rect)
        score_text = font.render(f"Score: {current_score}", 1, (0,0,255))
        score_rect = score_text.get_rect(center=(740,20))
        window.blit(score_text, score_rect)
        stage_text = font.render(f"Current Stage: {stage}", 1, (0,0,255))
        stage_rect = stage_text.get_rect(center=(75,580))
        window.blit(stage_text, stage_rect)
        
    else:
        if current_score > highscore:
            highscore = current_score
            gameover_1_text = font.render(f"Game over.", 1, (0,0,255))
            gameover_1_rect = lives_text.get_rect(center=(400,260))
            window.blit(gameover_1_text, gameover_1_rect)
            gameover_2_text = font.render(f"New highscore: {current_score}", 1, (0,0,255))
            gameover_2_rect = lives_text.get_rect(center=(400,300))
            window.blit(gameover_2_text, gameover_2_rect)
        else:
            gameover_1_text = font.render(f"Game over.", 1, (0,0,255))
            gameover_1_rect = lives_text.get_rect(center=(400,260))
            window.blit(gameover_1_text, gameover_1_rect)
            gameover_2_text = font.render(f"Your Score: {current_score}", 1, (0,0,255))
            gameover_2_rect = lives_text.get_rect(center=(400,300))
            window.blit(gameover_2_text, gameover_2_rect)
            gameover_3_text = font.render(f"Highscore: {highscore}", 1, (0,0,255))
            gameover_3_rect = lives_text.get_rect(center=(400,340))
            window.blit(gameover_3_text, gameover_3_rect)
        startScreen = True
        