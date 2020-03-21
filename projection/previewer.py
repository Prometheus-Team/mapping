import pygame as pg
import numpy as np
import OpenGL.GL.shaders
import pyrr
import time
import threading

from PIL import Image

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

class R:
	previewResolution = (1200,1200)
	vertexShaderPath = "shaders/vertex.shader"
	fragmentShaderPath = "shaders/fragment.shader"
	autoRotateRate = 0.1
	defaultPointSize = 1


class ModelPreview(threading.Thread):

	POINTS = 1
	WIREFRAME = 2
	SOLID = 3
	TEXTURED = 4

	def __init__(self):
		threading.Thread.__init__(self)
		self.renderMode = GL_POINTS
		self.vertices = np.array([],dtype=np.float32)
		self.indices = np.array([],dtype=np.int32)
		self.edgeIndices = np.array([],dtype=np.int32)
		self.polyIndices = np.array([],dtype=np.int32)
		self.controller = ModelController(self)
		self.rowlen = 0
		self.shader = None
		self.permaRotation = pyrr.Matrix44.from_x_rotation(0)
		self.tempRotation = pyrr.Matrix44.from_x_rotation(0)
		self.autoRotation = pyrr.Matrix44.from_x_rotation(0)
		self.updateBuffersValue = False
		self.updateAttribsValue = False

	def run(self):
		self.launchPreview()
		self.startRunning()

	def setRenderMode(self, renderMode):
		if (renderMode == ModelPreview.POINTS):
			self.renderMode = GL_POINTS
			self.indices = np.linspace(0, len(self.vertices)/3 - 1, len(self.vertices)/3, dtype=np.int32)
		elif renderMode == ModelPreview.WIREFRAME:
			self.renderMode = GL_LINES
			if self.edgeIndices != None:
				self.indices = self.edgeIndices
		self.setUpdateBuffers()

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

		glClearColor(0.2, 0.2, 0.2, 1.0)
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

	def startRunning(self):
		self.runPreview()


	def runPreview(self):
		while True:
			self.controller.updateController()

			if self.updateBuffersValue:
				self.updateBuffers()
				self.updateBuffersValue = False

			glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

			persp = pyrr.Matrix44.perspective_projection(45, 1, 0.1, 100)
			offset = pyrr.Matrix44.from_translation((0,0,-5)) * pyrr.Matrix44.from_x_rotation(np.pi/-6)# * pyrr.Matrix44.from_y_rotation(np.pi/6)

			transformLoc = glGetUniformLocation(self.shader, "transform")
			self.autoRotation = pyrr.Matrix44.from_y_rotation(R.autoRotateRate * time.time()/3)
			glUniformMatrix4fv(transformLoc, 1, GL_FALSE, persp * offset * self.tempRotation * self.permaRotation)
			glDrawElements(self.renderMode, len(self.indices), GL_UNSIGNED_INT, None)

			pg.display.flip()
			pg.time.wait(10)


	def buildVertices(self, points, color=None, pointSize=None, texCoord=None):
		rowlen = points.shape[0]

		if color == None:
			colors = np.ones((rowlen, 3)).astype(dtype=np.float32)
		elif len(color) == 3:
			colors = np.tile(color, rowlen).reshape((rowlen, 3)).astype(dtype=np.float32)
		else:
			colors = color.astype(dtype=np.float32)

		if pointSize == None:
			pointSizes = np.array(R.defaultPointSize).repeat(rowlen).reshape((rowlen,1)).astype(dtype=np.float32)
		elif type(pointSize) == int:
			pointSizes = np.array(pointSize).repeat(rowlen).reshape((rowlen,1)).astype(dtype=np.float32)
		else:
			pointSizes = pointSize.astype(dtype=np.float32)

		if texCoord == None:
			texCoords = np.zeros((rowlen,2)).astype(dtype=np.float32)
		elif len(texCoord) == 2:
			texCoords = np.tile(texCoord, rowlen).reshape((rowlen, 2)).astype(dtype=np.float32)
		else:
			texCoords = texCoord.astype(dtype=np.float32)

		self.vertices = np.concatenate((points, colors, pointSizes, texCoords), axis=1)
		self.rowlen = self.vertices.shape[1]
		# print(self.vertices.shape)
		self.vertices = self.vertices.reshape((-1,))


	def ShowPolies(self, points, polies, color=None, pointSize=None, texCoord=None):
		self.vertices = np.array(points, dtype=np.float32)
		self.polyIndices = np.array(polies, dtype=np.int32)
		self.edgeIndices = self.polyIndices
		self.indices = self.polyIndices
		self.setRenderMode(ModelPreview.TEXTURED)

	def ShowEdges(self, points, edges, color=None, pointSize=None, texCoord=None):
		self.vertices = np.array(points, dtype=np.float32)
		self.edgeIndices = np.array(edges, dtype=np.int32)
		self.polyIndices = None
		self.indices = self.edgeIndices
		self.setRenderMode(ModelPreview.WIREFRAME)

	def ShowPoints(self, points, color=None, pointSize=None, texCoord=None):
		self.buildVertices(points, color=color, pointSize=pointSize, texCoord=texCoord)
		self.edgeIndices = None
		self.polyIndices = None
		self.setRenderMode(ModelPreview.POINTS)

	def setUpdateBuffers(self):
		self.updateBuffersValue = True



class ModelController:

	def __init__(self, previewer):
		self.previewer = previewer
		self.dragging = False
		self.dragMousePosition = (0,0)
		self.handlers = [(pg.QUIT,(self.Quit,)), 
						(pg.MOUSEBUTTONDOWN, (self.MouseDown,)), 
						(pg.MOUSEBUTTONUP, (self.MouseUp,)), 
						(pg.MOUSEMOTION , (self.MouseMove,)),
						(pg.KEYDOWN, (self.KeyDown,))]

	def updateController(self):
		for event in pg.event.get():
			for handlerPair in self.handlers:
				if event.type == handlerPair[0]:
					for handler in handlerPair[1]:
						handler(event)

	def Quit(self, event):
		pg.quit()
		quit()

	def MouseUp(self, event):
		self.dragging = False
		self.dragMousePosition = (0,0)
		self.previewer.permaRotation = self.previewer.tempRotation * self.previewer.permaRotation
		self.previewer.tempRotation = pyrr.Matrix44.from_x_rotation(0)

	def MouseDown(self, event):
		self.dragging = True
		self.dragMousePosition = pg.mouse.get_pos()

	def MouseMove(self, event):
		if self.dragging:
			mouseOffset = (np.array(self.dragMousePosition) - np.array(pg.mouse.get_pos()))/10
			self.dragMousePosition = pg.mouse.get_pos()
			vector = pyrr.Vector3((mouseOffset[1]/20,mouseOffset[0]/20,0))
			vector = self.previewer.tempRotation * vector
			self.previewer.tempRotation *= pyrr.Matrix44.from_y_rotation(vector.y)
			self.previewer.tempRotation *= pyrr.Matrix44.from_x_rotation(vector.x)

	def KeyDown(self, event):
		if event.key == pg.K_LEFT:
			self.previewer.permaRotation = self.previewer.permaRotation * pyrr.Matrix44.from_y_rotation(-0.2)
		if event.key == pg.K_RIGHT:
			self.previewer.permaRotation = self.previewer.permaRotation * pyrr.Matrix44.from_y_rotation(0.2)
		if event.key == pg.K_UP:
			self.previewer.permaRotation = pyrr.Matrix44.from_x_rotation(-0.2) * self.previewer.permaRotation
		if event.key == pg.K_DOWN:
			self.previewer.permaRotation = pyrr.Matrix44.from_x_rotation(0.2) * self.previewer.permaRotation
		if event.key == pg.K_KP0:
			self.previewer.permaRotation = pyrr.Matrix44.from_x_rotation(0)





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
	t = np.array(np.meshgrid(x,y,z)).T
	return t.reshape(int(t.size/3),3)


if __name__ == '__main__':
	lin = np.linspace(-1,1,10)
	verts = pair3(lin, lin, lin).astype(dtype=np.float32)
	print(verts.shape)
	m = ModelPreview()
	m.start()
	print(verts)
	m.ShowPoints(verts, pointSize=1)
	# m.setRenderMode(ModelPreview.WIREFRAME)
