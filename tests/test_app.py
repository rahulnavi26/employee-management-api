
import pytest

from app import app, employees


# Configure the Flask application for testing

# Configure the Flask application for testing
@pytest.fixture
def client():

    # Reset employee data before every test
    employees.clear()

    employees.extend([
        {
            "id": 1,
            "name": "Rahul",
            "department": "DevOps",
            "email": "rahul@example.com"
        },
        {
            "id": 2,
            "name": "Arun",
            "department": "Development",
            "email": "arun@example.com"
        }
    ])

    # Save original testing configuration
    original_testing = app.config.get("TESTING", False)

    # Enable testing mode
    app.config["TESTING"] = True

    # Create Flask test client
    with app.test_client() as client:
        yield client

    # Restore original configuration
    app.config["TESTING"] = original_testing


# Test GET API - Retrieve all employees
def test_get_employees(client):

    response = client.get("/api/employees")

    assert response.status_code == 200

    data = response.get_json()

    assert data["count"] == 2
    assert len(data["employees"]) == 2
    assert data["employees"][0]["name"] == "Rahul"
    assert data["employees"][1]["name"] == "Arun"


# Test POST API - Create a new employee
def test_create_employee(client):

    response = client.post(
        "/api/employees",
        json={
            "name": "Kiran",
            "department": "DevOps",
            "email": "kiran@example.com"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Employee created successfully"
    assert data["employee"]["name"] == "Kiran"
    assert data["employee"]["department"] == "DevOps"
    assert data["employee"]["email"] == "kiran@example.com"

# Test POST API - Reject duplicate email
def test_create_employee_duplicate_email(client):

    response = client.post(
        "/api/employees",
        json={
            "name": "Another Rahul",
            "department": "Testing",
            "email": "rahul@example.com"
        }
    )

    assert response.status_code == 409

    data = response.get_json()

    assert data["error"] == "Employee email already exists"

# Test PUT API - Update an employee
def test_update_employee(client):

    response = client.put(
        "/api/employees/2",
        json={
            "name": "Arun Kumar",
            "department": "DevOps",
            "email": "arun@example.com"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Employee updated successfully"
    assert data["employee"]["id"] == 2
    assert data["employee"]["name"] == "Arun Kumar"
    assert data["employee"]["department"] == "DevOps"

# Test DELETE API - Delete an employee
def test_delete_employee(client):

    response = client.delete("/api/employees/2")

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Employee deleted successfully"
    assert data["employee"]["id"] == 2
    assert data["employee"]["name"] == "Arun"

    # Verify that employee is actually deleted
    get_response = client.get("/api/employees")

    employees_data = get_response.get_json()

    assert employees_data["count"] == 1
    assert len(employees_data["employees"]) == 1

# Test PUT API - Employee not found
def test_update_employee_not_found(client):

    response = client.put(
        "/api/employees/99",
        json={
            "name": "Suresh",
            "department": "Testing",
            "email": "suresh@example.com"
        }
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Employee not found"

# Test DELETE API - Employee not found
def test_delete_employee_not_found(client):

    response = client.delete("/api/employees/99")

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Employee not found"

# Test POST API - Missing required field
def test_create_employee_missing_email(client):

    response = client.post(
        "/api/employees",
        json={
            "name": "Suresh",
            "department": "Testing"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == (
        "email is required and must be a non-empty string"
    )

# Test POST API - Empty email validation
def test_create_employee_empty_email(client):

    response = client.post(
        "/api/employees",
        json={
            "name": "Suresh",
            "department": "Testing",
            "email": "   "
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == (
        "email is required and must be a non-empty string"
    )

# Test POST API - Invalid JSON
def test_create_employee_invalid_json(client):

    response = client.post(
        "/api/employees",
        data='{"name": "Suresh", "department": "Testing",',
        content_type="application/json"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Request body must contain valid JSON"