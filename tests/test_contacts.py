from unittest import TestCase
from fastapi.testclient import TestClient
from main import app

class TestContacts(TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_get_contacts(self):
        response = self.client.get("/contacts")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)

    def test_create_contact(self):
        contact = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@example.com",
            "phone_number": "1234567890",
            "birthday": "1990-01-01"
        }
        response = self.client.post("/contacts", json=contact)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["first_name"], "John")

    def test_get_contact(self):
        contact = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@example.com",
            "phone_number": "1234567890",
            "birthday": "1990-01-01"
        }
        self.client.post("/contacts", json=contact)
        response = self.client.get("/contacts/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["first_name"], "John")

    def test_update_contact(self):
        contact = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@example.com",
            "phone_number": "1234567890",
            "birthday": "1990-01-01"
        }
        self.client.post("/contacts", json=contact)
        updated_contact = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "janedoe@example.com",
            "phone_number": "9876543210",
            "birthday": "1990-01-01"
        }
        response = self.client.put("/contacts/1", json=updated_contact)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["first_name"], "Jane")

    def test_delete_contact(self):
        contact = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@example.com",
            "phone_number": "1234567890",
            "birthday": "1990-01-01"
        }
        self.client.post("/contacts", json=contact)
        response = self.client.delete("/contacts/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Contact deleted"})