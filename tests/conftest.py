"""Shared test fixtures for ShieldOps CLI tests."""
import pytest
from click.testing import CliRunner


@pytest.fixture
def runner():
    """Provide a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_config(tmp_path, monkeypatch):
    """Redirect config to a temp directory so tests don't touch real config."""
    config_dir = tmp_path / ".shieldops"
    config_dir.mkdir()
    monkeypatch.setattr("shieldops_cli.config.CONFIG_DIR", config_dir)
    monkeypatch.setattr("shieldops_cli.config.CONFIG_FILE", config_dir / "config.json")
    return config_dir


@pytest.fixture
def sample_dockerfile(tmp_path):
    """Create a sample Dockerfile for testing."""
    df = tmp_path / "Dockerfile"
    df.write_text("FROM python:3.11\nRUN pip install flask\nCOPY . /app\nCMD [\"python\", \"app.py\"]\n")
    return df


@pytest.fixture
def sample_k8s(tmp_path):
    """Create a sample Kubernetes manifest for testing."""
    k8s = tmp_path / "deployment.yaml"
    k8s.write_text("""apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: test
  template:
    metadata:
      labels:
        app: test
    spec:
      containers:
      - name: test
        image: nginx:latest
        ports:
        - containerPort: 80
""")
    return k8s


@pytest.fixture
def sample_compose(tmp_path):
    """Create a sample docker-compose.yml for testing."""
    dc = tmp_path / "docker-compose.yml"
    dc.write_text("""version: '3.8'
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
""")
    return dc
