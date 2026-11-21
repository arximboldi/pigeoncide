// Renders the glowing areas of the scene: the base texture masked by the
// glow map in texture stage 1.

uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1;

in vec2 texcoord;
out vec4 o_color;

void main ()
{
  o_color = texture (p3d_Texture0, texcoord) * texture (p3d_Texture1, texcoord);
}
