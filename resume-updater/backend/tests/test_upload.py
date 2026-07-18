def test_upload_invalid_type(test_client):
    response = test_client.post(
        "/api/v1/upload",
        files={"file": ("test.txt", b"dummy content", "text/plain")}
    )
    assert response.status_code == 400
