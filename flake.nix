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

        # Every package in nix/packages, able to depend on the others by name.
        scope = pkgs.lib.makeScope pkgs.newScope (self: {
          # Panda3D ships prebuilt wheels per CPython minor version, so the
          # interpreter is pinned to one the wheels are built for.
          python = pkgs.python313;

          panda3d = self.callPackage ./nix/packages/panda3d.nix { };
          panda3d-interrogate = self.callPackage ./nix/packages/panda3d-interrogate.nix { };
          pigeoncide = self.callPackage ./nix/package.nix { };

          # The web build.
          emscripten-cache = self.callPackage ./nix/packages/emscripten-cache.nix { };
          cpython-wasm = self.callPackage ./nix/packages/cpython-wasm.nix { };
          ode-wasm = self.callPackage ./nix/packages/ode-wasm { };
          panda3d-wasm = self.callPackage ./nix/packages/panda3d-wasm { };
          pigeoncide-web = self.callPackage ./nix/packages/pigeoncide-web { };
          serve-web = self.callPackage ./nix/packages/serve-web.nix { };
        });
      in
      {
        packages = {
          default = scope.pigeoncide;
          inherit (scope)
            panda3d
            panda3d-interrogate
            emscripten-cache
            cpython-wasm
            ode-wasm
            panda3d-wasm
            pigeoncide-web
            serve-web
            ;
        };

        # Building the package runs the unit tests.
        checks.default = scope.pigeoncide;

        devShells.default = scope.callPackage ./nix/devshell.nix { };
      }
    );
}
