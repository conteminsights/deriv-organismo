from pathlib import Path


def test_runbooks_exist():
    assert Path("docs/runbooks/local-demo.md").exists()
    assert Path("docs/runbooks/promotion-readiness.md").exists()
