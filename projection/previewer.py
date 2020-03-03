import pygame as pg
import numpy as np
import OpenGL.GL.shaders
import pyrr
import time
from PIL import Image

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

class R:
	previewResolution = (800,800)
	vertexShaderPath = "shaders/vertex.shader"
	fragmentShaderPath = "shaders/fragment.shader"



class ModelPreview:

	POINTS = 1
	WIREFRAME = 2
	SOLID = 3
	TEXTURED = 4

	def __init__(self):
		self.renderMode = GL_POINTS
		self.vertices = np.array([],dtype=np.float32)
		self.indices = np.array([],dtype=np.int32)
		self.edgeIndices = np.array([],dtype=np.int32)
		self.polyIndices = np.array([],dtype=np.int32)
		self.controller = ModelController(self)
		self.rowlen = 0
		self.shader = None
		self.launchPreview()

	def setRenderMode(self, renderMode):
		if (renderMode == ModelPreview.POINTS):
			self.renderMode = GL_POINTS
			self.indices = np.linspace(0, len(self.vertices)/3 - 1, len(self.vertices)/3, dtype=np.int32)
		elif renderMode == ModelPreview.WIREFRAME:
			self.renderMode = GL_LINES
			self.indices = self.edgeIndices
		self.updateBuffers()

	def getShader(self, path):
		return open(path).read()

	def launchPreview(self):
		pg.init()
		pg.display.set_mode(R.previewResolution, DOUBLEBUF|OPENGL)

		self.shader = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShader(self.getShader(R.vertexShaderPath), GL_VERTEX_SHADER),
		                                          OpenGL.GL.shaders.compileShader(self.getShader(R.fragmentShaderPath), GL_FRAGMENT_SHADER))

		self.updateBuffers()
		self.updateAttributes()

		glUseProgram(self.shader)

		glClearColor(0.0, 0.0, 0.0, 1.0)
		glEnable(GL_DEPTH_TEST)
		glPointSize(1)
		# glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)
		# gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

	def updateBuffers(self):

		VBO = glGenBuffers(1)
		glBindBuffer(GL_ARRAY_BUFFER, VBO)
		glBufferData(GL_ARRAY_BUFFER, self.vertices.itemsize * len(self.vertices), self.vertices, GL_STATIC_DRAW)

		EBO = glGenBuffers(1)
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
		glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.itemsize * len(self.indices), self.indices, GL_STATIC_DRAW)

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


	def updateAttributes(self):
		position = glGetAttribLocation(self.shader, 'position')
		glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, self.vertices.itemsize * self.rowlen, ctypes.c_void_p(0))
		glEnableVertexAttribArray(position)

		# color = glGetAttribLocation(self.shader, 'color')
		# glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, cube.itemsize * 8, ctypes.c_void_p(12))
		# glEnableVertexAttribArray(color)

		# texCoords = glGetAttribLocation(self.shader, "InTexCoords")
		# glVertexAttribPointer(texCoords, 2, GL_FLOAT, GL_FALSE,  cube.itemsize * 8, ctypes.c_void_p(24))
		# glEnableVertexAttribArray(texCoords)

	def runPreview(self):
		dragging = False
		dragMousePosition = (0,0)
		permaRotation = pyrr.Matrix44.from_x_rotation(0)
		tempRotation = pyrr.Matrix44.from_x_rotation(0)

		while True:

			
			glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

			persp = pyrr.Matrix44.perspective_projection(45, 1, 0.1, 100)
			offset = pyrr.Matrix44.from_translation((0,0,-5))
			# rot_x = pyrr.Matrix44.from_x_rotation(0.5 * time.time())
			# rot_y = pyrr.Matrix44.from_y_rotation(0.8 * time.time())

			transformLoc = glGetUniformLocation(self.shader, "transform")
			glUniformMatrix4fv(transformLoc, 1, GL_FALSE, persp * offset * dragRotation * permadrag)
			glDrawElements(GL_POINTS, len(self.indices), GL_UNSIGNED_INT, None)

			pg.display.flip()
			pg.time.wait(10)

	def ShowPolies(self, points, polies):
		self.vertices = np.array(points, dtype=np.float32)
		self.polyIndices = np.array(polies, dtype=np.int32)
		self.edgeIndices = self.polyIndices
		self.indices = self.polyIndices
		self.rowlen = 3
		self.setRenderMode(ModelPreview.TEXTURED)
		self.launchPreview()

	def ShowEdges(self, points, edges):
		self.vertices = np.array(points, dtype=np.float32)
		self.edgeIndices = np.array(edges, dtype=np.int32)
		self.polyIndices = None
		self.rowlen = 3
		self.indices = self.edgeIndices
		self.setRenderMode(ModelPreview.WIREFRAME)
		self.launchPreview()

	def ShowPoints(self, points):
		self.vertices = np.array(points, dtype=np.float32)
		self.rowlen = 3
		self.setRenderMode(ModelPreview.POINTS)
		self.launchPreview()
		self.runPreview()

	def runControl(self):
 		pass


def ModelController:

	def __init__(self, previewer):
		self.previewer = previewer
		self.dragging = False
		self.handlers = [(pg.QUIT,(self.Quit)), (pg.MOUSEBUTTONDOWN, (self.MouseDown)), (pg.MOUSEBUTTONUP, (self.MouseUp)), (pg.MOUSEMOTION , (self.MouseMove))]

	def updateController(self):
		for event in pg.event.get():
			for handlerPair in self.handlers:
				if event == handlerPair[0]:
					for handler in handlerPair[1]:
						handler()

	def Quit(self):
		pg.quit()
		quit()

	def MouseUp(self):
		self.dragging = False
		dragMousePosition = (0,0)
		permadrag = dragRotation * permadrag
		dragRotation = pyrr.Matrix44.from_x_rotation(0)

	def MouseDown(self):
		self.dragging = True
		dragMousePosition = pg.mouse.get_pos()

	def MouseMove(self):
		if self.dragging:
			mouseOffset = (np.array(dragMousePosition) - np.array(pg.mouse.get_pos()))/10
			dragMousePosition = pg.mouse.get_pos()
			vector = pyrr.Vector3((mouseOffset[1]/20,mouseOffset[0]/20,0))
			vector = dragRotation.inverse * vector
			dragRotation *= pyrr.Matrix44.from_y_rotation(vector.y)
			dragRotation *= pyrr.Matrix44.from_x_rotation(vector.x)



# cube = [-0.5, -0.5, 0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
#         0.5, -0.5, 0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
#         0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
#         -0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 0.0, 1.0,

#         -0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
#         0.5, -0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
#         0.5, 0.5, -0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
#         -0.5, 0.5, -0.5, 1.0, 1.0, 1.0, 0.0, 1.0,

#         0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
#         0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
#         0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
#         0.5, -0.5, 0.5, 1.0, 1.0, 1.0, 0.0, 1.0,

#         -0.5, 0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
#         -0.5, -0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
#         -0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
#         -0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 0.0, 1.0,

#         -0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
#         0.5, -0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
#         0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
#         -0.5, -0.5, 0.5, 1.0, 1.0, 1.0, 0.0, 1.0,

#         0.5, 0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
#         -0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
#         -0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
#         0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 0.0, 1.0]

# cube = np.array(cube, dtype=np.float32)

cube = [-0.5, -0.5, 0.5,
        0.5, -0.5, 0.5,
        0.5, 0.5, 0.5,
        -0.5, 0.5, 0.5,

        -0.5, -0.5, -0.5,
        0.5, -0.5, -0.5,
        0.5, 0.5, -0.5,
        -0.5, 0.5, -0.5]

cube = np.array(cube, dtype=np.float32)

# indices = [0, 1, 2, 2, 3, 0,
#            4, 5, 6, 6, 7, 4,
#            8, 9, 10, 10, 11, 8,
#            12, 13, 14, 14, 15, 12,
#            16, 17, 18, 18, 19, 16,
#            20, 21, 22, 22, 23, 20]

# indices = np.array(indices, dtype=np.uint32)


def pair3(x, y, z):
    return np.array(np.meshgrid(x,y,z)).T.reshape((-1,))

lin = np.linspace(-1,1,4)
verts = pair3(lin, lin, lin).astype(dtype=np.float32)
print(verts)
print(verts.shape)
m = ModelPreview()
m.ShowPoints(verts)




