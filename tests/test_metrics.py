from datapilot.metrics import results_match


def res(columns, rows):
    return {"columns": columns, "rows": rows}


def test_identical_results_match():
    g = res(["a"], [(1,), (2,)])
    assert results_match(g, res(["x"], [(1,), (2,)]))


def test_row_order_is_ignored():
    g = res(["a"], [(1,), (2,)])
    assert results_match(g, res(["a"], [(2,), (1,)]))


def test_extra_columns_are_allowed():
    g = res(["ville"], [("sao paulo",)])
    assert results_match(g, res(["ville", "n"], [("sao paulo", 15540)]))


def test_different_value_fails():
    assert not results_match(res(["a"], [(1,)]), res(["a"], [(2,)]))


def test_different_row_count_fails():
    assert not results_match(res(["a"], [(1,), (2,)]), res(["a"], [(1,)]))


def test_error_fails():
    assert not results_match(res(["a"], [(1,)]), {"error": "no such column"})


def test_none_prediction_fails():
    assert not results_match(res(["a"], [(1,)]), None)


def test_floats_are_rounded():
    assert results_match(res(["m"], [(12.5,)]), res(["m"], [(12.4999,)]))