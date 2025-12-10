# Installing NfSpy3

NfSpy has been modernized to support standard Python packaging tools like `uv` and `pip`.

## Prerequisites

*   **Python 3.6+**
*   **Linux** (required for `nfspy` FUSE mount)
*   **libfuse-dev**: Required if you intend to use the FUSE client (`nfspy`).
    *   Ubuntu/Debian: `sudo apt-get install libfuse-dev`
    *   Fedora/RHEL: `sudo dnf install fuse-devel`

## Installation

### Using `uv` (Recommended)

To install the tool in an isolated environment:

```bash
# Install with FUSE support (recommended for Linux)
uv tool install .[fuse]

# Install only the interactive shell (nfspysh)
uv tool install .
```

### Using `pip`

```bash
# Install with FUSE support
pip install .[fuse]

# Install only the interactive shell
pip install .
```

## Troubleshooting FUSE Support

The `nfspy` tool relies on the `fuse-python` bindings (which provide the `fuse` module with `fuse.Fuse` class).

*   **Note:** `fusepy` is a different library and is **not compatible** with this codebase, as it uses a different API. The project requires `fuse-python`.
*   If installation of `fuse-python` fails, ensure you have the C compiler and FUSE development headers (`libfuse-dev`) installed on your system.

## Verification

After installation, verify the tools are available in your path:

```bash
nfspysh --help
nfspy --help  # Only works if [fuse] was installed
```
