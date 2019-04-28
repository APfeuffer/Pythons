#version 330

in vec4 norm;
in vec2 texc;
in vec4 eye;

uniform sampler2D tex_sampler;
uniform vec4 light_direction = vec4(0,0,1,0);
uniform vec4 light_color = vec4(1,1,1,1);
uniform vec4 ambient_color = vec4(.1,.1,.1,.1);
uniform float spec_exponent = 5.0;
uniform float spec_factor = 1;

out vec4 out_color;

void main() {
    vec4 n = normalize(norm);
    float brightness = max(0,dot(n,light_direction));
    float costheta = max(0,dot(normalize(eye),reflect(light_direction,n)));
    vec4 light = light_color*brightness+ambient_color;
    out_color = light*texture(tex_sampler, texc)+spec_factor*pow(costheta,spec_exponent)*light_color;
}
