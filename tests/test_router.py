from datapilot.agent.graph import MAX_ATTEMPTS, route_after_execute


def make_state(error=None, rows=(("x",),), attempts=1):
    return {"error": error, "result": {"rows": list(rows)}, "attempts": attempts}


def test_retry_on_error():
    assert route_after_execute(make_state(error="no such column", attempts=1)) == "retry"


def test_give_up_after_max_attempts():
    assert route_after_execute(make_state(error="boom", attempts=MAX_ATTEMPTS)) == "give_up"


def test_retry_on_empty_result():
    assert route_after_execute(make_state(rows=[], attempts=1)) == "retry"


def test_answer_on_empty_result_after_max_attempts():
    assert route_after_execute(make_state(rows=[], attempts=MAX_ATTEMPTS)) == "answer"


def test_answer_on_success():
    assert route_after_execute(make_state()) == "answer"