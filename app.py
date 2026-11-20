
from flask import Flask, jsonify, request

# Create Flask application
app = Flask(__name__)

# Employee data (temporary in-memory storage)
employees = [
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
]


# Get all employees
@app.route("/api/employees", methods=["GET"])
def get_employees():
    return jsonify({
        "count": len(employees),
        "employees": employees
    }), 200


# Create a new employee
@app.route("/api/employees", methods=["POST"])
def create_employee():

    # Read JSON data from client
    data = request.get_json(silent=True)

    # Validate request body
    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must contain valid JSON"
        }), 400

    # Check required fields
    required_fields = ["name", "department", "email"]

    for field in required_fields:
        if not isinstance(data.get(field), str) or not data[field].strip():
            return jsonify({
                "error": f"{field} is required and must be a non-empty string"
            }), 400

    # Check for duplicate email
    if any(emp["email"].lower() == data["email"].strip().lower() for emp in employees):
        return jsonify({
            "error": "Employee email already exists"
        }), 409

    # Generate new employee ID
    new_id = max((emp["id"] for emp in employees), default=0) + 1

    # Create employee record
    new_employee = {
        "id": new_id,
        "name": data["name"].strip(),
        "department": data["department"].strip(),
        "email": data["email"].strip()
    }

    # Store employee
    employees.append(new_employee)

    # Return response
    return jsonify({
        "message": "Employee created successfully",
        "employee": new_employee
    }), 201

# Update an existing employee
@app.route("/api/employees/<int:employee_id>", methods=["PUT"])
def update_employee(employee_id):

    # Find employee using ID
    employee = next(
        (emp for emp in employees if emp["id"] == employee_id),
        None
    )

    # Check whether employee exists
    if employee is None:
        return jsonify({"error": "Employee not found"}), 404

    # Read JSON data
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must contain valid JSON"
        }), 400

    # Validate required fields
    required_fields = ["name", "department", "email"]

    for field in required_fields:
        if not isinstance(data.get(field), str) or not data[field].strip():
            return jsonify({
                "error": f"{field} is required and must be a non-empty string"
            }), 400

    # Check duplicate email
    if any(
        emp["email"].lower() == data["email"].strip().lower()
        and emp["id"] != employee_id
        for emp in employees
    ):
        return jsonify({"error": "Employee email already exists"}), 409

    # Update employee details
    employee["name"] = data["name"].strip()
    employee["department"] = data["department"].strip()
    employee["email"] = data["email"].strip()

    return jsonify({
        "message": "Employee updated successfully",
        "employee": employee
    }), 200

# Delete an employee
@app.route("/api/employees/<int:employee_id>", methods=["DELETE"])

def delete_employee(employee_id):

    # Find employee using ID
    employee = next(
        (emp for emp in employees if emp["id"] == employee_id),
        None
    )

    # Check whether employee exists
    if employee is None:
        return jsonify({"error": "Employee not found"}), 404

    # Delete employee from the list
    employees.remove(employee)

    return jsonify({
        "message": "Employee deleted successfully",
        "employee": employee
    }), 200

# Home API
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "application": "Employee Management API",
        "version": "1.0",
        "message": "Application is running"
    })


# Health Check API
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "application": "Employee Management API"
    }), 200


# Run application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
