from src.app.version import __version__
import pytest


def test_get_version(test_client):
    """Test GET /version endpoint returns correct version."""
    response = test_client.get("/api/v1/version")
    assert response.status_code == 200
    assert response.json() == {"version": __version__}


def test_get_version_response_structure(test_client):
    """Test that version response has correct structure."""
    response = test_client.get("/api/v1/version")
    assert response.status_code == 200
    
    json_response = response.json()
    assert "version" in json_response
    assert isinstance(json_response["version"], str)
    assert len(json_response) == 1


def test_get_version_content_type(test_client):
    """Test that version endpoint returns JSON content type."""
    response = test_client.get("/api/v1/version")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"


def test_get_version_version_format(test_client):
    """Test that version follows semantic versioning format."""
    response = test_client.get("/api/v1/version")
    assert response.status_code == 200
    
    version = response.json()["version"]
    version_parts = version.split(".")
    assert len(version_parts) >= 2, "Version should have at least major.minor format"
    
    for part in version_parts:
        assert part.isdigit(), f"Version part '{part}' should be numeric"


def test_get_version_matches_module_version(test_client):
    """Test that API version matches the module version exactly."""
    response = test_client.get("/api/v1/version")
    assert response.status_code == 200
    assert response.json()["version"] == __version__


def test_get_version_wrong_path_returns_404(test_client):
    """Test that wrong version paths return 404."""
    wrong_paths = [
        "/version",
        "/api/version", 
        "/api/v1/ver",
        "/api/v2/version"
    ]
    
    for path in wrong_paths:
        response = test_client.get(path)
        assert response.status_code == 404
