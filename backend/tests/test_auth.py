def test_register(client):
    response = client.post(
        "/auth/register",
        data={
            "username": "test",
            "email": "test@gmail.com",
            "password": "test",
            "confirm_password": "test"
        })

    assert response.status_code == 200