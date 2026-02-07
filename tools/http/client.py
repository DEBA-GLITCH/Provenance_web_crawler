# tools/http/client.py

import requests
from tools.http.timeouts import TimeoutConfig
from tools.http.headers import build_headers
from tools.http.errors import TransportError, TimeoutError

class HttpClient:
    """
    Raw HTTP execution only.
    No retries. No judgment.
    """

    def __init__(self, timeout_cfg: TimeoutConfig):
        self.timeout_cfg = timeout_cfg

    def fetch(self, url: str) -> dict:
        try:
            resp = requests.get(
                url,
                headers=build_headers(),
                timeout=(
                    self.timeout_cfg.connect_timeout,
                    self.timeout_cfg.read_timeout,
                ),
                allow_redirects=True,
            )
            return {
                "url": url,
                "status": resp.status_code,
                "headers": dict(resp.headers),
                "body": resp.content,
            }

        except requests.exceptions.Timeout as e:
            raise TimeoutError(str(e))

        except requests.exceptions.RequestException as e:
            raise TransportError(str(e))
