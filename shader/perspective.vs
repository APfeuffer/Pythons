#version 330

layout (location=0) in vec3 position;
layout (location=1) in vec3 normal;
layout (location=2) in vec2 tex_coords;

uniform mat4 mvp;
uniform mat4 mv;

out vec4 norm;
out vec2 texc;
out vec4 eye;

void main() {
    vec4 pos = vec4(position, 1);
    norm = mv * vec4(normal, 0);
    texc = tex_coords;
    eye = mv * pos;
    gl_Position = mvp * pos;
}
