"""Darkseed daemon that listens for DNS requests and commands."""

import copy
import logging as log
import random
import socketserver
import threading
import time

from dnslib import AAAA, QTYPE, RR, TXT, A, DNSRecord

from darkseed.config import get_config

# Generate dummy records until real data is read from crawler outputs
SeedRecords = []
for i in range(20):
    SeedRecords.append((QTYPE.A, A(f"192.168.178.{i}")))
    SeedRecords.append((QTYPE.AAAA, AAAA(f"ff06:f00d::10:{i}")))
    SeedRecords.append((QTYPE.TXT, TXT(f"Test data {i}")))


def dns_handler(data, addr) -> bytearray:
    request = DNSRecord.parse(data)
    log.debug("Received DNS request from %s", addr)

    # if TimeUp():
    #   create new selection
    # else:
    #   use the current selection

    reply = request.reply()

    pool = SeedRecords.copy()
    num_recs = 0
    size_limit = 512
    while True:
        if not pool:
            log.warning("Ran out of reachable nodes during reply creation.")
            if num_recs == 0:
                log.warning("Returning empty reply")
            return reply.pack()

        rtype, rdata = random.choice(pool)
        # log.debug("attempting to add rtype=%s, rdata=%s", rtype, rdata)
        # todos:
        # - avoid dups
        # - inbue with domain knowledge (e.g., if CJDNS, I2P, and TOR records exist,
        #   provide at least one of the two former, two of the latter)
        rrec = RR("seed.21.ninja", rtype=rtype, ttl=60, rdata=rdata)

        reply_new = copy.deepcopy(reply)
        reply_new.add_answer(rrec)

        if len(reply_new.pack()) > size_limit:
            # exit early. room for opt: try another record
            log.debug(
                "new_size=%dB exceeds limit=%dB", len(reply_new.pack()), size_limit
            )
            break

        num_recs += 1
        log.debug(
            "Added record (data=%s, type=%s, number=%d, prev_size=%dB, new_size=%dB)",
            rrec.rdata,
            rrec.rtype,
            num_recs,
            len(reply.pack()),
            len(reply_new.pack()),
        )
        reply = reply_new

    log.info("Created reply (size=%dB, records=%d)", len(reply.pack()), num_recs)
    return reply.pack()


class DNSRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        response = dns_handler(data, self.client_address)
        reply_size = len(response)
        socket.sendto(response, self.client_address)
        log.debug("Sent DNS reply (size=%d, to=%s)", reply_size, self.client_address)


class CommandServerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip().decode("utf-8")
        log.debug("Command received: %s", data)
        response = ""
        if data.lower() == "status":
            response = "Server running. Uptime: 100 minutes."
        elif data.lower() == "update":
            response = "Updated records."
        else:
            response = "Invalid command."

        self.request.sendall(response.encode("utf-8"))


def start_dns_server():
    server = socketserver.UDPServer(("localhost", 8053), DNSRequestHandler)
    server.serve_forever()


def start_command_server():
    server = socketserver.TCPServer(("localhost", 8054), CommandServerHandler)
    server.serve_forever()


# def list_files_in_directory(directory):
#     while True:
#         files = os.listdir(directory)
#         log.debug(f"Files in {directory}: {files}")
#         time.sleep(600)  # Sleep for 10 minutes (600 seconds)
#


def init():
    """
    Handle initialization.

    First, check requirements, then parse command-line arguments and create
    settings object. Next, sanity-check the settings and initialize the logger.
    """


def main():
    """Parse command-line arguments, set up logging, and run darkseed daemon."""

    conf = get_config()
    log.basicConfig(
        level=conf.log_level,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    log.Formatter.converter = time.gmtime
    log.info("Using configuration: %s", conf)

    dns_thread = threading.Thread(target=start_dns_server)
    command_thread = threading.Thread(target=start_command_server)
    # nodes_thread = threading.Thread(
    #     target=list_files_in_directory, args=(directory_to_watch,)
    # )

    dns_thread.start()
    log.info("Started DNS thread.")
    command_thread.start()
    log.info("Started command thread.")


if __name__ == "__main__":
    main()
