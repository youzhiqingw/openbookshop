# Files and Directories to Exclude from GitHub

This document lists all files and directories that should not be uploaded to GitHub for this Django + Vue3 online bookshop project.

## Python/Django Backend Files to Exclude

### Compiled Python Files
- `__pycache__/` directories (Python bytecode cache)
- `*.pyc` files (compiled Python bytecode)
- `*.pyo` files (optimized Python bytecode)
- `*.pyd` files (Python extension modules)
- `$py.class` files

### Virtual Environment
- `venv/` (Python virtual environment)
- `.venv/` (alternative virtual environment)
- `env/` (environment directory)
- `.env` (environment variables - contains sensitive data)
- `ENV/` (Windows environment)
- `env.bak/` (backup environment)
- `venv.bak/` (backup virtual environment)

### Database Files
- `db.sqlite3` (SQLite database file)
- `db.sqlite3-journal` (SQLite journal file)
- Any other `*.sqlite` or `*.db` files

### Logs and Cache
- `*.log` files (application logs)
- `openbookshop/backend/logs/` (log directory)
- `.pytest_cache/` (pytest cache)
- `.mypy_cache/` (mypy type checker cache)
- `.ruff_cache/` (ruff linter cache)
- `.cache/` (general cache)

### Test Coverage
- `.coverage` (coverage.py data)
- `.coverage.*` (coverage.py data with patterns)
- `htmlcov/` (HTML coverage reports)
- `coverage.xml` (XML coverage reports)
- `*.cover` (coverage files)
- `*.py.cover` (Python coverage files)

### Build and Distribution
- `build/` (build directory)
- `dist/` (distribution directory)
- `*.egg-info/` (egg metadata)
- `.eggs/` (installed eggs)
- `*.egg` (egg files)
- `develop-eggs/` (development eggs)
- `downloads/` (downloads directory)
- `eggs/` (eggs directory)
- `lib/` (library directory)
- `lib64/` (64-bit library directory)
- `parts/` (build parts)
- `sdist/` (source distribution)
- `var/` (variable data)
- `wheels/` (wheel packages)
- `share/python-wheels/` (shared wheels)
- `.installed.cfg` (installation config)
- `MANIFEST` (manifest file)

## Node.js/Frontend Files to Exclude

### Dependencies
- `openbookshop/frontend/node_modules/` (NPM dependencies)
- Any other `node_modules/` directories

### Build Output
- `openbookshop/frontend/dist/` (build output directory)
- `npm-debug.log*` (NPM debug logs)
- `yarn-debug.log*` (Yarn debug logs)
- `yarn-error.log*` (Yarn error logs)
- `.pnpm-debug.log*` (PNPM debug logs)

## IDE and Editor Files

### VS Code
- `.vscode/` (VS Code settings - optional exclusion)
- `.vscode/*` (specific VS Code files)

### PyCharm
- `.idea/` (PyCharm project files - optional exclusion)

### General IDE
- `.spyderproject` (Spyder project)
- `.spyproject` (Spyder project)
- `.ropeproject` (Rope project)
- `.ipynb_checkpoints` (Jupyter notebook checkpoints)

## Operating System Files
- `.DS_Store` (macOS)
- `Thumbs.db` (Windows)
- `.directory` (Linux)

## Media and Uploads
- `openbookshop/backend/media/` (uploaded media files)
- Any user-generated content directories

## Environment and Configuration
- `.env` (environment variables with secrets)
- `local_settings.py` (Django local settings)
- `.python-version` (pyenv version)
- `.pdm-python` (PDM Python)
- `.pdm-build/` (PDM build)
- `.pixi` (Pixi environment)

## Documentation Builds
- `docs/_build/` (Sphinx documentation build)
- `/site` (mkdocs build)

## Temporary Files
- `celerybeat-schedule` (Celery scheduler)
- `celerybeat.pid` (Celery PID file)
- `pip-log.txt` (pip log)
- `pip-delete-this-directory.txt` (pip cleanup)
- `.sage.py` (SageMath parsed files)

## Git-related
- `.git/` (Git repository - already excluded by Git)

## Project-specific Exclusions for OpenBookShop

### Backend-specific
- `openbookshop/backend/media/` (uploaded files)
- `openbookshop/backend/logs/` (application logs)
- Any `*.log` files in backend

### Frontend-specific
- `openbookshop/frontend/node_modules/` (dependencies)
- `openbookshop/frontend/dist/` (build output)

## Files That Should Be Included

### Configuration Examples
- `.env.example` (environment variable example)
- `requirements.txt` (Python dependencies)
- `package.json` (Node.js dependencies)
- `package-lock.json` (Node.js lock file)

### Source Code
- All `*.py` files in `openbookshop/backend/`
- All source files in `openbookshop/frontend/src/`
- Configuration files (`settings.py`, `urls.py`, etc.)
- Templates and static files
- Documentation files (`.md`)

### Build and Deployment
- `Dockerfile` files
- `docker-compose.yml`
- Deployment scripts
- GitHub workflow files

## Notes

1. **Security**: Never commit `.env` files or any files containing passwords, API keys, or other secrets.
2. **Dependencies**: Always commit dependency specification files (`.txt`, `.json`, `requirements.txt`) but never the actual dependency directories.
3. **Build Artifacts**: Never commit build outputs or compiled files - these should be built during deployment.
4. **IDE Files**: Consider whether to exclude IDE-specific files based on team preferences.

The existing `.gitignore` file in the project root already covers most of these exclusions.