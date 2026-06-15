from fastapi.testclient import TestClient

from app.db import init_db
from app.main import app


init_db()
client = TestClient(app)


def test_session_turn_report_export_flow():
    created = client.post("/sessions", json={"title": "Test"}).json()
    session_id = created["id"]

    turn = client.post(
        f"/sessions/{session_id}/turns",
        json={"raw_input": "quiero llevarlo a codigo sin perder contrato"},
    ).json()

    assert turn["response_plan"]
    assert turn["report"]
    assert "answer" in turn

    narrative = client.get(f"/sessions/{session_id}/narrative").json()
    assert narrative["objective"]
    assert "central_objects" in narrative

    report = client.get(f"/turns/{turn['id']}/report").json()
    assert report["answer_given"] == turn["answer"]

    exported = client.get(f"/sessions/{session_id}/export").json()
    assert exported["turns"]
    assert "object_graph" in exported


def test_tests_endpoint():
    result = client.post("/tests/run").json()
    assert result["total"] >= 25
    assert result["passed"] / result["total"] >= 0.8
