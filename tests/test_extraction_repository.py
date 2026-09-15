"""The sibling extraction service is chosen explicitly for one installation."""

import json

import httpx
import pytest

from edusharing.errors import EduSharingError
from edusharing.extraction import TextExtraction


@pytest.mark.parametrize("repository, expected", [
    ("https://repository.staging.example.org", "https://text-extraction.staging.example.org"),
    ("repository.example.org", "https://text-extraction.example.org"),
    ("https://repository.example.org/edu-sharing/rest/", "https://text-extraction.example.org"),
    ("https://repository.example.org/prefix/edu-sharing", "https://text-extraction.example.org"),
    ("http://repository.dev.example.org:8080", "http://text-extraction.dev.example.org:8080"),
    ("HTTPS://REPOSITORY.EXAMPLE.ORG/", "https://text-extraction.example.org"),
    ("https://repository.bücher.example", "https://text-extraction.xn--bcher-kva.example"),
])
async def test_repository_factory_keeps_the_installation_and_does_not_probe(repository, expected):
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(200, json={"status": "ok"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as http:
        async with TextExtraction.from_repository(repository, client=http) as service:
            assert service.base_url == expected
            assert requests == [], "construction must not contact either service"
            assert await service.ping() == {"status": "ok"}
            assert str(requests[0].url) == expected + "/_ping"
        assert not http.is_closed, "the injected client still belongs to its caller"


@pytest.mark.parametrize("url", [
    "", "https://example.org", "https://repo.example.org", "https://repository.org",
    "http://localhost:8080", "http://127.0.0.1", "ftp://repository.example.org",
    "https://repository.example.org:invalid", "https://repository.example.org:65536",
    "https://user:SECRET@repository.example.org", "user:SECRET@repository.example.org",
    "https://repository.example.org/path?token=SECRET",
    "https://repository.example.org/#SECRET", "https://repository.example.org/path\\SECRET",
    "https://repository.foo bar.org", "https://repository.foo%2F.org",
    "https://repository.-example.org", "https://repository.example-.org",
    "https://repository.foo_bar.org", "https://repository..example.org",
    "https://repository." + "a" * 64 + ".org",
    "https://repository." + ("a" * 60 + ".") * 4 + "org",
])
def test_nonstandard_or_unsafe_repository_address_needs_explicit_service(url):
    with pytest.raises(EduSharingError, match="TextExtraction") as error:
        TextExtraction.from_repository(url)
    assert "SECRET" not in str(error.value)


@pytest.mark.parametrize("method, output_format, body", [
    ("simple", "txt", "Unsere Mission\nBildungsmaterialien"),
    ("browser", "markdown", "## Unsere Mission\n\n[Bildung](https://example.org)"),
])
async def test_supplied_extraction_modes_keep_the_service_request_and_text(
    method, output_format, body, monkeypatch,
):
    monkeypatch.setenv(TextExtraction.ENV_BASE_URL, "https://unrelated.example.org")
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(200, json={"text": body, "lang": "de", "status": 200})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as http:
        async with TextExtraction.from_repository(
            "https://repository.example.org/edu-sharing", client=http,
            resolve=lambda _: ["93.184.216.34"],
        ) as service:
            result = await service.text_of(
                "https://wirlernenonline.de", method=method, output_format=output_format,
            )
    assert str(requests[0].url) == "https://text-extraction.example.org/from-url"
    assert json.loads(requests[0].content) == {
        "url": "https://wirlernenonline.de", "method": method,
        "output_format": output_format, "lang": "auto", "preference": "none",
    }
    assert result.text == body
    assert result.status == 200
    assert result.lang == "de"
    assert result.char_count == len(body)
    assert not result.truncated


def test_environment_factory_still_requires_explicit_service(monkeypatch):
    monkeypatch.delenv(TextExtraction.ENV_BASE_URL, raising=False)
    monkeypatch.setenv("EDU_SHARING_URL", "https://repository.example.org")
    with pytest.raises(EduSharingError, match=TextExtraction.ENV_BASE_URL):
        TextExtraction.from_env()
