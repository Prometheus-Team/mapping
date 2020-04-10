#version 330

in vec3 position;
in vec3 color;
in vec2 InTexCoords;
in vec3 normal;
in float pointSize;

out vec3 newColor;
out vec2 OutTexCoords;
out vec3 fragNormal;

uniform mat4 transform; 

void main() {

	gl_Position = transform * vec4(position, 1.0f);
	newColor = color;
	fragNormal = normal;
	OutTexCoords = InTexCoords;
	gl_PointSize = pointSize;

}

