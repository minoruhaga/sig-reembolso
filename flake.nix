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
      qualityPythonEnv = pkgs.python312.withPackages (ps: with ps; [
        django
        pillow
        python-dotenv
        pip
        bandit
        coverage
      ]);
    in
    {
      devShells.${system} = rec {
        default = backend;

        backend = pkgs.mkShell {
          name = "sig-reembolso-backend";
          packages = [
            pythonEnv
            pkgs.git
          ];
          shellHook = ''
            export PATH=$HOME/.nix-profile/bin:$PATH
            export PYTHONPATH="$PWD/src:$PYTHONPATH"
            echo "Ambiente Backend ativo (Python 3.12 + Django 5 + Pillow)"
          '';
        };

        quality = pkgs.mkShell {
          name = "sig-reembolso-quality";
          packages = [
            qualityPythonEnv
            pkgs.git
            pkgs.ruff
            pkgs.gitleaks
          ];
          shellHook = ''
            export PATH=$HOME/.nix-profile/bin:$PATH
            export PYTHONPATH="$PWD/src:$PYTHONPATH"
            echo "Ambiente de Quality Gates ativo (Ruff + Gitleaks + Bandit + Coverage)"
          '';
        };
      };
    };
}
