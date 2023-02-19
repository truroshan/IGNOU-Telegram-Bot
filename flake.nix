{
  description = "IGNOU Telegram Bot v2.0";

  inputs.nixpkgs.url = "github:NixOs/nixpkgs/nixos-22.11";
  inputs.flake-utils.url = "github:numtide/flake-utils/v1.0.0";

  outputs = inputs: (inputs.flake-utils.lib.eachDefaultSystem ( system : 
    let 
        pname = "ignou";
        version = "2.0";

        pkgs = inputs.nixpkgs.legacyPackages.${system};

        pyEnv = pkgs.python3.withPackages (p: with p; [
        pyrogram
        tgcrypto
        httpx
        prettytable
        beautifulsoup4
        ]);

        ignouScript = pkgs.writeShellScriptBin "start-bot" ''
          cd ${ignou}
          ${pyEnv}/bin/python3 -m bot'';


        ignou =  pkgs.stdenv.mkDerivation {
          pname = "ignou-telegram-bot";
          version = "2.0";
          runtimeDependencies = [ pyEnv ];
          src = ./.;
          installPhase = ''
            mkdir -p $out/bot
            cp -r bot/* $out/bot/
          '';
        };


    in rec {

        packages.default = pkgs.buildEnv {
          name = "${pname}-${version}";
          paths = [ ignou ignouScript ];
        };

        devShell = pkgs.mkShell {
          buildInputs = [ pyEnv ];
        };
    })) // {
        nixosModules.default = import ./nix/module.nix inputs;
    };
}
