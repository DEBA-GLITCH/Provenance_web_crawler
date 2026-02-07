# tools/crawl/fetch_page.py

from tools.http.client import HttpClient
from tools.crawl.robots import RobotsPolicy
from validators.transport import validate_transport
from validators.structure import validate_structure
from orchestrator.failure_event import FailureEvent
from orchestrator.execution_context import FailureClass

def fetch_page(url, http: HttpClient, robots: RobotsPolicy):
    if not robots.allowed(url, "*"):
        return FailureEvent(FailureClass.CLIENT_ERROR, 403, "Blocked by robots.txt")

    resp = http.fetch(url)

    failure = validate_transport(resp)
    if failure:
        return failure

    failure = validate_structure(resp)
    if failure:
        return failure

    return resp
