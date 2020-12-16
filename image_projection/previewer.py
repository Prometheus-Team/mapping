
if __name__ == '__main__':

	import os
	import sys

	mainDirectory = os.getcwd()

	sys.path.append(mainDirectory + '\\..\\..')

	os.chdir(mainDirectory + '\\..\\..')

import pygame as pg
import numpy as np
import OpenGL.GL.shaders
import pyrr
import time
import math
import threading

from PIL import Image

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from mapping.image_projection.util import *

class R:
	previewResolution = (800, 800)
	bgColor = (0.2, 0.2, 0.2)
	gridColor = (0.3, 0.3, 0.3)
	gridCount = 21
	gridSize = 10
	axisTipSize = 5
	xColor = (0.8,0,0)
	yColor = (0,0.9,0)
	zColor = (0.2,0.4,1)
	vertexShaderPath = "mapping/image_projection/shaders/vertex.shader"
	fragmentShaderPath = "mapping/image_projection/shaders/fragment.shader"
	autoRotateRate = 0.1
	defaultPointSize = 1

class Renderable:

	POINTS = 1
	WIREFRAME = 2
	SOLID = 3
	TEXTURED = 4

	def __init__(self, points, renderMode, indices=None, color=None, normal=None, pointSize=None, texCoord=None, renderType = None):
		self.data = np.array([],dtype=np.float32)
		self.rowlen = 0
		self.indices = np.array([],dtype=np.int32)

		self.points = np.array([],dtype=np.float32)
		self.color = np.array([],dtype=np.float32)
		self.pointSize = np.array([],dtype=np.float32)
		self.texCoord = np.array([],dtype=np.float32)
		self.normals = np.array([],dtype=np.float32)
		self.renderMode = renderMode
		self.renderType = renderType

		self.currentPreviewer = None
		self.indiceStart = 0
		self.dataStart = 0
		self.buildVertices(points, indices, color, normal, pointSize, texCoord)

	def getRange(self):
		return ctypes.c_void_p(self.indiceStart * 4), self.indices.shape[0]

	def getRenderType(self):
		if self.renderType != None:
			return self.renderType
		elif self.renderMode == Renderable.POINTS:
			return GL_POINTS
		elif self.renderMode == Renderable.WIREFRAME:
			return GL_LINES
		elif self.renderMode == Renderable.SOLID:
			return GL_TRIANGLES
		else:
			return GL_POINTS

	def getPointsArray(self, points):
		return points.reshape((-1,3)).astype(dtype=np.float32)

	def getColorArray(self, color, rowAmount):
		if type(color) == type(None):
			colors = np.ones((rowAmount, 3)).astype(dtype=np.float32)
		elif len(color) == 3:
			colors = np.tile(color, rowAmount).reshape((rowAmount, 3)).astype(dtype=np.float32)
		else:
			colors = np.array(color, dtype=np.float32).reshape((rowAmount, 3))

		return colors

	def getPointSizeArray(self, pointSize, rowAmount):
		if type(pointSize) == type(None):
			pointSizes = np.array(R.defaultPointSize).repeat(rowAmount).reshape((rowAmount,1)).astype(dtype=np.float32)
		elif type(pointSize) == int:
			pointSizes = np.array(pointSize).repeat(rowAmount).reshape((rowAmount,1)).astype(dtype=np.float32)
		else:
			pointSizes = np.array(pointSize, dtype=np.float32).reshape((rowAmount, 1))

		return pointSizes

	def getTexCoordArray(self, texCoord, rowAmount):

		if type(texCoord) == type(None):
			texCoords = np.zeros((rowAmount,2)).astype(dtype=np.float32)
		elif len(texCoord) == 2:
			texCoords = np.tile(texCoord, rowAmount).reshape((rowAmount, 2)).astype(dtype=np.float32)
		else:
			texCoords = np.array(texCoord, dtype=np.float32).reshape((rowAmount, 2))

		return texCoords		

	def getNormalArray(self, normal, rowAmount):
		if normal is None:
			normals = np.tile(np.array(((0,1,0),)), rowAmount).reshape((rowAmount, 3)).astype(dtype=np.float32)
		elif len(normal) == 3:
			normals = np.tile(normal, rowAmount).reshape((rowAmount, 3)).astype(dtype=np.float32)
		else:
			normals = np.array(normal, dtype=np.float32).reshape((rowAmount, 3))

		return normals



	def buildVertices(self, points, indices=None, color=None, normal=None, pointSize=None, texCoord=None):
		points = self.getPointsArray(points)
		rowAmount = points.shape[0]

		colors = self.getColorArray(color, rowAmount)
		pointSizes = self.getPointSizeArray(pointSize, rowAmount)
		texCoords = self.getTexCoordArray(texCoord, rowAmount)
		normals = self.getNormalArray(normal, rowAmount)

		self.data = np.concatenate((points, colors, texCoords, pointSizes, normals), axis=1)
		self.rowlen = self.data.shape[1]
		self.indices = indices
		if type(self.indices) == type(None):
			self.indices = np.linspace(0, self.data.shape[0] - 1, self.data.shape[0], dtype=np.int32)
		self.indices = self.indices.reshape((-1,)).astype(dtype=np.int32)
		
		if len(self.indices) % 2 != 0:
			self.indices = np.append(self.indices, self.indices[-1])

	def updateColors(self, color):
		colors = self.getColorArray(color, rowAmount)
		self.data[:, 3:6] = colors

		if currentPreviewer != None:
			currentPreviewer.setUpdateBuffers()

	def updatePoints(self, points):
		points = self.getPointsArray(points)
		self.data[:, 0:3] = points

		if currentPreviewer != None:
			currentPreviewer.setUpdateBuffers()




class Camera:

	def __init__(self, hfovd, vfovd, matrix = None):
		self.focal = 1
		self.x = math.tan(math.radians(hfovd/2)) * self.focal
		self.y = math.tan(math.radians(vfovd/2)) * self.focal
		self.matrix = matrix
		self.renderable = None
		self.previewer = None
		self.buildCamera()

	def buildCamera(self):
		verts = np.array([[0,0,0],[self.focal,self.y,self.x],[self.focal,self.y,-self.x],[self.focal,-self.y,-self.x],[self.focal,-self.y,self.x]], dtype=np.float32)/2
		inds = np.array([0,1,2,0,2,3,0,3,4,0,4,1,0], dtype=np.int32)

		if self.matrix is not None:
			verts = transform(verts, self.matrix)

		if self.previewer is not None:
			self.previewer.removeRenderable(self.renderable)

		self.renderable = Renderable(verts, Renderable.WIREFRAME, indices=inds, renderType=GL_LINE_STRIP, color=(0.8, 0.6, 0.3))

		if self.previewer is not None:
			self.previewer.addRenderable(self.renderable)


	def transform(self, matrix):
		self.matrix = matrix
		self.buildCamera()

class RenderUtil:

	def getBounds(points):
		minBound, maxBound = bounds(points)
		print("Min and max", minBound, maxBound)
		boundPointsMask = pair3((0,1),(0,1),(0,1))
		boundPoints = np.where(boundPointsMask == 0, minBound, maxBound)

		indices = []
		for i in range(boundPointsMask.shape[0]):
			for j in range(i):
				if np.sum(np.abs(boundPointsMask[i] - boundPointsMask[j])) == 1:
					indices.append((i,j))
		indices = np.array(indices, dtype=np.int32)

		return boundPoints, indices


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
		self.offset = pyrr.Matrix44.from_translation((0,0,-5))# * pyrr.Matrix44.from_x_rotation(np.pi/-6)# * pyrr.Matrix44.from_y_rotation(np.pi/6)
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

	def addRenderables(self, renderables):
		for i in renderables:
			self.addRenderable(i)

	def addRenderable(self, renderable):
		self.renderables.append(renderable)
		renderable.currentPreviewer = self
		self.setUpdateBuffers()


	def removeRenderable(self, renderable):
		self.renderables.remove(renderable)
		self.setUpdateBuffers()
		
	def addDefaultRenderables(self):
		self.addAxesTips()
		self.addAxes()
		self.addGrid()

	def addGrid(self):
		vlin = np.linspace(-1,1,R.gridCount)
		hlin = np.array([-1, 1], dtype=np.float32)
		vy = pair3(hlin, vlin, np.zeros(1)).astype(dtype=np.float32)
		vx = vy.copy()
		vx[:,2] = vy[:,0]
		vx[:,0] = vy[:,2]
		verts = np.concatenate((vx,vy)) * R.gridSize

		self.addRenderable(Renderable(verts, Renderable.WIREFRAME, pointSize=4, color=R.gridColor))

	def addCamera(self, camera):
		camera.previewer = self
		self.addRenderable(camera.renderable)

	def addAxes(self):
		length = R.gridSize;
		verts = np.array([[0,0,-length],[0,0,length],[length,0,0],[-length,0,0]], dtype=np.float32)
		col = np.array([R.zColor,R.zColor,R.xColor,R.xColor], dtype=np.float32)

		self.addRenderable(Renderable(verts, Renderable.WIREFRAME, color=col))

	def addAxesTips(self):
		length = R.gridSize;
		verts = np.array([[0,0,length],[length,0,0]], dtype=np.float32)
		col = np.array([R.zColor,R.xColor], dtype=np.float32)

		self.addRenderable(Renderable(verts, Renderable.POINTS, pointSize=R.axisTipSize,color=col))


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
			dataStart = self.data.shape[0]
			self.data = np.concatenate((self.data, i.data))
			indiceStart = self.indices.shape[0]
			self.indices = np.concatenate((self.indices, i.indices + dataStart))
			i.indiceStart = indiceStart
			i.dataStart = dataStart

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
		glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, self.data.itemsize * self.rowlen, ctypes.c_void_p(12))
		glEnableVertexAttribArray(color)

		normal = glGetAttribLocation(self.shader, 'normal')
		glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, self.data.itemsize * self.rowlen, ctypes.c_void_p(36))
		glEnableVertexAttribArray(normal)

		# texCoords = glGetAttribLocation(self.shader, "InTexCoords")
		# glVertexAttribPointer(texCoords, 2, GL_FLOAT, GL_FALSE,  self.data.itemsize * 8, ctypes.c_void_p(24))
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

			transformLoc = glGetUniformLocation(self.shader, "transform")
			self.autoRotation = pyrr.Matrix44.from_y_rotation(R.autoRotateRate * time.time()/3)
			glUniformMatrix4fv(transformLoc, 1, GL_FALSE, persp * self.offset * self.tempRotation * self.permaRotation)
			
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

		if (event.button == 4):
			self.previewer.offset = pyrr.Matrix44.from_translation((0,0,1)) * self.previewer.offset
		elif (event.button == 5):
			self.previewer.offset = pyrr.Matrix44.from_translation((0,0,-1)) * self.previewer.offset		

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
		if event.key == pg.K_KP_MINUS:
			self.previewer.offset = pyrr.Matrix44.from_translation((0,0,-3)) * self.previewer.offset
		if event.key == pg.K_KP_PLUS:
			self.previewer.offset = pyrr.Matrix44.from_translation((0,0,3)) * self.previewer.offset


if __name__ == '__main__':
	verts = (box(32, 96, 64) * np.array((1,3,2))) - np.array((0, -2, 1))
	m = ModelPreview()
	m.start()
	m.addRenderable(Renderable(verts, Renderable.POINTS, pointSize=1, color=(verts + 1)/2))
	# m.setRenderMode(ModelPreview.WIREFRAME)
