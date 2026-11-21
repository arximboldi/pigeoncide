# The ODE physics engine as a static WebAssembly library, for linking into
# the web build of Panda3D. Single precision, as Panda3D expects, and
# without threading, which the browser build does not have.
{
  stdenv,
  ode,
  emscripten,
  emscripten-cache,
  cmake,
  ninja,
}:

stdenv.mkDerivation {
  pname = "ode-wasm";
  inherit (ode) version src;

  # ODE's build does not know Emscripten: it would fail to identify the
  # platform and enable x86 assembly for Emscripten's nominal "x86" CPU.
  patches = [ ./emscripten.patch ];

  nativeBuildInputs = [
    emscripten
    cmake
    ninja
  ];

  configurePhase = ''
    runHook preConfigure
    export EM_CACHE="$TMPDIR/emscripten-cache"
    cp -r --no-preserve=mode ${emscripten-cache} "$EM_CACHE"
    emcmake cmake -G Ninja -B build -S . \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX=$out \
      -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
      -DBUILD_SHARED_LIBS=OFF \
      -DODE_DOUBLE_PRECISION=OFF \
      -DODE_WITH_DEMOS=OFF \
      -DODE_WITH_TESTS=OFF \
      -DODE_NO_BUILTIN_THREADING_IMPL=ON \
      -DODE_NO_THREADING_INTF=ON
    runHook postConfigure
  '';

  buildPhase = ''
    runHook preBuild
    ninja -C build
    runHook postBuild
  '';

  installPhase = ''
    runHook preInstall
    ninja -C build install
    runHook postInstall
  '';

  dontFixup = true;

  meta = ode.meta // {
    description = "ODE physics engine for Emscripten (static library)";
    platforms = [
      "x86_64-linux"
      "aarch64-linux"
    ];
  };
}
