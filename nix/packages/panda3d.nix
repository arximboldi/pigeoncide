# Panda3D is not in nixpkgs. Building it from source with makepanda is a
# large, fragile build, so this repackages the official manylinux wheel and
# points its ELF files at Nix store libraries instead.
{
  lib,
  stdenv,
  fetchurl,
  python,
  autoPatchelfHook,
  libGL,
  libx11,
  libxext,
  libxrandr,
  libxcursor,
  libxxf86dga,
  libxi,
  zlib,
  alsa-lib,
}:

let
  version = "1.10.16";
  wheels = {
    x86_64-linux = {
      url = "https://files.pythonhosted.org/packages/77/d3/5e6c3feff433efbfc49e2723ff83b53bf06c10e1169e564b1c017e226013/panda3d-${version}-cp313-cp313-manylinux2014_x86_64.whl";
      hash = "sha256-IFOllgFPIdXM4PqT6utyOmhfPAIxpjMSxFOv8XM+0GE=";
    };
    aarch64-linux = {
      url = "https://files.pythonhosted.org/packages/7d/cb/e0d2f433c6ae3f52d27b9cdb6ca9c3f7bbfd558d8876de1a3021c7207778/panda3d-${version}-cp313-cp313-manylinux2014_aarch64.whl";
      hash = "sha256-+3q4S3Lpd6oIRqED4O5ROPXJ8t5IYVKRQgu0dXbisrc=";
    };
  };
in
python.pkgs.buildPythonPackage {
  pname = "panda3d";
  inherit version;
  format = "wheel";

  src = fetchurl (
    wheels.${stdenv.hostPlatform.system}
      or (throw "panda3d: no wheel for ${stdenv.hostPlatform.system}")
  );

  nativeBuildInputs = [
    autoPatchelfHook
  ];

  buildInputs = [
    stdenv.cc.cc.lib
    libGL
    libx11
    libxext
    libxrandr
    libxcursor
    libxxf86dga
    libxi
    zlib
  ];

  # The bundled OpenAL Soft is linked statically and dlopens its audio
  # backend, so autoPatchelf cannot see it as a NEEDED entry. Only ALSA is
  # wired up: its PulseAudio backend rejects current libpulse, and PipeWire
  # systems serve ALSA clients through their ALSA plugin anyway.
  appendRunpaths = [ "${lib.getLib alsa-lib}/lib" ];

  # deploy_libs holds frozen-app support modules for the wheel's own CPython
  # build, and the pstats profiler GUI links against GTK 2. Neither is needed
  # to run games, and keeping them would pull in unrelated libraries.
  postInstall = ''
    rm -rf $out/${python.sitePackages}/deploy_libs
    rm $out/${python.sitePackages}/panda3d_tools/pstats
  '';

  pythonImportsCheck = [
    "panda3d.core"
    "panda3d.ode"
    "direct.showbase.ShowBase"
  ];

  meta = {
    description = "Panda3D game engine (official binary wheel)";
    homepage = "https://www.panda3d.org/";
    license = lib.licenses.bsd3;
    sourceProvenance = [ lib.sourceTypes.binaryNativeCode ];
    platforms = builtins.attrNames wheels;
  };
}
