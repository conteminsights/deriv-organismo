from pathlib import Path


def test_docker_compose_declares_postgres_and_redis():
    content = Path("docker-compose.yml").read_text()
    assert "postgres:" in content
    assert "redis:" in content
