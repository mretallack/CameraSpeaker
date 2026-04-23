# CameraSpeaker — Tasks

## Phase 1: Project Scaffolding

- [x] **Task 1.1**: Create project structure (`camera_speaker/`, `tests/`, `pyproject.toml`, `.gitignore`, `README.md`)
- [x] **Task 1.2**: Create `pyproject.toml` with metadata and `paramiko` dependency
- [x] **Task 1.3**: Write initial `README.md` with usage examples

## Phase 2: Core Implementation

- [x] **Task 2.1**: Implement `config.py` — Load config from CLI args, env vars, config file, and defaults
- [x] **Task 2.2**: Implement `transport.py` — SSH connection, command execution, and SCP file upload using paramiko
- [x] **Task 2.3**: Implement `converter.py` — Format detection and ffmpeg-based conversion to Opus
- [x] **Task 2.4**: Implement `cli.py` — Argparse CLI with `play`, `say`, `sound`, `sounds`, `stop` subcommands
- [x] **Task 2.5**: Wire up `__init__.py` and `__main__.py` entry point

## Phase 3: Testing

- [x] **Task 3.1**: Write unit tests for `converter.py` (format detection, conversion command building)
- [x] **Task 3.2**: Write unit tests for `config.py` (priority resolution, defaults)
- [ ] **Task 3.3**: Write integration test script for manual camera testing

## Phase 4: Documentation & Polish

- [x] **Task 4.1**: Complete `README.md` with installation, configuration, and all usage examples
- [x] **Task 4.2**: Add example config file (`config.ini.example`)
- [ ] **Task 4.3**: Initialize git repository
