import http.client
import ssl
from json import loads
from typing import List
from urllib.parse import urlencode


class HTTPRequests(object):
    def __init__(self, web_address: str):
        self._conn = http.client.HTTPSConnection(
            web_address,
            context=ssl._create_unverified_context())

    def get_request(self, params: str = "") -> bytes:
        endpoint = f"/get?{params}" if params else "/get"
        self._conn.request("GET", endpoint)
        response = self._conn.getresponse()
        if response.status != 200:
            raise RuntimeError(
                f"ErrorCode: {response.status} {response.reason}")
        return response.read()


class FishTextWebsiteHttpRequest(object):
    def __init__(self):
        self._website_requests = HTTPRequests("fish-text.ru")

    def request_sentences(self, count: int) -> List[str]:
        return self._request_text("sentence", count)

    def request_titles(self, count: int) -> List[str]:
        return self._request_text("title", count)

    def request_paragraphs(self, count: int) -> List[str]:
        return self._request_text("paragraph", count)

    def _request_text(self, text_type: str, count: int) -> List[str]:
        params = urlencode({"type": text_type,
                            "number": count,
                            "format": "json"})
        text = self._make_request(params)

        separator = ". " if text_type == "sentence" else "\\n\\n"
        return text.split(sep=separator)

    def _make_request(self, params: str) -> str:
        response = self._website_requests.get_request(params)
        response_dict = loads(response.decode("utf-8"))
        return response_dict["text"]
