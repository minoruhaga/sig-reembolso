{ pkgs ? import <nixpkgs> {} }:

let
  pythonEnv = pkgs.python312.withPackages (ps: with ps; [
    django
    pillow
    python-dotenv
    pip
  ]);
in
pkgs.mkShell {
  name = "sig-reembolso-dev";
  packages = [
    pythonEnv
    pkgs.git
  ];
  shellHook = ''
    export PATH=$HOME/.nix-profile/bin:$PATH
    export PYTHONPATH="$PWD/src:$PYTHONPATH"
  '';
}
