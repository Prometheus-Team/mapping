from mapping.image_projection.normalestimator import NormalEstimator

import numpy as np

class OBJExporter:

	extension = '.obj'

	def exportModel(mesh, name):
		OBJExporter.export(mesh[0], mesh[1], mesh[2], name)

	def export(vertices, faces, normals, name):
		normals = NormalEstimator.getFaceNormals(vertices, faces);

		print("Verts:", len(vertices))
		print("Faces:", len(faces))
		print("Normals:", len(normals))

		text = OBJExporter.getExportContent(vertices, faces, normals, name)
		if not name.endswith(OBJExporter.extension):
			name += OBJExporter.extension
		file = open(name, 'w')
		file.write(text)
		file.close()


	def getExportContent(vertices, faces, normals, name):
		text = ""
		text += "\no " + name

		print(vertices)

		for v in vertices:
			text += "\nv %.4f %.4f %.4f" % (v[0], v[1], v[2])

		for n in normals:
			text += "\nvn %.4f %.4f %.4f" % (n[0], n[1], n[2])

		text += "\ns off"

		for i in range(len(faces)):
			j = i + 1
			text += "\nf %.d//%.d %.d//%.d %.d//%.d" % (faces[i][0] + 1, j, faces[i][1] + 1, j, faces[i][2] + 1, j)

		return text


if __name__ == '__main__':

	OBJExporter.export(np.array([(1,2,3),(3,1,1),(4,4,2)]), np.array([(0,1,2)]), np.array([(1,0,0)]), "Igno")

