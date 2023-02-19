{
  description = "IGNOU Telegram Bot v2.0";

  inputs.nixpkgs.url = "github:NixOs/nixpkgs/nixos-22.11";
  inputs.flake-utils.url = "github:numtide/flake-utils/v1.0.0";

  outputs = inputs: inputs.flake-utils.lib.eachDefaultSystem ( system : 
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

        ignouDrv =  pkgs.stdenv.mkDerivation {
          pname = "ignou-telegram-bot";
          version = "2.0";
          src = ./.;
          installPhase = ''
            mkdir -p $out/bot
            cp -r bot/* $out/bot/
          '';
        };

        ignouScript = pkgs.writeShellScriptBin "start-bot" ''
          cd ${ignouDrv}
          ${pyEnv}/bin/python3 -m bot'';

    in {

        packages.deafult = pkgs.buildEnv {
          name = "${pname}-${version}";
          paths = [ ignouDrv pyEnv ];
        };

        devShell = pkgs.mkShell {
          buildInputs = [ pyEnv ];
        };

        nixosModules.default = import ./nix/module.nix inputs;

    });
}
