from project.app import app

def test_index():
    client = app.test_client()
    resp = client.get("/", content_type="html/text")
    assert resp.status_code == 200
    assert resp.data == b"Hello, World!"