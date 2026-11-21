# Pigeoncide for web browsers: a static site with the game compiled to
# WebAssembly. The game's Python code is frozen and linked with CPython and
# Panda3D into pigeoncide.wasm; the assets are packed into pigeoncide.data,
# with models converted to .bam, since the web build has no .egg loader.
# Serve the output directory over HTTP.
{
  lib,
  stdenv,
  python312,
  emscripten,
  emscripten-cache,
  cpython-wasm,
  ode-wasm,
  panda3d,
  panda3d-wasm,
}:

let
  # Freezing needs a host interpreter matching the target's Python version.
  hostPanda3d = panda3d.override { python = python312; };
  hostPython = python312.withPackages (_: [ hostPanda3d ]);
in
stdenv.mkDerivation {
  pname = "pigeoncide-web";
  version = "0.0.1";

  src = lib.fileset.toSource {
    root = ../../..;
    fileset = lib.fileset.unions [
      ../../../src
      ../../../data
    ];
  };

  nativeBuildInputs = [
    emscripten
    hostPython
  ];

  dontConfigure = true;

  buildPhase = ''
    runHook preBuild
    export EM_CACHE="$TMPDIR/emscripten-cache"
    cp -r --no-preserve=mode ${emscripten-cache} "$EM_CACHE"

    # The files the game reads at run time, laid out as under WEB_ROOT.
    mkdir -p assets/src/core
    cp -r data assets/data
    cp -r src/core/sha assets/src/core/sha
    find assets/data -name '*.egg' | while read -r egg; do
      ${hostPanda3d}/bin/egg2bam -noabs -ps rel -o "''${egg%.egg}.bam" "$egg"
      rm "$egg"
    done

    # FreezeTool from the web build's direct package; panda3d.core from
    # the host's desktop Panda3D.
    mkdir hostpath
    ln -s ${panda3d-wasm}/direct hostpath/direct
    PYTHONPATH=$PWD/hostpath python3 ${./freeze.py} \
      src assets ${cpython-wasm} ${panda3d-wasm} ${ode-wasm} out
    runHook postBuild
  '';

  installPhase = ''
    runHook preInstall
    mkdir -p $out
    cp out/pigeoncide.js out/pigeoncide.wasm out/pigeoncide.data $out/
    cp ${./index.html} $out/index.html
    runHook postInstall
  '';

  dontFixup = true;

  meta = {
    description = "Pigeoncide compiled to WebAssembly, as a static website";
    homepage = "https://savannah.nongnu.org/projects/pigeoncide/";
    license = lib.licenses.gpl3Plus;
    platforms = [
      "x86_64-linux"
      "aarch64-linux"
    ];
  };
}
