

def test_layout_template(client):
    response = client.get("/")
    assert b"<title>QUIZHACK!</title>" in response.data