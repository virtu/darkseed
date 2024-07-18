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

    port = mkOption {
      type = types.int;
      default = 53;
      example = 8053;
      description = mdDoc "Port used by DNS server.";
    };

    address = mkOption {
      type = types.str;
      default = "127.0.0.1";
      example = "192.168.0.1";
      description = mdDoc "address used by DNS server.";
    };

  };

  config = mkIf cfg.enable {
    networking.firewall.allowedUDPPorts = [ cfg.port ];
    systemd.services.darkseed = {
      description = "darkseed";
      after = [ "network-online.target" ];
      wantedBy = [ "multi-user.target" ];
      serviceConfig = {
        ExecStart = ''${darkseed}/bin/darkseed \
            --log-level ${cfg.logLevel} \
            --dns-port ${toString cfg.port} \
            --dns-address ${cfg.address} \
          '';
        AmbientCapabilities = "CAP_NET_BIND_SERVICE";
        DynamicUser = true;
      };
    };
  };
}
