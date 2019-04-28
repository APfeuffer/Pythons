#version 330

layout (location=0) in vec3 position;
layout (location=1) in vec3 normal;
layout (location=2) in vec2 tex_coords;

out vec4 norm;
out vec2 texc;
out vec4 eye;

void main() {
    eye = vec4(position, 1);
    gl_Position = eye;
    norm = vec4(normal, 0);
    texc = tex_coords;
}
