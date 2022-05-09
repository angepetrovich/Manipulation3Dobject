import sys
from pygame.constants import *
from OpenGL.GLU import *
from objLoader import *
from cvzone.HandTrackingModule import HandDetector
import mediapipe as mp
import time
import glm
import numpy
import pyrr

width, height = 1200, 800


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

box = OBJ('untitled.obj', )  # from OBJFileLoader import OBJ

glLightfv(GL_LIGHT0, GL_POSITION, 1.0, 1.0, 1.0, 1.0) #(-40, 200, 100, 0.0)
glLightfv(GL_LIGHT0, GL_POSITION, 1.0, 1.0, 1.0, 1.0)
glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0)) #
glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0)) #(0.5, 0.5, 0.5, 1.0)
glEnable(GL_LIGHT0)
glEnable(GL_LIGHTING)
glEnable(GL_COLOR_MATERIAL)


glMatrixMode(GL_PROJECTION)
gluPerspective(60, (width/ height), 0.01, 15)

glMatrixMode(GL_MODELVIEW)
modelMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
rMat = pyrr.matrix44.create_identity(dtype=np.float32)
tMat = pyrr.matrix44.create_identity(dtype=np.float32)

model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
modelMatrix = pyrr.matrix44.create_identity(dtype=np.float32)

run = True
while run:

    glPushMatrix()
    glLoadIdentity()

    view_matrix = pyrr.matrix44.create_identity(dtype=np.float32)

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
            #print(i, j)
            if rotate:
                rx += i
                ry += j
                rMat = pyrr.matrix44.create_identity(dtype=np.float32)
                x1, y1 = pygame.mouse.get_pos()
                #print(x1, y1)

                rMat = mul(rMat, rotationMat(x1, 0, 1, 0))
                #print(rMat)
                rMat = mul(rMat, rotationMat(y1, 1, 0, 0))
                model_transform = pyrr.matrix44.multiply(model_transform, rMat)
                #modelMatrix = mul(pyrr.matrix44.create_identity(dtype=np.float32), rMat)
                #print(rMat)
            if move:

                tx += i
                ty -= j


    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # glMatrixMode(GL_PROJECTION)
    #glLoadIdentity()
    #gluOrtho2D(0, width, height, 0)
    #glDisable(GL_DEPTH_TEST)



    #glMultMatrixf(modelMatrix)
    #modelMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
    #print(modelMatrix)
    #glLoadIdentity()
    #glTranslate(tx / 100., ty / 100., - zpos)
    #glRotate(ry, 1, 0, 0)
    #glRotate(rx, 0, 1, 0)
    #glMultMatrixf(modelMatrix)

    #modelMatrix = mul(pyrr.matrix44.create_identity(dtype=np.float32), tMat)
    #modelMatrix = mul(modelMatrix , rMat)


    model_transform = pyrr.matrix44.multiply(model_transform, pyrr.matrix44.create_from_translation(
                    vec=np.array(box.position), dtype=np.float32
                ))

    #glLoadIdentity()
    #glTranslatef(0,0, -5)
    #glMultMatrixf(modelMatrix)
    #modelMatrix = mul(modelMatrix, view_matrix)
    #modelMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
    #glLoadMatrixf(modelMatrix)
    #glLoadIdentity()
    #glTranslatef(0, 0, -5)
    modelMatrix = pyrr.matrix44.multiply(modelMatrix, model_transform)
    glMultMatrixf(modelMatrix)
    #modelMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
    glEnable(GL_DEPTH_TEST)
    box.render()

    glPopMatrix()
    pygame.display.flip()
pygame.quit()
