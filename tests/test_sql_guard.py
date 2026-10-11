import pytest
from datapilot.tools.sql_guard import validate_sql


def test_select_ok_and_limit_added():
    assert validate_sql("SELECT * FROM orders").endswith("LIMIT 50")


def test_existing_limit_kept():
    assert validate_sql("SELECT * FROM orders LIMIT 5") == "SELECT * FROM orders LIMIT 5"


@pytest.mark.parametrize("sql", [
    "DROP TABLE orders",
    "DELETE FROM orders",
    "UPDATE orders SET x = 1",
    "SELECT 1; DROP TABLE orders",
    "INSERT INTO orders VALUES (1)",
])
def test_dangerous_queries_blocked(sql):
    with pytest.raises(ValueError):
        validate_sql(sql)