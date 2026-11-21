{
  lib,
  stdenvNoCC,
  makeWrapper,
  python,
  panda3d,
}:

let
  pythonEnv = python.withPackages (_: [ panda3d ]);
in
stdenvNoCC.mkDerivation {
  pname = "pigeoncide";
  version = "0.0.1";

  src = lib.fileset.toSource {
    root = ../.;
    fileset = lib.fileset.unions [
      ../src
      ../data
    ];
  };

  nativeBuildInputs = [ makeWrapper ];

  # The game finds data/ as a sibling of src/, so both are installed
  # together under share/.
  installPhase = ''
    runHook preInstall
    mkdir -p $out/share/pigeoncide
    cp -r src data $out/share/pigeoncide/
    ${pythonEnv.interpreter} -m compileall -q $out/share/pigeoncide/src
    makeWrapper ${pythonEnv.interpreter} $out/bin/pigeoncide \
      --add-flags $out/share/pigeoncide/src/main.py
    runHook postInstall
  '';

  doInstallCheck = true;
  installCheckPhase = ''
    runHook preInstallCheck
    ${pythonEnv.interpreter} $out/share/pigeoncide/src/test_main.py
    runHook postInstallCheck
  '';

  meta = {
    description = "Game about an ill-minded child whose imaginary friend tells him to kill all the pigeons";
    homepage = "https://savannah.nongnu.org/projects/pigeoncide/";
    license = lib.licenses.gpl3Plus;
    mainProgram = "pigeoncide";
    platforms = panda3d.meta.platforms;
  };
}
