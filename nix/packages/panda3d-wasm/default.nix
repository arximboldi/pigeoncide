# Panda3D built for the browser with Emscripten: static libraries for the
# engine and its Python modules, plus the Python "direct" package, ready to
# be frozen and linked with cpython-wasm into a single program.
#
# No Panda3D release supports the web yet; the WebGL port lives on the
# master branch, so this pins a commit of it. Only the parts the game uses
# are built: WebGL, OpenAL, Vorbis, FreeType, ODE physics and particles.
{
  lib,
  stdenv,
  fetchFromGitHub,
  writeShellScriptBin,
  python312,
  emscripten,
  emscripten-cache,
  cpython-wasm,
  ode-wasm,
  panda3d-interrogate,
}:

let
  rev = "ec9ea0a93a7de249efea3f41b4fdf878f5e1650b";

  # When cross-compiling, makepanda points PYTHONHOME at the target Python,
  # which breaks the Python-based Emscripten tools; run them without it.
  emscriptenTools = map (
    tool:
    writeShellScriptBin tool ''
      exec env -u PYTHONHOME -u PYTHONPATH ${emscripten}/bin/${tool} "$@"
    ''
  ) [ "emcc" "em++" "emar" "emranlib" ];
in
stdenv.mkDerivation {
  pname = "panda3d-wasm";
  version = "1.11.0-unstable-2026-07-25";

  src = fetchFromGitHub {
    owner = "panda3d";
    repo = "panda3d";
    inherit rev;
    hash = "sha256-1U6kgItFQEo0kaGKAuXFWg1qtzkMCHPuf9WieVfDQd4=";
  };

  patches = [
    # Panda never noticed pointer lock engaging, so it could not re-centre
    # the pointer and mouse look spun the view. Not yet reported upstream.
    ./pointerlockchange-on-document.patch
    # Panda sized the canvas in CSS pixels, so on high-DPI screens the game
    # was rendered at a lower resolution and stretched. Not yet reported
    # upstream.
    ./canvas-device-pixels.patch
  ];

  nativeBuildInputs = emscriptenTools ++ [ python312 ];

  dontConfigure = true;

  buildPhase = ''
    runHook preBuild
    export EM_CACHE="$TMPDIR/emscripten-cache"
    cp -r --no-preserve=mode ${emscripten-cache} "$EM_CACHE"
    export CC=emcc CXX=em++ AR=emar RANLIB=emranlib
    export INTERROGATE=${panda3d-interrogate}/bin/interrogate
    export INTERROGATE_MODULE=${panda3d-interrogate}/bin/interrogate_module
    python3 makepanda/makepanda.py \
      --target emscripten --static --nothing \
      --use-python --use-direct --use-gles2 \
      --use-openal --use-vorbis --use-zlib --use-freetype --use-harfbuzz \
      --use-pandaphysics --use-pandaparticlesystem \
      --use-ode --ode-incdir=${ode-wasm}/include --ode-libdir=${ode-wasm}/lib \
      --python-incdir=${cpython-wasm}/include --python-libdir=${cpython-wasm}/lib \
      --optimize 4 --threads $NIX_BUILD_CORES \
      --outputdir $out --git-commit=${rev}
    runHook postBuild
  '';

  installPhase = ''
    runHook preInstall
    rm -rf $out/tmp
    runHook postInstall
  '';

  dontFixup = true;

  meta = {
    description = "Panda3D game engine for Emscripten (static libraries)";
    homepage = "https://www.panda3d.org/";
    license = lib.licenses.bsd3;
    platforms = [
      "x86_64-linux"
      "aarch64-linux"
    ];
  };
}
