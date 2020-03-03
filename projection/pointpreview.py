import pygame as pg
from pygame.locals import *
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *

cubeVertices = ((1,1,1),(1,1,-1),(1,-1,-1),(1,-1,1),(-1,1,1),(-1,-1,-1),(-1,-1,1),(-1,1,-1))
cubeEdges = ((0,1),(0,3),(0,4),(1,2),(1,7),(2,5),(2,3),(3,6),(4,6),(4,7),(5,6),(5,7))
cubeQuads = ((0,3,6,4),(2,5,6,3),(1,2,5,7),(1,0,4,7),(7,4,6,5),(2,3,0,1))


def pair(x, y):
    return np.array(np.meshgrid(x,y)).T.reshape((-1,2))

def pair3(x, y, z):
    return np.array(np.meshgrid(x,y,z)).T.reshape((-1,3))

lin = np.linspace(-1,1,20)
verts = pair3(lin, lin, lin)

def wireCube():
    glBegin(GL_LINES)
    for cubeEdge in cubeEdges:
        for cubeVertex in cubeEdge:
            glVertex3fv(cubeVertices[cubeVertex])
    glEnd()

def solidCube():
    glPointSize(5)
    glBegin(GL_POINTS)
    for cubeQuad in cubeQuads:
        for cubeVertex in cubeQuad:
            glVertex3fv(cubeVertices[cubeVertex])
    glEnd()


def pointDraw():
    glPointSize(1)
    glBegin(GL_POINTS)
    for i in verts:
        glVertex3fv(i)
    glEnd()


def main():
    pg.init()
    display = (1680, 1050)
    pg.display.set_mode(display, DOUBLEBUF|OPENGL)
    dragMousePosition = (0,0)
    dragging = False

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

    glTranslatef(0.0, 0.0, -5)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            if event.type == pg.MOUSEBUTTONDOWN:
                dragging = True
                dragMousePosition = pg.mouse.get_pos()
            if event.type == pg.MOUSEBUTTONUP:
                dragging = False
                dragMousePosition = (0,0)
            if event.type == pg.MOUSEMOTION:
                if dragging:
                    offset = (np.array(dragMousePosition) - np.array(pg.mouse.get_pos()))/10
                    dragMousePosition = pg.mouse.get_pos()
                    glRotatef(-1, offset[1], offset[0], 0)



        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        pointDraw()
        # solidCube()
        #wireCube()
        pg.display.flip()
        pg.time.wait(10)

if __name__ == "__main__":
    main()