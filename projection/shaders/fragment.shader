#version 330

in vec3 newColor;
in vec3 fragNormal;
in vec2 OutTexCoords;

out vec4 outColor;
uniform sampler2D samplerTex;

void main() {

	vec3 light = vec3(0,1,0);
	float diffuse = (1 + max(dot(light, fragNormal), 0))/2;
	outColor = vec4(newColor,1) * diffuse;

}
