{
  description = "Pigeoncide, a game about a child who must kill all the pigeons in the world";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    { nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachSystem [ "x86_64-linux" "aarch64-linux" ] (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        # Panda3D ships prebuilt wheels per CPython minor version, so the
        # interpreter is pinned to the one the wheel was built for.
        python = pkgs.python313;
        panda3d = pkgs.callPackage ./nix/packages/panda3d.nix { inherit python; };
        pigeoncide = pkgs.callPackage ./nix/package.nix { inherit python panda3d; };
      in
      {
        packages = {
          default = pigeoncide;
          inherit panda3d;
        };
        devShells.default = pkgs.callPackage ./nix/devshell.nix { inherit python panda3d; };
      }
    );
}
