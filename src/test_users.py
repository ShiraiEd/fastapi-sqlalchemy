# signup
from urllib import response


def test_signup(client):
    response = client.post("/signup/", json={"name": "John", "email": "john@test.com", "password": "senha123"})

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "john@test.com"
    assert "password" not in data

def test_signup_no_name_failure(client):
    response = client.post("/signup/", json={"email": "john@test.com", "password": "senha123"})
    assert response.status_code==422

def test_signup_no_email_failure(client):
    response = client.post("/signup/", json={"name": "John", "password": "senha123"})
    assert response.status_code == 422

def test_signup_no_password_failure(client):
    response = client.post("/signup/", json={"name": "John", "email": "john@test.com"})
    assert response.status_code == 422


# login
def test_login_wrong_password(client):
    client.post("/signup/", json={"name": "John", "email": "john@test.com", "password": "senha123"})
    response = client.post("/login/", json = {"email": "john@test.com", "password": "senhaerrada"})
    assert response.status_code==400

def test_login_wrong_email(client):
    client.post("/signup/", json={"name": "John", "email": "john@test.com", "password": "senha123"})
    response = client.post("/login/", json = {"email": "wrong@test.com", "password": "senha123"})
    assert response.status_code==404

def test_login_success(client):
    client.post("/signup", json={"name": "John", "email": "john@test.com", "password": "senha123"})
    response = client.post("/login/", json={"email": "john@test.com", "password": "senha123"})
    assert response.status_code==200

def test_user_not_found(client):
    client.post("/signup/", json={"name": "John", "email": "john@test.com", "password": "senha123"})
    response1 = client.get("/users/1")
    response2 = client.get("/users/2")

    assert response1.status_code==200
    assert response2.status_code==404


# change password
def test_change_password_wrong_password(client):
    client.post("/signup/", json={"name": "John", "email": "john@test.com", "password": "senha123"})
    response = client.patch("/update_password/1", json={"old_password": "aaa", "new_password": "aaa"})
    assert response.status_code==400

def test_change_password_equal_old_password(client):
    client.post("/signup/", json={"name": "John", "email": "john@test.com", "password": "senha123"})
    response = client.patch("/update_password/1", json={"old_password": "senha123", "new_password": "senha123"})
    assert response.status_code==400

def test_change_password_success(client):
    client.post("/signup/", json={"name": "John", "email": "john@test.com", "password": "senha123"})
    response = client.patch("/update_password/1", json={"old_password": "senha123", "new_password": "123"})
    assert response.status_code==200


# update user
def test_change_user_email_and_name_already_exists_failure(client):
    client.post("/signup/", json={"name": "John", "email": "john@test.com", "password": "senha123"})
    response = client.patch("/users/1", json={"name": "John", "email": "john@test.com"})
    assert response.status_code==400

def test_change_user_name_success(client):
    client.post("/signup/", json={"name": "John", "email": "john@test.com", "password": "senha123"})
    response = client.patch("users/1", json={"name": "Josh"})
    data = response.json()
    assert data["name"] == "Josh"
    assert response.status_code==200

def test_change_user_email_success(client):
    client.post("/signup/", json={"name": "John", "email": "john@test.com", "password": "senha123"})
    response = client.patch("users/1", json={"email": "josh@test.com"})
    data = response.json()
    assert data["email"] == "josh@test.com"
    assert response.status_code == 200

# delete user
def test_delete_user_success(client):
    client.post("/signup/", json={"name": "John", "email": "john@test.com", "password": "senha123"})
    response=client.delete("/users/1")
    assert response.status_code==204