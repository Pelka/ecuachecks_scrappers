# from fastapi.testclient import TestClient
# from app.main import app

# client = TestClient(app)

# def test_read_main():
#     response = client.get("/")
#     assert response.status_code == 200
#     assert response.json() == {"message": "Welcome to my API"}

# def test_auth_route():
#     response = client.get("/auth")
#     assert response.status_code == 200
#     # Add more assertions based on your auth route

# def test_external_api_route():
#     response = client.get("/external-api")
#     assert response.status_code == 200
#     # Add more assertions based on your external api route
