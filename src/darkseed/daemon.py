"""Darkseed daemon that listens for DNS requests and commands."""

import copy
import random
import socketserver
import threading
import time
from pathlib import Path

from dnslib import AAAA, QTYPE, RR, TXT, A, DNSRecord

# Generate dummy records until real data is read from crawler outputs
SeedRecords = []
for i in range(20):
    SeedRecords.append((QTYPE.A, A(f"192.168.178.{i}")))
    SeedRecords.append((QTYPE.AAAA, AAAA(f"ff06:f00d::10:{i}")))
    SeedRecords.append((QTYPE.TXT, TXT(f"Test data {i}")))


def dns_handler(data, addr):
    request = DNSRecord.parse(data)
    print(f"Received DNS request from {addr}")

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
            print("No more records to return.")
            return

        rtype, rdata = random.choice(pool)
        # log.debug print(f"attempting to add rtype={rtype}, rdata={rdata}")
        # todos:
        # - avoid dups
        # - inbue with domain knowledge (e.g., if CJDNS, I2P, and TOR records exist,
        #   provide at least one of the two former, two of the latter)
        rrec = RR("seed.21.ninja", rtype=rtype, ttl=60, rdata=rdata)

        reply_new = copy.deepcopy(reply)
        reply_new.add_answer(rrec)

        if len(reply_new.pack()) > size_limit:
            # exit early. room for opt: try another record
            print(f"new_size={len(reply_new.pack())}B exceeds limit={size_limit}B")
            break

        num_recs += 1
        print(
            f"Added record (data={rrec.rdata}, type={rrec.rtype}, number={num_recs}, "
            f"prev_size={len(reply.pack())}B, new_size={len(reply.pack())}B)"
        )
        reply = reply_new

    print(f"Done creating reply (size={len(reply.pack())}B, records={num_recs}")
    return reply.pack()


class DNSRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        response = dns_handler(data, self.client_address)
        reply_size = len(response)
        print(f"Sending DNS reply (size={reply_size})...", end="")
        socket.sendto(response, self.client_address)
        print("done.")


class CommandServerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip().decode("utf-8")
        print(f"Command received: {data}")
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
#         print(f"Files in {directory}: {files}")
#         time.sleep(600)  # Sleep for 10 minutes (600 seconds)
#


def main():
    dns_thread = threading.Thread(target=start_dns_server)
    command_thread = threading.Thread(target=start_command_server)
    # nodes_thread = threading.Thread(
    #     target=list_files_in_directory, args=(directory_to_watch,)
    # )

    dns_thread.start()
    print("Started DNS thread.")
    command_thread.start()
    print("Started command thread.")


if __name__ == "__main__":
    main()
