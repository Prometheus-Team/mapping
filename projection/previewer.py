import pygame as pg
import numpy as np
import OpenGL.GL.shaders
import pyrr
import time
from PIL import Image

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

vertexShaderPath = "shaders/vertex.shader"
fragmentShaderPath = "shaders/fragment.shader"


def getShader(path):
	return open(path).read()

class PointPreview:

	def launchPreview():


	def Show(self, points, edges, polies):
		


pg.init()
display = (500,500)
pg.display.set_mode(display, DOUBLEBUF|OPENGL)

cube = [-0.5, -0.5, 0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
        0.5, -0.5, 0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
        0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
        -0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 0.0, 1.0,

        -0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
        0.5, -0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
        0.5, 0.5, -0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
        -0.5, 0.5, -0.5, 1.0, 1.0, 1.0, 0.0, 1.0,

        0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
        0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
        0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
        0.5, -0.5, 0.5, 1.0, 1.0, 1.0, 0.0, 1.0,

        -0.5, 0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
        -0.5, -0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
        -0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
        -0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 0.0, 1.0,

        -0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
        0.5, -0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
        0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
        -0.5, -0.5, 0.5, 1.0, 1.0, 1.0, 0.0, 1.0,

        0.5, 0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
        -0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
        -0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
        0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 0.0, 1.0]



# convert to 32bit float

cube = np.array(cube, dtype=np.float32)

indices = [0, 1, 2, 2, 3, 0,
           4, 5, 6, 6, 7, 4,
           8, 9, 10, 10, 11, 8,
           12, 13, 14, 14, 15, 12,
           16, 17, 18, 18, 19, 16,
           20, 21, 22, 22, 23, 20]

indices = np.array(indices, dtype=np.uint32)


VERTEX_SHADER = getShader(vertexShaderPath)

FRAGMENT_SHADER = getShader(fragmentShaderPath)


# Compile The Program and shaders

shader = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
                                          OpenGL.GL.shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER))

# Create Buffer object in gpu
VBO = glGenBuffers(1)
# Bind the buffer
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, cube.itemsize * len(cube), cube, GL_STATIC_DRAW)

# Create EBO
EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.itemsize * len(indices), indices, GL_STATIC_DRAW)


# get the position from  shader
position = glGetAttribLocation(shader, 'position')
print(position)
glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, cube.itemsize * 8, ctypes.c_void_p(0))
glEnableVertexAttribArray(position)

# get the color from  shader
color = glGetAttribLocation(shader, 'color')
print(color)
glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, cube.itemsize * 8, ctypes.c_void_p(12))
glEnableVertexAttribArray(color)


# texCoords = glGetAttribLocation(shader, "InTexCoords")
# print(texCoords)
# glVertexAttribPointer(texCoords, 2, GL_FLOAT, GL_FALSE,  cube.itemsize * 8, ctypes.c_void_p(24))
# glEnableVertexAttribArray(texCoords)


# #Texture Creation
# texture = glGenTextures(1)
# glBindTexture(GL_TEXTURE_2D, texture)
# # Set the texture wrapping parameters
# glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
# glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
# # Set texture filtering parameters
# glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
# glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
# # load image
# image = Image.open("fire.jpg")
# img_data = np.array(list(image.getdata()), np.uint8)
# glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
# glEnable(GL_TEXTURE_2D)

glUseProgram(shader)

glClearColor(0.0, 0.0, 0.0, 1.0)
glEnable(GL_DEPTH_TEST)
glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)
# gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)


while True:
	for event in pg.event.get():
		if event.type == pg.QUIT:
			pg.quit()
			quit()
	
	glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

	persp = pyrr.Matrix44.perspective_projection(45, 1, 0.1, 100)
	offset = pyrr.Matrix44.from_translation((0,0,-5))
	rot_x = pyrr.Matrix44.from_x_rotation(0.5 * time.time())
	rot_y = pyrr.Matrix44.from_y_rotation(0.8 * time.time())

	transformLoc = glGetUniformLocation(shader, "transform")
	glUniformMatrix4fv(transformLoc, 1, GL_FALSE, persp * offset * rot_x * rot_y)

	# Draw Cube

	glDrawElements(GL_POINTS, 36, GL_UNSIGNED_INT, None)

	pg.display.flip()
	pg.time.wait(10)