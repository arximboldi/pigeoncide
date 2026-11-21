{
  mkShell,
  python,
  panda3d,
}:

mkShell {
  packages = [
    (python.withPackages (_: [ panda3d ]))
  ];
}
