# Staff Sergeant AKA SSG (a Static Site Generator)

A Python-based static site generator that is compatible with Jekyll content.
The main focus of SSG is for my blog, but it is easy enough to extend for
other purposes.  SSG is quite minimal, it provides a base set of templates
for creating an index page and blog posts. Styling and additional pages are
left up to the user.

## Quickstart

1. Clone this project

## Install

Install the released package from the project's GitHub Releases using pip:

1. Download the desired release wheel or source archive from the GitHub Releases page: <https://github.com/swysocki/staffsergeant/releases>

1. Install with pip (replace the path/filename below with the downloaded file):

```powershell
python -m pip install C:\path\to\staffsergeant-<version>-py3-none-any.whl
```

After installing the package globally you can run the `ssg` module or `ssg.py` as documented.

You can also add the package to a `requirements.txt` using a GitHub release tag, for example:

```text
staffsergeant @ git+https://github.com/swysocki/staffsergeant@v0.0.1
```

## Development setup

This project uses `uv` to manage virtual environments and pinned dependencies. Recommended workflow to set up a development environment:

1. Install the `uv` CLI (if you don't have it). On Windows you can use winget:

```powershell
winget install --id astral-sh.uv -e
```


1. Create (or recreate) the project virtual environment at `.venv` using your system Python (use the python you want, e.g. Python 3.14):

```powershell
uv venv --python C:\Path\To\python.exe .venv
```

1. Sync the locked dependencies into the created venv (installs both runtime and dev deps):

```powershell
uv pip sync requirements.lock requirements-dev.lock -p .venv\Scripts\python.exe
```

1. Activate the venv and run tests:

```powershell
. .\.venv\Scripts\Activate.ps1
python -m pytest
```

1. VS Code: the workspace can be configured to use the project venv by adding or ensuring the following in `.vscode/settings.json`:

```jsonc
{
  "python.defaultInterpreterPath": "${workspaceFolder}\\.venv\\Scripts\\python.exe"
}
```

Notes

- If uv complains about the project's Python requirement, use a system Python that meets `pyproject.toml` (>=3.12).
- Recreate the `.venv` whenever you change the system python used to run the project.
- You can also use `uv pip sync requirements.lock` alone if you don't want dev dependencies.

1. Copy your blog posts to the `_posts` directory
1. Run `python3 ssg.py generate` from the root of the project
1. (Optional) View your website locally by running `python3 -m http.server ./docs`
