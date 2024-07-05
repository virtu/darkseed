flake: { config, pkgs, lib, ... }:

with lib;

let
  inherit (flake.packages.${pkgs.stdenv.hostPlatform.system}) darkseed;
  cfg = config.services.darkseed;
in
{
  options.services.darkseed = {
    enable = mkEnableOption "darkseed";

    logLevel = mkOption {
      type = types.str;
      default = "INFO";
      example = "DEBUG";
      description = mdDoc "Log verbosity for console.";
    };

  };

  config = mkIf cfg.enable {
    systemd.services.darkseed = {
      description = "darkseed";
      after = [ "network-online.target" ];

      serviceConfig = {
        ExecStart = ''${darkseed}/bin/darkseed \
            --log-level ${cfg.logLevel} \
          '';
        DynamicUser = true;
      };
    };
  };
}
