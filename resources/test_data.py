import pytest

MOVIES_FILTER_DATA = [
    pytest.param(1000, 3000, 'MSK', 2, id="Medium price MSK"),
    pytest.param(1, 500, 'SPB', 1, id="Cheap SPB"),
    pytest.param(5000, 10000, "MSK", 3, id="Expensive MSK")
]