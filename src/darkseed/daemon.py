"""Darkseed daemon that listens for DNS requests and commands."""

import socketserver
import threading

from dnslib import AAAA, RR, TXT, A, DNSRecord


def dns_handler(data, addr):
    request = DNSRecord.parse(data)
    print(f"Received DNS request from {addr}")

    reply = request.reply()
    reply.add_answer(RR("example.com", rtype=1, ttl=300, rdata=A("127.0.0.2")))
    reply.add_answer(RR("example.com", rtype=28, ttl=300, rdata=AAAA("::2")))
    reply.add_answer(RR("example.com", rtype=16, ttl=300, rdata=TXT("text successful")))
    return reply.pack()


class DNSRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        response = dns_handler(data, self.client_address)
        print("Sending DNS reply...", end="")
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


def main():
    dns_thread = threading.Thread(target=start_dns_server)
    command_thread = threading.Thread(target=start_command_server)
    dns_thread.start()
    print("Started DNS thread.")
    command_thread.start()
    print("Started command thread.")


if __name__ == "__main__":
    main()
