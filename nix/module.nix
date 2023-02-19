inputs: { 
    config,
    lib,
    pkgs,
    ...
    }: 
let
    cfg = config.services.ignou;
    ignou = inputs.self.packages.${pkgs.stdenv.hostPlatform.system}.default;

in
with lib;
{
    options = {

        services.ignou = {

            enable = mkEnableOption "Enable the IGNOU Bot service";

            BOT_TOKEN = mkOption {
                type = types.str;
                description = "Telegram Bot Token";
            };

        };
    };

    config = mkIf cfg.enable {

        systemd.services.ignou = {

            description = "IGNOU Telegram Bot";

            after = [ "network.target" ];

            wantedBy = [ "multi-user.target" ];

            serviceConfig = {
                Type = "oneshot";
                ExecStart = "${ignou}/bin/start-bot";
            };

            environment = {
                BOT_TOKEN = cfg.BOT_TOKEN;
            };

        };

    };
}