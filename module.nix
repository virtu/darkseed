flake: { config, pkgs, lib, ... }:

with lib;

let
  inherit (flake.packages.${pkgs.stdenv.hostPlatform.system}) darkseed;
  cfg = config.services.darkseed;
in
{
  options.services.darkseed = {
    enable = mkEnableOption "darkseed";

    tor.enable = mkEnableOption "darkseed via TOR";
    i2p.enable = mkEnableOption "darkseed via I2P";
    cjdns = {
      enable = mkEnableOption "darkseed via CJDNS";
      address = mkOption {
        type = types.nullOr types.str;
        default = null;
        example = "fcf9:45bc:8c48:6973:7b3f:5538:6e51:8fc9";
        description = mdDoc "Address used by CJDNS server.";
      };
    };

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
      zone = mkOption {
        type = types.nullOr types.str;
        default = null;
        example = "dnsseed.acme.com.";
        description = mdDoc "Zone managed by DNS server.";
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
    assertions = [
      { assertion = !(cfg.cjdns.enable && cfg.cjdns.address == null); message = "services.darkseed.cjdns.address must be set when services.darkseed.cjdns.enable is true."; }
      { assertion = cfg.dns.zone != null; message = "services.darkseed.dns.zone must be set."; }
    ];

    networking.firewall = {
      allowedUDPPorts = [ cfg.dns.port ];
      allowedTCPPorts = [ cfg.dns.port cfg.rest.port ];
    };

    services.tor = mkIf cfg.tor.enable {
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

    services.i2pd = mkIf cfg.i2p.enable {
      enable = true;
      inTunnels.darkseed_rest = {
        enable = true;
        inPort = cfg.rest.port;
        destination = cfg.rest.address;
        address = cfg.rest.address;
        port = cfg.rest.port;
      };
      inTunnels.darkseed_dns = {
        enable = true;
        inPort = cfg.dns.port;
        destination = cfg.dns.address;
        address = cfg.dns.address;
        port = cfg.dns.port;
      };
    };

    services.nginx = mkIf cfg.cjdns.enable {
      enable = true;
      recommendedGzipSettings = true;
      recommendedOptimisation = true;
      recommendedProxySettings = true;
      recommendedTlsSettings = true;
      virtualHosts = {
        darkseed_rest = {
          listen = [{ addr = "[${cfg.cjdns.address}]"; port = cfg.rest.port; }];
          locations."/" = { proxyPass = "http://${cfg.rest.address}:${toString cfg.rest.port}"; };
        };
      };
    };
    environment.systemPackages = with pkgs; [
      socat
    ];
    systemd.services.socat-tcp-forward = {
      description = "TCP Forwarder on specific IPv6 address using socat";
      wantedBy = [ "multi-user.target" ];
      serviceConfig = {
        ExecStart = "${pkgs.socat}/bin/socat TCP6-LISTEN:${cfg.dns.port},bind=${cfg.cjdns.address},fork,su=nobody TCP4:${cfg.dns.address}:${cfg.dns.port}";
        Restart = "always";
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
            --dns-zone ${cfg.dns.zone} \
            --rest-port ${toString cfg.rest.port} \
            --rest-address ${cfg.rest.address} \
          '';
        AmbientCapabilities = "CAP_NET_BIND_SERVICE";
        DynamicUser = true;
      };
    };
  };
}
