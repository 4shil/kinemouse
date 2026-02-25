# Contributing to KineMouse

We welcome contributions! Here's how:

## Development Setup

```bash
git clone https://github.com/4shil/kinemouse
cd kinemouse
pip install -r requirements.txt
pip install pytest pytest-cov
```

## Running Tests

```bash
pytest tests/ -v --cov=kinemouse
```

## Code Style

- Follow PEP 8
- Type hints encouraged
- Docstrings for public functions

## Adding a New Backend

1. Subclass `BaseBackend` in `kinemouse/backends/`
2. Implement: `get_screen_resolution()`, `move()`, `click()`, `right_click()`, `mouse_down()`, `mouse_up()`
3. Update `get_backend()` in `kinemouse/backends/__init__.py`
4. Test thoroughly with gesture FSM
5. Submit PR with platform-specific setup guide in `docs/`

## Reporting Issues

- Describe OS, Python version, and exact error
- Paste verbose output (run `python main.py --debug` if available)
- Include steps to reproduce

## PR Guidelines

- Target the `main` branch
- Include tests for new features
- Update docs if adding/changing public APIs
- One feature per PR

Thank you! 🎉
