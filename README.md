![PyPI version](https://img.shields.io/pypi/v/pytest-depends-on)
![Python](https://img.shields.io/badge/python->=3.12-blue)
![Development Status](https://img.shields.io/badge/status-stable-green)
![Maintenance](https://img.shields.io/maintenance/yes/2026)
![PyPI](https://img.shields.io/pypi/dm/pytest-depends-on)
![License](https://img.shields.io/pypi/l/pytest-depends-on)

---

# pytest-depends-on

An advanced pytest plugin designed for Python projects, offering robust dependency management utilities to enhance the testing workflow. <br>
It allows tests to be skipped based on the execution status of other tests, ensuring that dependent tests do not run if their prerequisites fail or are skipped, resulting in a cleaner and more efficient testing experience.

-----

## 🚀 Features
- ✅ **depends-on**: A powerful marker to declare test dependencies. If a parent test fails or hasn't run, the dependent test is automatically skipped.
    - **Marker:** `@pytest.mark.depends_on`
    - **Arguments:**
        - `tests` (list): A list of parent test names (node IDs) that the current test depends on.
        - `status` (optional): The expected status of the parent test. Defaults to `PASSED`. The dependent test will skip if the parent status does not match this value.
        - `allowed_not_run` (optional): Boolean. If `True`, the test will not skip if the parent test has not run yet. Defaults to `False` (skips if parent is missing).
          <br> <br>
  - ✅ **Automatic Status Tracking**: Automatically tracks the result (`passed`, `failed`, `skipped`, `xfailed`, `xpassed`) of every test during the `call` phase to resolve dependencies dynamically.

-----

## 📦 Installation

```bash
pip install pytest-depends-on
```

-----

### 🔧 Usage

#### 1\. Register the marker

Add the marker to your `pytest.ini` file to avoid warnings (optional, as the plugin programmatically registers it, but good practice):

```ini
[pytest]
markers =
    depends_on: mark test as dependent on another test
```

#### 2\. Implement in your tests

Use the marker decorator on your test functions.

**Basic Dependency:**
`test_child` will only run if `test_parent` passes.

```python
import pytest

def test_parent():
    assert True

@pytest.mark.depends_on(tests=["test_parent"])
def test_child():
    assert True
```

**Custom Status Dependency:**
`test_child` will run only if `test_parent` fails (useful for testing error handling or recovery).

```python
import pytest

from pytest_depends_on.consts.status import Status

@pytest.mark.depends_on(tests=["test_parent"], status=Status.FAILED)
def test_child():
    pass
```

**Soft Dependency:**
`test_child` will run even if `test_parent` hasn't executed yet (e.g., due to ordering).

```python
import pytest

@pytest.mark.depends_on(tests=["test_parent"], allowed_not_run=True)
def test_child():
    pass
```

-----

## 🤝 Contributing

If you have a helpful tool, pattern, or improvement to suggest:
Fork the repo <br>
Create a new branch <br>
Submit a pull request <br>
I welcome additions that promote clean, productive, and maintainable development. <br>

-----

## 🙏 Thanks

Thanks for exploring this repository\! <br>
Happy coding\! <br>
