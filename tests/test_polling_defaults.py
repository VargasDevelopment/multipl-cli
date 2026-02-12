from multipl_cli import polling


def test_fast_poll_default_is_650ms() -> None:
    assert polling.FAST_POLL_MS == 650
