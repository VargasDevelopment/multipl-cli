from multipl_cli import __version__, openapi_client


def test_build_client_includes_user_agent(monkeypatch) -> None:
    class FakeClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    monkeypatch.setattr(openapi_client, "_import_client_classes", lambda: FakeClient)

    client = openapi_client.build_client("https://example.com")

    assert client.kwargs["headers"]["user-agent"] == f"multipl-cli {__version__}"


def test_build_client_includes_auth_and_user_agent(monkeypatch) -> None:
    class FakeClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    monkeypatch.setattr(openapi_client, "_import_client_classes", lambda: FakeClient)

    client = openapi_client.build_client("https://example.com", api_key="abc123")

    assert client.kwargs["headers"]["authorization"] == "Bearer abc123"
    assert client.kwargs["headers"]["user-agent"] == f"multipl-cli {__version__}"
