import functools
import os
import runpy
from urllib.error import URLError
from urllib.request import Request, urlopen

from dnslib import DNSRecord


def send_over_https(record, _dest, _port=53, tcp=False, ipv6=False, timeout=None):
    request = Request(
        "https://dns.google/dns-query",
        data=record.pack(),
        headers={
            "Content-Type": "application/dns-message",
            "Accept": "application/dns-message",
        },
    )
    try:
        with urlopen(request, timeout=timeout or 5) as response:
            content = response.read(65536)
        if len(content) > 65535:
            raise ValueError("Oversized DNS response")
        return content
    except (URLError, TimeoutError, ValueError) as error:
        raise TimeoutError("DNS-over-HTTPS upstream failed") from error


if __name__ == "__main__":
    if os.environ.get("STATION_DNS_DOH") == "1":
        DNSRecord.send = send_over_https
    else:
        DNSRecord.send = functools.partialmethod(DNSRecord.send, tcp=True)
    runpy.run_module("dnslib.intercept", run_name="__main__")
