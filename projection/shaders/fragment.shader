#version 330

in vec3 newColor;
in vec2 OutTexCoords;

out vec4 outColor;
uniform sampler2D samplerTex;

void main() {

	outColor = vec4(0.9,0.9,0.9,1);

}
