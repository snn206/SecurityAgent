# Packages

Custom installable Python packages for SecurityAgent.

## Structure

Each package is a standard Python package installable via pip/uv.

```bash
uv pip install ./packages/my_package/
```

Register in `registry/versions.yaml`:

```yaml
packages:
  my_package:
    version: "1.0.0"
    artifact: "pypi"
    changelog: "registry/changelog/packages/my_package.md"
```
