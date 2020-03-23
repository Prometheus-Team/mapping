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
	previewResolution = (1000,1000)
	bgColor = (0.2, 0.2, 0.2)
	gridColor = (0.3, 0.3, 0.3)
	gridCount = 40
	gridSize = 10
	vertexShaderPath = "shaders/vertex.shader"
	fragmentShaderPath = "shaders/fragment.shader"
	autoRotateRate = 0.1
	defaultPointSize = 1

class Renderable:

	POINTS = 1
	WIREFRAME = 2
	SOLID = 3
	TEXTURED = 4

	def __init__(self, points, renderMode, indices=None, color=None, pointSize=None, texCoord=None, renderType = None):
		self.data = np.array([],dtype=np.float32)
		self.rowlen = 0
		self.indices = np.array([],dtype=np.int32)

		self.points = np.array([],dtype=np.float32)
		self.color = np.array([],dtype=np.float32)
		self.pointSize = np.array([],dtype=np.float32)
		self.texCoord = np.array([],dtype=np.float32)
		self.renderMode = renderMode
		self.renderType = renderType

		self.indiceStart = 0
		self.buildVertices(points, indices, color, pointSize, texCoord)

	def getRange(self):
		return ctypes.c_void_p(self.indiceStart * 4), self.indices.shape[0]

	def getRenderType(self):
		if self.renderType != None:
			return self.renderType
		elif self.renderMode == Renderable.POINTS:
			return GL_POINTS
		elif self.renderMode == Renderable.WIREFRAME:
			return GL_LINES
		else:
			return GL_POINTS


	def buildVertices(self, points, indices=None, color=None, pointSize=None, texCoord=None):
		rowAmount = points.shape[0]

		if color == None:
			colors = np.ones((rowAmount, 3)).astype(dtype=np.float32)
		elif len(color) == 3:
			colors = np.tile(color, rowAmount).reshape((rowAmount, 3)).astype(dtype=np.float32)
		else:
			colors = np.array(color, dtype=np.float32)

		if pointSize == None:
			pointSizes = np.array(R.defaultPointSize).repeat(rowAmount).reshape((rowAmount,1)).astype(dtype=np.float32)
		elif type(pointSize) == int:
			pointSizes = np.array(pointSize).repeat(rowAmount).reshape((rowAmount,1)).astype(dtype=np.float32)
		else:
			pointSizes = np.array(pointSize, dtype=np.float32)

		if texCoord == None:
			texCoords = np.zeros((rowAmount,2)).astype(dtype=np.float32)
		elif len(texCoord) == 2:
			texCoords = np.tile(texCoord, rowAmount).reshape((rowAmount, 2)).astype(dtype=np.float32)
		else:
			texCoords = np.array(texCoord, dtype=np.float32)

		self.data = np.concatenate((points, colors, texCoords, pointSizes), axis=1)
		self.rowlen = self.data.shape[1]
		self.indices = indices
		if self.indices == None:
			self.indices = np.linspace(0, self.data.shape[0] - 1, self.data.shape[0], dtype=np.int32)






class ModelPreview(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.data = np.array([],dtype=np.float32)
		self.indices = np.array([],dtype=np.int32)
		self.controller = ModelController(self)
		self.rowlen = 0
		self.shader = None
		self.permaRotation = pyrr.Matrix44.from_x_rotation(0)
		self.tempRotation = pyrr.Matrix44.from_x_rotation(0)
		self.autoRotation = pyrr.Matrix44.from_x_rotation(0)
		self.updateBuffersValue = False
		self.updateAttribsValue = False

		self.renderables = []
		self.clear()

	def run(self):
		self.launchPreview()
		self.startRunning()

	def clear(self):
		self.renderables = []
		self.addDefaultRenderables()
		self.setUpdateBuffers()

	def addRenderable(self, renderable):
		self.renderables.append(renderable)
		self.setUpdateBuffers()
		
	def addDefaultRenderables(self):
		self.addGrid()

	def addGrid(self):
		vlin = np.linspace(-1,1,R.gridCount)
		hlin = np.array([-1, 1], dtype=np.float32)
		vy = pair3(hlin, np.zeros(1), vlin).astype(dtype=np.float32)
		vx = vy.copy()
		vx[:,2] = vy[:,0]
		vx[:,0] = vy[:,2]
		verts = np.concatenate((vx,vy)) * R.gridSize

		self.addRenderable(Renderable(verts, Renderable.WIREFRAME, pointSize=4, color=R.gridColor))


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

		glClearColor(R.bgColor[0], R.bgColor[1], R.bgColor[2], 1.0)
		glEnable(GL_DEPTH_TEST)
		# glPointSize(1)
		glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)
		# gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

	def buildData(self):

		if len(self.renderables) == 0:
			return

		self.data = self.renderables[0].data
		self.indices = self.renderables[0].indices

		for i in self.renderables[1:]:
			self.data = np.concatenate((self.data, i.data))
			indiceStart = self.indices.shape[0]
			self.indices = np.concatenate((self.indices, i.indices + indiceStart))
			i.indiceStart = indiceStart

		self.rowlen = self.data.shape[1]
		self.data = self.data.reshape((-1,))

	def updateBuffers(self):

		self.buildData()

		VBO = glGenBuffers(1)
		glBindBuffer(GL_ARRAY_BUFFER, VBO)
		glBufferData(GL_ARRAY_BUFFER, self.data.itemsize * len(self.data), self.data, GL_STATIC_DRAW)

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
		print("Attrib", self.rowlen)
		glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, self.data.itemsize * self.rowlen, ctypes.c_void_p(0))
		glEnableVertexAttribArray(position)

		color = glGetAttribLocation(self.shader, 'color')
		glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, cube.itemsize * self.rowlen, ctypes.c_void_p(12))
		glEnableVertexAttribArray(color)

		# texCoords = glGetAttribLocation(self.shader, "InTexCoords")
		# glVertexAttribPointer(texCoords, 2, GL_FLOAT, GL_FALSE,  cube.itemsize * 8, ctypes.c_void_p(24))
		# glEnableVertexAttribArray(texCoords)

		pointSize = glGetAttribLocation(self.shader, 'pointSize')
		glVertexAttribPointer(pointSize, 1, GL_FLOAT, GL_FALSE, self.data.itemsize * self.rowlen, ctypes.c_void_p(32))
		glEnableVertexAttribArray(pointSize)

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
			offset = pyrr.Matrix44.from_translation((0,0,-5))# * pyrr.Matrix44.from_x_rotation(np.pi/-6)# * pyrr.Matrix44.from_y_rotation(np.pi/6)

			transformLoc = glGetUniformLocation(self.shader, "transform")
			self.autoRotation = pyrr.Matrix44.from_y_rotation(R.autoRotateRate * time.time()/3)
			glUniformMatrix4fv(transformLoc, 1, GL_FALSE, persp * offset * self.tempRotation * self.permaRotation)
			
			for i in self.renderables:
				start, count = i.getRange()
				glDrawElements(i.getRenderType(), count, GL_UNSIGNED_INT, start)

			pg.display.flip()
			pg.time.wait(10)


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

def pair(x, y):
    return np.array(np.meshgrid(x,y)).T.reshape((-1,2))

def pair3(x, y, z):
	t = np.array(np.meshgrid(x,y,z)).T
	return t.reshape(int(t.size/3),3)


if __name__ == '__main__':
	lin = np.linspace(-1,1,10)
	verts = pair3(lin, lin, lin).astype(dtype=np.float32)
	print(verts.shape)
	m = ModelPreview()
	m.start()
	m.addRenderable(Renderable(verts, Renderable.POINTS, pointSize=4))
	# m.setRenderMode(ModelPreview.WIREFRAME)
