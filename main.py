import os
import random, datetime

script_dir = os.path.dirname(__file__)

import math

import pygame
pygame.init()

def sign(x):
    return 1 if x >= 0 else -1
def stdblit(image_name, pos=(0,0), scale=None):
    if scale == None:
        screen.blit(stdload(image_name), pos)
    else:
        screen.blit(pygame.transform.scale(stdload(image_name), scale), pos)
def stdload(image_name):
    return pygame.image.load(os.path.join(script_dir, "media", "images", (image_name + ".png"))).convert_alpha()
def maketext(text, color=(255, 255, 255), size=24, fon=None):
    return pygame.font.Font(fon, size).render(text, True, color)

import ctypes

screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
ctypes.windll.user32.ShowWindow(pygame.display.get_wm_info()['window'], 3)

car_x, car_y = 297, 615
x_velocity, y_velocity = 0, 0
cardir = 0
turnspeed = 0

racetype = "hill"
racemedia = {
    "hill": {
        "map": "hillmap",
        "back": "backhill",
        "car": "carmap",
        "color": "#656565",
        "issue": "tree"
    },
    "desert": {
        "map": "desertmap",
        "back": "backdesert",
        "car": "carmap",
        "color": "#726248",
        "issue": "cactus",
    },
    "sea": {
        "map": "seamap",
        "back": "backsea",
        "car": "carmap",
        "color": "#575757",
        "issue": "rock",
    },
    "city": {
        "map": "citymap",
        "back": "backcity",
        "car": "carmap",
        "color": "#424248",
        "issue": "building",
    }
}

mapmask = pygame.mask.from_surface(stdload(racemedia[racetype]["map"]))
carmask = pygame.mask.from_surface(stdload("carmap"))
issuemask = pygame.mask.from_surface(stdload("issuemap"))

def is_solid(x, y):
    offset = int(x), int(y)
    result = mapmask.overlap(carmask, offset)
    return result is not None

on_street = False
def cartrace(player_x, player_y, dire):
    global on_street
    touches = []
    linetouches = []
    start_x, start_y = player_x, player_y

    stepx = math.cos(math.radians(dire))
    stepy = math.sin(math.radians(dire))

    # Start by checking if we're on a street or not
    on_street = False

    while 0 <= player_x <= 700 and 0 <= player_y <= 700:
        while 0 <= player_x <= 700 and 0 <= player_y <= 700 and is_solid(player_x, player_y) == on_street:
            player_x += stepx
            player_y += stepy

        # Record the transition point & Flip what we're searching for next
        touches.append((player_x, player_y))
        on_street = not on_street

    # Convert to distances from start
    sqtouches = []
    for hit in touches:
        sqtouches.append(math.sqrt((hit[0] - start_x) ** 2 + (hit[1] - start_y) ** 2))
        sqtouches[-1] = sqtouches[-1] * math.cos(math.radians(dire - cardir))

    return sqtouches if len(sqtouches) > 0 else None

sc_height = screen.get_height()
def carpaint(rays):
    global sc_height
    def dperp(distance):
        return (sc_height * (1 - (223 / 360))) + 20000 / (distance + 5000 / (sc_height * (223 / 1440))) - 20000 / 989

    for col in range(rays):
        col_angle = cardir + (90 * col / rays) - 45
        result = cartrace(car_x, car_y, col_angle)

        # Draw road column
        if result is not None:
            cast = [round(x) for x in result]
            for i in range(0, len(cast) - 1, 2):
                column = pygame.Rect(
                    col * (screen.get_width() / rays),
                    dperp(cast[i + 1]),
                    (screen.get_width() / rays) + 1,
                    dperp(cast[i]) - dperp(cast[i + 1])
                )
                linecolumn1 = pygame.Rect(
                    col * (screen.get_width() / rays),
                    dperp(cast[i + 1]),
                    (screen.get_width() / rays) + 1,
                    3
                )
                linecolumn2 = pygame.Rect(
                    col * (screen.get_width() / rays),
                    dperp(cast[i]),
                    (screen.get_width() / rays) + 1,
                    3
                )
                pygame.draw.rect(screen, racemedia[racetype]["color"], column)
                pygame.draw.rect(screen, "#cacaca", linecolumn1)
                pygame.draw.rect(screen, "#cacaca", linecolumn2)

def mouse_in_rect(rect):
    mousex, mousey = pygame.mouse.get_pos()
    if rect[0] <= mousex < rect[0] + rect[2] and rect[1] <= mousey < rect[1] + rect[3]:
        return True
    return False

def mouserelease():
    wait = True
    while wait:
        pygame.event.pump()
        if not pygame.mouse.get_pressed()[0]:
            wait = False

pause = False
finished = False
finishdelay = 0
racestarted = False
racestarttime = -1
currentcheckpoint = 0
touchingcheckpoint = False

def stdaudio(audio_name):
    return os.path.join(os.path.dirname(__file__), "media", "audio", audio_name)
carengine = pygame.mixer.Sound(stdaudio("engine-6000.wav"))
checkbell = pygame.mixer.Sound(stdaudio("bell-98033.wav"))
carengine.set_volume(0.3)
checkbell.set_volume(0.3)

pygame.mixer.music.load(os.path.join(os.path.dirname(__file__), "media", "audio", "runners.wav"))
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(loops=-1)

running = True
menu = "main"
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if menu == "main":
                    if mouse_in_rect((screen.get_width() / 2 - 174, 340, 348, 80)):
                        menu = "selectmap"
                elif menu == "selectmap":
                    x_velocity, y_velocity = 0, 0
                    if mouse_in_rect((screen.get_width() / 2 - 174, 340, 348, 80)):
                        menu = "racemap"
                        racetype = "hill"
                        mapmask = pygame.mask.from_surface(stdload(racemedia[racetype]["map"]))
                        car_x, car_y = 297, 615
                        cardir = 0
                        turnspeed = 0
                        pause = False
                        finished = False
                        currentcheckpoint = 0
                    if mouse_in_rect((screen.get_width() / 2 - 174, 430, 348, 80)):
                        menu = "racemap"
                        racetype = "desert"
                        mapmask = pygame.mask.from_surface(stdload(racemedia[racetype]["map"]))
                        car_x, car_y = 323, 533
                        cardir = 90
                        turnspeed = 0
                        pause = False
                        finished = False
                        currentcheckpoint = 0

                        pygame.mixer.music.load(os.path.join(os.path.dirname(__file__), "media", "audio", "mexica.wav"))
                        pygame.mixer.music.set_volume(0.2)
                        pygame.mixer.music.play(loops=-1)
                elif menu == "racemap":
                    if mouse_in_rect((screen.get_width() - 80, 0, 80, 80)) or pygame.key.get_pressed()[pygame.K_ESCAPE]:
                        pause = True
                        pygame.mouse.set_visible(True)
                    if mouse_in_rect((screen.get_width() / 2 - 174, 340, 348, 80)):
                        pause = False
                    if mouse_in_rect((screen.get_width() / 2 - 174, 430, 348, 80)):
                        menu = "main"
                wait = True
                while wait:
                    pygame.event.pump()
                    if not pygame.mouse.get_pressed()[0]:
                        wait = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                pause = True
                pygame.mouse.set_visible(True)

    if menu == "main":
        pygame.mouse.set_visible(True)
        stdblit("backscreen", (0,0), (screen.get_width(), screen.get_height()))
        stdblit("dr2", (50,60), (631, 172))
        stdblit("playbutton", (screen.get_width() / 2 - 174, 340))

    elif menu == "selectmap":
        racestarted = False
        stdblit("backscreen", (0,0), (screen.get_width(), screen.get_height()))
        stdblit("dr2", (50,60), (631, 172))
        stdblit("playhill", (screen.get_width() / 2 - 174, 340))
        stdblit("playdesert", (screen.get_width() / 2 - 174, 430))
        stdblit("playsea", (screen.get_width() / 2 - 174, 520))

    elif menu == "racemap":
        if pygame.mask.from_surface(stdload("checkpoint" + str(currentcheckpoint % 8 + 1) + racemedia[racetype]["map"])).overlap(carmask, (int(car_x), int(car_y))) is not None:
            if not touchingcheckpoint:
                if currentcheckpoint == 0 and not racestarted:
                    racestarted = True
                currentcheckpoint += 1
                checkbell.play()
                touchingcheckpoint = True
        else:
            touchingcheckpoint = False

        laps = 1
        if currentcheckpoint == 8 * laps + 1:
            if not finished:
                ticksduration = pygame.time.get_ticks() - racestarttime
                finished = True
                racestarted = False

        stdblit(racemedia[racetype]["back"], (0,0), (screen.get_width(), screen.get_height()))
        carpaint(100)
        stdblit("view", (0,0), (screen.get_width(), screen.get_height()))
        screen.blit(maketext(str(math.floor(24 * math.sqrt(x_velocity**2 + y_velocity**2))) + "km/h", color="#CCCCCC", size=35), (740,657))
        if not racestarted:
            racestarttime = pygame.time.get_ticks()
        screen.blit(maketext(f"{int(((pygame.time.get_ticks() - racestarttime) / 8.363 )//7200)}:{str((((pygame.time.get_ticks() - racestarttime) / 8.363)%7200)/120)[:6]}", color="#CCCCCC", size=35), (740,710))

        if (pygame.time.get_ticks() - racestarttime) / 1003.56 < 2 and (pygame.time.get_ticks() - racestarttime) / 1003.56 > 0.1:
            stdblit("start", (0, 0), screen.get_size())

        if not pause:
            pygame.mouse.set_visible(False)
            if not finished:
                if is_solid(car_x, car_y):
                    x_velocity *= 0.87
                    y_velocity *= 0.87
                else:
                    if racetype == "desert":
                        x_velocity *= 0.5
                        y_velocity *= 0.5
                    else:
                        x_velocity *= 0.7
                        y_velocity *= 0.7
                x_velocity = 0 if abs(x_velocity) < 0.05 else x_velocity
                y_velocity = 0 if abs(y_velocity) < 0.05 else y_velocity
                if abs(x_velocity) + abs(y_velocity) > 0 and carengine.get_num_channels() == 0:
                    carengine.play()
                keys = pygame.key.get_pressed()
                if keys[pygame.K_w] or keys[pygame.K_s]:
                    x_velocity += 0.4 * math.cos(math.radians(cardir)) * (keys[pygame.K_w] - keys[pygame.K_s])
                    y_velocity += 0.4 * math.sin(math.radians(cardir)) * (keys[pygame.K_w] - keys[pygame.K_s])
                if keys[pygame.K_a] or keys[pygame.K_d]:
                    turnspeed += 2 * (keys[pygame.K_d] - keys[pygame.K_a])
                cardir += turnspeed
                turnspeed *= 0.7
                cardir = cardir%360 if cardir%360>=0 and cardir%360<180 else cardir%360-360

                car_x += x_velocity
                car_y += y_velocity
                
                if racetype == "sea" and not is_solid(car_x, car_y):
                    while not is_solid(car_x, car_y):
                        car_x -= x_velocity
                        car_y -= y_velocity
                    x_velocity = -3 * sign(x_velocity)
                    y_velocity = -3 * sign(y_velocity)

                stdblit("pausebutton", (screen.get_width() - 80, 0))
            else:
                carengine.stop()
                if finishdelay <= 30:
                    car_x += x_velocity
                    car_y += y_velocity
                    
                    if racetype == "sea" and not is_solid(car_x, car_y):
                        while not is_solid(car_x, car_y):
                            car_x -= x_velocity
                            car_y -= y_velocity
                        x_velocity = -3 * sign(x_velocity)
                        y_velocity = -3 * sign(y_velocity)
                    stdblit(racemedia[racetype]["back"], (0,0), (screen.get_width(), screen.get_height()))
                    carpaint(100)
                    stdblit("view", (0,0), (screen.get_width(), screen.get_height()))
                    finishdelay += 1
                    stdblit("blackscreen", (0, 0), screen.get_size())
                    screen.blit(maketext(f"Time: {int((ticksduration / 8.363 )//7200)}:{str(((ticksduration / 8.363)%7200)/120)[:6]}", (255, 255, 255), 80), (100, 500))
                else:
                    finishdelay = 0
                    menu = "main"
                    pygame.mixer.music.load(os.path.join(os.path.dirname(__file__), "media", "audio", "runners.wav"))
                    pygame.mixer.music.set_volume(0.4)
                    pygame.mixer.music.play(loops=-1)
        else:
            stdblit("resume", (screen.get_width() / 2 - 174, 340))
            stdblit("mainmenu", (screen.get_width() / 2 - 174, 430))

        stdblit("mini" + racemedia[racetype]["map"], (screen.get_width() - 280, screen.get_height() - 280))
        stdblit("carmap", (screen.get_width() - 283 + int(car_x * (280 / 700)), screen.get_height() - 283 + int(car_y * (280 / 700))), (5, 5))

    pygame.display.flip()
    if pygame.key.get_pressed()[pygame.K_F2]:
        pygame.image.save(screen, os.path.join(script_dir, "..", "..", "gallery", datetime.datetime.now().strftime("%Y%m%d_%H%M%S" + str(random.randrange(0,100)) + ".png")))
        pygame.time.wait(150)

    pygame.time.Clock().tick(120)