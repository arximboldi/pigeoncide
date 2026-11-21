// Applies the base texture to the colour lit per vertex by lit.vert, then
// adds the specular highlight on top, as fixed-function OpenGL does with a
// separate specular colour.

uniform sampler2D p3d_Texture0;

in vec2 texcoord;
in vec4 color;
in vec3 highlight;
out vec4 o_color;

void main ()
{
  o_color = color * texture (p3d_Texture0, texcoord);
  o_color.rgb += highlight;
}
