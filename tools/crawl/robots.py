# tools/crawl/robots.py

import time
import urllib.robotparser as robotparser
from tools.http.client import HttpClient

class RobotsCacheEntry:
    def __init__(self, parser, fetched_at):
        self.parser = parser
        self.fetched_at = fetched_at

class RobotsPolicy:
    """
    Domain-scoped robots.txt policy with TTL.
    """

    TTL_SECONDS = 3600

    def __init__(self, http_client: HttpClient):
        self.http = http_client
        self.cache = {}

    def allowed(self, url: str, user_agent: str) -> bool:
        domain = self._domain(url)
        entry = self.cache.get(domain)

        if not entry or time.time() - entry.fetched_at > self.TTL_SECONDS:
            entry = self._fetch(domain)
            self.cache[domain] = entry

        return entry.parser.can_fetch(user_agent, url)

    def _fetch(self, domain: str) -> RobotsCacheEntry:
        robots_url = f"{domain}/robots.txt"
        parser = robotparser.RobotFileParser()

        try:
            resp = self.http.fetch(robots_url)
            parser.parse(resp["body"].decode("utf-8", errors="ignore").splitlines())
        except Exception:
            parser.disallow_all = False  # fail-open, but recorded later

        return RobotsCacheEntry(parser, time.time())

    def _domain(self, url: str) -> str:
        return url.split("/", 3)[0] + "//" + url.split("/", 3)[2]
