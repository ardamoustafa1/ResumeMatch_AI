# Root-level conftest.py
# Exclude locust load tests from pytest collection.
# Locust uses gevent which monkey-patches SSL and causes a RecursionError in Python 3.14+.
# Run load tests manually: locust -f tests/load_test.py --host=http://localhost:8000
collect_ignore = ["tests/load_test.py"]
