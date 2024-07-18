"""CLI for darkdig."""


import base64
import importlib.metadata
import time

import dns.flags
import dns.opcode
import dns.query
import dns.rcode
import dns.rdataclass
import dns.rdatatype
import dns.resolver
import dns.reversename
import dns.zone

from darkseed.dns import CustomNullEncoding

from .config import get_config

__version__ = importlib.metadata.version("darkseed")


def lookup(
    domain: str, nameserver: str, port: int, ctype: str = "A"
) -> dns.resolver.Answer:
    """Look up DNS records for a domain."""

    resolver = dns.resolver.Resolver()
    resolver.nameservers = [nameserver]
    resolver.port = port

    answer = resolver.resolve(domain, ctype)
    return answer


class PrettyPrinter:
    """Class to pretty print DNS query response."""

    @staticmethod
    def print_header(response):
        """Print DNS query response header."""
        print(";; ->>HEADER<<-", end=" ")
        print(f"opcode: {dns.opcode.to_text(response.opcode())}", end=", ")
        print(f"status: {dns.rcode.to_text(response.rcode())}", end=", ")
        print(f"id: {response.id}")

        # section mapping: query/0, answer/1, authority/2, additional/3
        print(f";; flags: {dns.flags.to_text(response.flags).lower()}", end=", ")
        print(f"QUERY: {len(response.sections[0])}", end=", ")
        print(f"ANSWER: {len(response.sections[1])}", end=", ")
        print(f"AUTHORITY: {len(response.sections[2])}", end=", ")
        print(f"ADDITIONAL: {len(response.sections[3])}")

        # Todo: WARNING IF Recursion requested but not available

        print("\n", end="")

    @staticmethod
    def print_question_section(response):
        """Print DNS query response question section."""
        domain = response.canonical_name()
        print(";;QUESTION SECTION:")
        for rrset in response.section_from_number(0):
            print(
                f"; domain={domain},"
                f" rdclass={dns.rdataclass.to_text(rrset.rdclass)},"
                f" rdtype={dns.rdatatype.to_text(rrset.rdtype)}"
            )
        print("\n", end="")

    @staticmethod
    def print_authority_section(response):
        """Print DNS query response authority section."""
        if len(response.sections[2]):
            raise NotImplementedError("Authority section not implemented yet.")

    @staticmethod
    def print_additional_section(response):
        """Print DNS query response additional section."""
        if len(response.sections[2]):
            raise NotImplementedError("Additional section not implemented yet.")

    @staticmethod
    def print_answer_section(response):
        """Print DNS query response answer section."""
        domain = response.canonical_name()
        print(";;ANSWER SECTION:")
        for rrset in response.section_from_number(1):
            for rdata in rrset:
                if rdata.rdtype != dns.rdatatype.NULL:
                    PrettyPrinter.print_regular_answer_record(domain, rrset, rdata)
                else:
                    PrettyPrinter.print_null_answer_record(domain, rrset, rdata)
        print("\n", end="")

    @staticmethod
    def print_regular_answer_record(domain, rrset, rdata):
        """Print one regular DNS query response answer record."""
        print(
            f"domain={domain},"
            f" ttl={rrset.ttl},"
            f" rdclass={dns.rdataclass.to_text(rrset.rdclass)},"
            f" rdtype={dns.rdatatype.to_text(rrset.rdtype)},"
            f" data={rdata}"
        )

    @staticmethod
    def print_null_answer_record(domain, rrset, rdata):
        """Print one custom NULL-encoded DNS query response answer record."""

        print(
            f"domain={domain},"
            f" ttl={rrset.ttl},"
            f" rdclass={dns.rdataclass.to_text(rrset.rdclass)},"
            f" rdtype={dns.rdatatype.to_text(rrset.rdtype)}"
        )

        data_base64 = base64.b64encode(rdata.to_wire()).decode("ascii").rstrip("=")
        encoding = CustomNullEncoding.from_bytes(rdata.to_wire())
        print(";; ->>custom NULL encoding<<-", end=" ")
        print(f"size: {len(rdata.to_wire())}", end=", ")
        print(f"records: {encoding.num_records}", end=", ")
        print(f"data (base64): {data_base64}")

        for pos, record in enumerate(encoding.records):
            print(";; ->>custom NULL-encoded address <<-", end=" ")
            print(f"record: {pos}", end=", ")
            print(f"address: {record._address}")

    @staticmethod
    def print_sections(response):
        """Print DNS query response sections."""

        PrettyPrinter.print_question_section(response)
        PrettyPrinter.print_answer_section(response)
        PrettyPrinter.print_authority_section(response)
        PrettyPrinter.print_additional_section(response)

    @staticmethod
    def print(answer):
        """Pretty print DNS query response."""
        response = answer.response
        PrettyPrinter.print_header(response)
        PrettyPrinter.print_sections(response)


def main():
    """Entry point."""
    conf = get_config()
    print(f"; <<>> darkdig {__version__} <<>>", end=" ")
    if conf.nameserver:
        print(f"@{conf.nameserver}", end=" ")
        print(f"-p {conf.port}", end=" ")
    if conf.verbose:
        print("-v", end=" ")
    print(f"{conf.domain}")

    lookup_start = time.time()
    answer = lookup(conf.domain, conf.nameserver, conf.port)
    lookup_end = time.time()

    PrettyPrinter.print(answer)

    lookup_time_msec = int((lookup_end - lookup_start) * 1000)
    print(f";; Query time: {lookup_time_msec} msec")
    print(f";; SERVER: {answer.nameserver}#{answer.port}")
    local_time = time.localtime(lookup_end)
    formatted_time = time.strftime("%a %b %d %H:%M:%S %Z %Y", local_time)
    print(f";; WHEN: {formatted_time}")
    print(f";; MSG SIZE  rcvd: {len(answer.response.to_wire())}")


if __name__ == "__main__":
    main()
