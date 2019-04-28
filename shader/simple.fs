#version 330

in vec4 norm;
in vec2 texc;
in vec4 eye;

uniform sampler2D tex_sampler;
uniform vec4 light_direction = vec4(0,0,1,0);
uniform vec4 light_color = vec4(1,1,1,1);
uniform vec4 ambient_color = vec4(.1,.1,.1,.1);

out vec4 out_color;

void main() {
    float brightness = max(0,dot(norm,light_direction));
    vec4 light = light_color*brightness+ambient_color;
    out_color = light*texture(tex_sampler, texc);
}
