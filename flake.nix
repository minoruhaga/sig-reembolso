{
  description = "Ambiente de desenvolvimento SIG-Reembolso";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      pythonEnv = pkgs.python312.withPackages (ps: with ps; [
        django
        pillow
        python-dotenv
        pip
      ]);
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        name = "sig-reembolso-dev";
        packages = [
          pythonEnv
          pkgs.git
        ];
        shellHook = ''
          export PATH=$HOME/.nix-profile/bin:$PATH
          export PYTHONPATH="$PWD/src:$PYTHONPATH"
          echo "Ambiente SIG-Reembolso ativo (Python 3.12 + Django 5 + Pillow)"
        '';
      };
    };
}
