# Panda3D's binding generator, needed on the build machine to build Panda3D
# from source. Upstream ships it only as prebuilt PyPI wheels; this takes
# the two command-line tools out of the wheel.
{
  lib,
  stdenv,
  fetchurl,
  unzip,
  autoPatchelfHook,
}:

let
  version = "0.11.2";
  wheels = {
    x86_64-linux = {
      url = "https://files.pythonhosted.org/packages/b6/3a/b233d6669f66ece060d4f2bceb00dbd47b684ac18f34e963313554d99387/panda3d_interrogate-${version}-cp33-abi3-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl";
      hash = "sha256-wAUj+6GeMbtpZK9XhDt8Cn7iR5XjYmauNMo29Dj4wLM=";
    };
    aarch64-linux = {
      url = "https://files.pythonhosted.org/packages/fc/1e/a04e3c55c3a73f2ac1bb156738a8dec05543bacf4b5a95dced31c6556972/panda3d_interrogate-${version}-cp33-abi3-manylinux_2_24_aarch64.manylinux_2_28_aarch64.whl";
      hash = "sha256-0Aq8Y4Yt8QUhj4uXxtAmhbGMpSsaXi3+q3vEopgyvoI=";
    };
  };
in
stdenv.mkDerivation {
  pname = "panda3d-interrogate";
  inherit version;

  src = fetchurl (
    wheels.${stdenv.hostPlatform.system}
      or (throw "panda3d-interrogate: no wheel for ${stdenv.hostPlatform.system}")
  );

  nativeBuildInputs = [
    unzip
    autoPatchelfHook
  ];
  buildInputs = [ stdenv.cc.cc.lib ];

  unpackPhase = "unzip $src";

  installPhase = ''
    install -Dm755 interrogate/interrogate $out/bin/interrogate
    install -Dm755 interrogate_module/interrogate_module $out/bin/interrogate_module
  '';

  meta = {
    description = "Binding generator for Panda3D";
    homepage = "https://github.com/panda3d/interrogate";
    license = lib.licenses.bsd3;
    sourceProvenance = [ lib.sourceTypes.binaryNativeCode ];
    platforms = builtins.attrNames wheels;
  };
}
