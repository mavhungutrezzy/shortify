def test_404(client):
    response = client.get("/non-existent-page", follow_redirects=False)
    assert response.status_code == 404
    assert (
        b"Sorry, we can't complete your request. Please check your input and try again."
        in response.data
    )
