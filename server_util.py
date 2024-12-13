# 13.12.24

from urllib.parse import urlparse, unquote


def updateUrl(oldUlr: str, domain: str):

    parsed_url = urlparse(oldUlr)
    hostname = parsed_url.hostname
    domain_part = hostname.split('.')[1]
    new_url = oldUlr.replace(domain_part, domain)

    return new_url