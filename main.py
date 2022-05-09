import sys
from pygame.constants import *
from OpenGL.GLU import *
from objLoader import *
from cvzone.HandTrackingModule import HandDetector
import mediapipe as mp
import time
from numba import jit, cuda
from timeit import default_timer as timer

width, height = 1200, 800
cap = cv2.VideoCapture(0)


rx, ry = (0,0)
tx, ty = (0,0)
zpos = 5
rotate = move = False
moveHandsX, moveHandsY = 0, 0
rotateHandsX, rotateHandsY = 0, 0
startDist = None
beforeX, beforeY = None, None

pygame.init()
pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
pygame.display.set_caption('Hand tracking')

box = OBJ('monkey.obj', )  # from OBJFileLoader import OBJ
im_loader = ImageLoader(0, 0)
#angle = 0

glLightfv(GL_LIGHT0, GL_POSITION, 1.0, 1.0, 1.0, 1.0) #(-40, 200, 100, 0.0)
glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0)) #
glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0)) #(0.5, 0.5, 0.5, 1.0)
glEnable(GL_LIGHT0)
glEnable(GL_LIGHTING)
glEnable(GL_COLOR_MATERIAL)
#glEnable(GL_DEPTH_TEST)
#glShadeModel(GL_SMOOTH)
glClearColor(0.7, 0, 0, 1)

detector = HandDetector(detectionCon=0.7, maxHands=2)
mpDraw = mp.solutions.drawing_utils
pTime = 0
cTime = 0

run = True
while run:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run = False
        elif e.type == KEYDOWN and e.key == K_ESCAPE:
            sys.exit()
        elif e.type == MOUSEBUTTONDOWN:
            if e.button == 4: #scroll up
                zpos = max(1, zpos - 1)
            elif e.button == 5: #scrol down
                zpos += 1
            elif e.button == 1: #left click
                rotate = True
            elif e.button == 3: #right click
                move = True
        elif e.type == MOUSEBUTTONUP:
            if e.button == 1:
                rotate = False
            elif e.button == 3:
                move = False
        elif e.type == MOUSEMOTION:
            i, j = e.rel
            print(i, j)
            if rotate:
                rx += i
                ry += j
            if move:
                tx += i
                ty -= j

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, width, height, 0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)

    success, img = cap.read()
    img = cv2.resize(img, (width, height))
    hands, img = detector.findHands(img)
    if len(hands) == 1:

        if detector.fingersUp(hands[0]) == [0, 1, 1, 0, 0]:
            lmList1 = hands[0]["lmList"]
            length, info, img = detector.findDistance(lmList1[8], lmList1[12], img)
            #print(length)
            i, j = 0, 0
            if moveHandsX or moveHandsY:
                i, j = lmList1[8][0], lmList1[8][1]

            if length < 60:
                if move == 0:
                    move = 1
                elif move:
                    if i or j:
                        resultX = moveHandsX - i
                        print(resultX)
                        resultY = moveHandsY - j
                        print(resultY)
                        tx += resultX
                        ty += resultY

            elif length >= 60 and move == 1:
                move = False
                moveHandsX, moveHandsY = 0, 0
                print("released")

            moveHandsX, moveHandsY = lmList1[8][0], lmList1[8][1]
            print(moveHandsX, moveHandsY)

        elif detector.fingersUp(hands[0]) == [0, 1, 1, 1, 1]:
            lmList1 = hands[0]["lmList"]
            length, info, img = detector.findDistance(lmList1[8], lmList1[12], img)

            i, j = 0, 0
            if rotateHandsX or rotateHandsY:
                i, j = lmList1[8][0], lmList1[8][1]

            if length < 60:
                if rotate == 0:
                    rotate = 1
                elif rotate:
                    if j or i:
                        resultX = rotateHandsX - i
                        resultY = rotateHandsY - j
                        if beforeX == None:
                            beforeX, beforeY = resultX, resultY
                            print(resultX, resultY)
                            rx += resultX
                            ry -= resultY
                        elif (((resultX - beforeX) > 15) or ((resultX - beforeX) > -15)) or (((resultY - beforeY) > 15) or ((resultY - beforeY) > -15)):
                            print(resultX, resultY)
                            rx += resultX
                            ry -= resultY

            elif length >= 60 and rotate == 1:
                rotate = False
                rotateHandsX, rotateHandsY = 0, 0
                beforeX, beforeY = None, None

            rotateHandsX, rotateHandsY = lmList1[8][0], lmList1[8][1]


    elif len(hands) == 2:
        if detector.fingersUp(hands[0]) == [1, 1, 0, 0, 0] and detector.fingersUp(hands[1]) == [1, 1, 0, 0, 0]:
            lmList1 = hands[0]["lmList"]
            lmList2 = hands[1]["lmList"]
            if startDist:
                length, info, img = detector.findDistance(lmList1[8], lmList2[8], img)

                if startDist < length and ((length - startDist) > 15):
                    zpos = max(0.5, zpos - 0.5)
                elif startDist > length and ((startDist - length ) > 15):
                    zpos += 0.5

            length, info, img = detector.findDistance(lmList1[8], lmList2[8], img)
            startDist = length

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    im_loader.load(img)
    glColor3f(1, 1, 1)
    im_loader.draw()

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, (width / height), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslate(tx / 100., ty / 100., - zpos)
    glRotate(ry, 1, 0, 0)
    glRotate(rx, 0, 1, 0)

    glEnable(GL_DEPTH_TEST)
    box.render()

    pygame.display.flip()

pygame.quit()
