// Per-vertex lighting in the style of OpenGL's fixed-function pipeline,
// for renderers that have none (OpenGL ES, WebGL): ambient light plus up to
// MAX_LIGHTS point or directional lights, with Blinn-Phong highlights.

#define MAX_LIGHTS 4

in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec4 p3d_Color;
in vec2 p3d_MultiTexCoord0;

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;
uniform vec4 p3d_ColorScale;

uniform struct {
  vec4 ambient;
} p3d_LightModel;

// Without a material Panda passes white ambient and diffuse and an
// all-zero emission; a material's emission has an alpha of one.
uniform struct {
  vec4 ambient;
  vec4 diffuse;
  vec4 emission;
  vec3 specular;
  float shininess;
} p3d_Material;

// Unused entries have a black colour.
uniform struct {
  vec4 color;
  vec4 specular;
  vec4 position;      // in view space; w = 0 for directional lights
  vec3 attenuation;   // constant, linear, quadratic
} p3d_LightSource[MAX_LIGHTS];

out vec2 texcoord;
out vec4 color;
out vec3 highlight;

void main ()
{
  gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
  texcoord = p3d_MultiTexCoord0;

  // Like fixed-function lighting: a material's diffuse colour replaces the
  // vertex colour, which still tints the ambient term.
  bool has_material = p3d_Material.emission.a > 0.5;
  vec4 diffuse = has_material ? p3d_Material.diffuse : p3d_Color;
  vec3 ambient = p3d_Color.rgb * p3d_Material.ambient.rgb;

  vec3 position = (p3d_ModelViewMatrix * p3d_Vertex).xyz;
  vec3 normal = normalize (p3d_NormalMatrix * p3d_Normal);
  vec3 to_eye = normalize (-position);

  vec3 light = ambient * p3d_LightModel.ambient.rgb;
  highlight = vec3 (0.0);
  for (int i = 0; i < MAX_LIGHTS; ++i) {
    // Unused entries are all zeros in some Panda versions, which would
    // divide by zero below.
    if (p3d_LightSource[i].color.rgb == vec3 (0.0)) {
      continue;
    }
    vec4 lpos = p3d_LightSource[i].position;
    vec3 to_light = lpos.xyz - position * lpos.w;
    float dist = length (to_light);
    to_light /= dist;
    vec3 att = p3d_LightSource[i].attenuation;
    float falloff = lpos.w == 0.0 ? 1.0 :
      1.0 / (att.x + att.y * dist + att.z * dist * dist);
    float lambert = max (dot (normal, to_light), 0.0);
    light += p3d_LightSource[i].color.rgb * diffuse.rgb * lambert * falloff;
    if (lambert > 0.0 && p3d_Material.shininess > 0.0) {
      float spec = max (dot (normal, normalize (to_light + to_eye)), 0.0);
      highlight += p3d_LightSource[i].specular.rgb * p3d_Material.specular
        * pow (spec, p3d_Material.shininess) * falloff;
    }
  }

  color = vec4 (light + p3d_Material.emission.rgb, diffuse.a) * p3d_ColorScale;
}
