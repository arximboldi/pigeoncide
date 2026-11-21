// Blurs the glow buffer vertically with a six-tap kernel.

uniform sampler2D p3d_Texture0;

in vec2 texcoord;
out vec4 o_color;

void main ()
{
  vec2 dir = vec2 (0.0, 1.0);
  vec3 offset = vec3 (1.0, 5.0, 9.0) / 1024.0;
  o_color  = texture (p3d_Texture0, texcoord - dir * offset.z) * 5.0;
  o_color += texture (p3d_Texture0, texcoord - dir * offset.y) * 8.0;
  o_color += texture (p3d_Texture0, texcoord - dir * offset.x) * 10.0;
  o_color += texture (p3d_Texture0, texcoord + dir * offset.x) * 10.0;
  o_color += texture (p3d_Texture0, texcoord + dir * offset.y) * 8.0;
  o_color += texture (p3d_Texture0, texcoord + dir * offset.z) * 5.0;
  o_color *= 0.030;
}
