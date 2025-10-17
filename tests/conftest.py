import pytest

# Define the 'extension' marker for grouping your new tests (NX1)
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "extension: marks tests as part of the project extension validation suite (NX1)"
    )