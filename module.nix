flake: { config, pkgs, lib, ... }:

with lib;

let
  inherit (flake.packages.${pkgs.stdenv.hostPlatform.system}) darkseed;
  cfg = config.services.darkseed;
in
{
  options.services.darkseed = {
    enable = mkEnableOption "darkseed";

    enableTor = mkEnableOption "darkseed via TOR";
    enableI2p = mkEnableOption "darkseed via I2P";

    logLevel = mkOption {
      type = types.str;
      default = "INFO";
      example = "DEBUG";
      description = mdDoc "Log verbosity for console.";
    };

    dns = {
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
        description = mdDoc "Address used by DNS server.";
      };
    };

    rest = {
      port = mkOption {
        type = types.int;
        default = 80;
        example = 8080;
        description = mdDoc "Port used by REST server.";
      };
      address = mkOption {
        type = types.str;
        default = "127.0.0.1";
        example = "192.168.0.1";
        description = mdDoc "Address used by REST server.";
      };
    };


  };

  config = mkIf cfg.enable {
    networking.firewall = {
      allowedUDPPorts = [ cfg.dns.port ];
      allowedTCPPorts = [ cfg.rest.port ];
    };

    services.tor = mkIf cfg.enableTor {
      enable = true;
      enableGeoIP = false;
      relay.onionServices = {
        darkseed = {
          version = 3;
          map = [
            { port = cfg.dns.port; target = { addr = "${cfg.dns.address}"; port = cfg.dns.port; }; }
            { port = cfg.rest.port; target = { addr = "${cfg.rest.address}"; port = cfg.rest.port; }; }
          ];
        };
      };
    };

    services.i2p = mkIf cfg.enableI2p {
      enable = true;
      inTunnels.darkseed = {
        enable = true;
        inPort = cfg.rest.port;
        # destination (my i2p address?)
        address = cfg.rest.address;
        port = cfg.rest.port;
      };
    };


    systemd.services.darkseed = {
      description = "darkseed";
      after = [ "network-online.target" ];
      wantedBy = [ "multi-user.target" ];
      serviceConfig = {
        ExecStart = ''${darkseed}/bin/darkseed \
            --log-level ${cfg.logLevel} \
            --dns-port ${toString cfg.dns.port} \
            --dns-address ${cfg.dns.address} \
            --rest-port ${toString cfg.rest.port} \
            --rest-address ${cfg.rest.address} \
          '';
        AmbientCapabilities = "CAP_NET_BIND_SERVICE";
        DynamicUser = true;
      };
    };
  };
}
