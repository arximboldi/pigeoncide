# CPython compiled to WebAssembly with Emscripten, as static libraries for
# linking into a browser program. Built from the same source as nixpkgs'
# python312, so bytecode frozen by that interpreter matches.
{
  stdenv,
  python312,
  emscripten,
  emscripten-cache,
  pkg-config,
  zlib,
}:

stdenv.mkDerivation {
  pname = "cpython-wasm";
  inherit (python312) version src;

  nativeBuildInputs = [
    emscripten
    python312
    pkg-config
  ];
  # The build first compiles a native interpreter, which needs zlib.
  buildInputs = [ zlib ];

  # wasm_build.py expects the tools inside the Emscripten SDK directory;
  # nixpkgs installs them as wrappers on PATH instead.
  postPatch = ''
    substituteInPlace Tools/wasm/wasm_build.py \
      --replace-fail 'configure_wrapper=EMSCRIPTEN_ROOT / "emconfigure"' \
                     'configure_wrapper=pathlib.Path(shutil.which("emconfigure"))' \
      --replace-fail 'ports=EMSCRIPTEN_ROOT / "embuilder"' \
                     'ports=pathlib.Path(shutil.which("embuilder"))' \
      --replace-fail 'cc=EMSCRIPTEN_ROOT / "emcc"' \
                     'cc=pathlib.Path(shutil.which("emcc"))' \
      --replace-fail 'make_wrapper=EMSCRIPTEN_ROOT / "emmake"' \
                     'make_wrapper=pathlib.Path(shutil.which("emmake"))'
  '';

  dontConfigure = true;

  buildPhase = ''
    runHook preBuild
    export EM_CONFIG=${emscripten}/share/emscripten/.emscripten
    export EM_CACHE="$TMPDIR/emscripten-cache"
    cp -r --no-preserve=mode ${emscripten-cache} "$EM_CACHE"
    python3 Tools/wasm/wasm_build.py emscripten-browser
    runHook postBuild
  '';

  installPhase = ''
    runHook preInstall
    build=builddir/emscripten-browser
    make -C $build install DESTDIR="$TMPDIR/install"
    mv "$TMPDIR/install/usr/local" $out
    # Static libraries of built-in modules that a final link also needs.
    cp $build/Modules/_hacl/libHacl_Hash_SHA2.a \
       $build/Modules/_decimal/libmpdec/libmpdec.a \
       $build/Modules/expat/libexpat.a \
       $out/lib/
    runHook postInstall
  '';

  dontFixup = true;

  meta = python312.meta // {
    description = "CPython for Emscripten (static libraries)";
    platforms = [
      "x86_64-linux"
      "aarch64-linux"
    ];
  };
}
