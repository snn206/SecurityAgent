"""Unit tests for versioning and component management."""

from security_agent.versioning.manager import (
    VersionManager,
    bump_version,
    is_valid_semver,
    parse_semver,
)


def test_semver_parsing_and_bump():
    assert parse_semver("1.2.3") == (1, 2, 3)
    assert is_valid_semver("0.1.0")
    assert is_valid_semver("2.0.0-beta.1")
    assert not is_valid_semver("v1.0")

    assert bump_version("1.2.3", "patch") == "1.2.4"
    assert bump_version("1.2.3", "minor") == "1.3.0"
    assert bump_version("1.2.3", "major") == "2.0.0"


def test_version_manager_registry_read():
    vm = VersionManager()
    reg = vm.load_registry()
    assert "core" in reg
    assert "providers" in reg

    entry, keys = vm.resolve_component("core")
    assert keys == ["core"]
    assert "version" in entry
    assert entry["version"] == "0.1.0"


def test_version_manager_resolve_provider():
    vm = VersionManager()
    entry, keys = vm.resolve_component("providers.anthropic")
    assert keys == ["providers", "anthropic"]
    assert entry["version"] == "0.1.0"
    assert entry["package"] == "langchain-anthropic"
