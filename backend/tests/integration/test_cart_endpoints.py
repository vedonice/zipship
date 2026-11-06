"""Integration tests for Cart API endpoints.

These tests validate the full HTTP flow with real database and service layer.
"""
import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

from src.app import app
from src.models.cart import Cart
from src.models.cart_item import CartItem


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def user_id():
    """Test user ID."""
    return str(uuid4())


@pytest.fixture
def cart_id():
    """Test cart ID."""
    return str(uuid4())


class TestCartEndpoints:
    """Integration tests for cart CRUD operations."""

    def test_create_cart_returns_201(self, client, user_id):
        """POST /carts should create a new cart and return 201."""
        response = client.post(
            "/api/v1/carts",
            headers={"Authorization": f"Bearer {user_id}"},
            json={"user_id": user_id},
        )
        assert response.status_code == 201
        data = response.json()
        assert "data" in data
        assert data["data"]["status"] == "active"
        assert "cart_id" in data["data"]
        assert data["data"]["user_id"] == user_id

    def test_create_cart_requires_auth(self, client):
        """POST /carts without auth should return 401."""
        response = client.post("/api/v1/carts", json={"user_id": str(uuid4())})
        assert response.status_code == 401

    def test_get_cart_by_id_returns_200(self, client, user_id, cart_id):
        """GET /carts/{id} should return cart details."""
        # First create a cart
        create_response = client.post(
            "/api/v1/carts",
            headers={"Authorization": f"Bearer {user_id}"},
            json={"user_id": user_id},
        )
        cart_id = create_response.json()["data"]["cart_id"]

        # Then retrieve it
        response = client.get(
            f"/api/v1/carts/{cart_id}",
            headers={"Authorization": f"Bearer {user_id}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["cart_id"] == cart_id

    def test_get_nonexistent_cart_returns_404(self, client, user_id):
        """GET /carts/{nonexistent_id} should return 404."""
        response = client.get(
            f"/api/v1/carts/{uuid4()}",
            headers={"Authorization": f"Bearer {user_id}"},
        )
        assert response.status_code == 404

    def test_add_item_to_cart_returns_201(self, client, user_id):
        """POST /carts/{id}/items should add item and return 201."""
        # Create cart
        cart_resp = client.post(
            "/api/v1/carts",
            headers={"Authorization": f"Bearer {user_id}"},
            json={"user_id": user_id},
        )
        cart_id = cart_resp.json()["data"]["cart_id"]

        # Add item
        response = client.post(
            f"/api/v1/carts/{cart_id}/items",
            headers={"Authorization": f"Bearer {user_id}"},
            json={
                "product_id": str(uuid4()),
                "product_name": "Test Product",
                "quantity": 2,
                "unit_price": "29.99",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["quantity"] == 2
        assert data["data"]["unit_price"] == "29.99"

    def test_add_item_with_invalid_quantity_returns_400(self, client, user_id):
        """POST /carts/{id}/items with quantity < 1 should return 400."""
        # Create cart
        cart_resp = client.post(
            "/api/v1/carts",
            headers={"Authorization": f"Bearer {user_id}"},
            json={"user_id": user_id},
        )
        cart_id = cart_resp.json()["data"]["cart_id"]

        # Try to add item with invalid quantity
        response = client.post(
            f"/api/v1/carts/{cart_id}/items",
            headers={"Authorization": f"Bearer {user_id}"},
            json={
                "product_id": str(uuid4()),
                "product_name": "Test Product",
                "quantity": 0,  # Invalid: must be 1-999
                "unit_price": "29.99",
            },
        )
        assert response.status_code == 400

    def test_update_item_quantity_returns_200(self, client, user_id):
        """PUT /carts/{id}/items/{item_id} should update quantity."""
        # Create cart and add item
        cart_resp = client.post(
            "/api/v1/carts",
            headers={"Authorization": f"Bearer {user_id}"},
            json={"user_id": user_id},
        )
        cart_id = cart_resp.json()["data"]["cart_id"]

        add_resp = client.post(
            f"/api/v1/carts/{cart_id}/items",
            headers={"Authorization": f"Bearer {user_id}"},
            json={
                "product_id": str(uuid4()),
                "product_name": "Test Product",
                "quantity": 2,
                "unit_price": "29.99",
            },
        )
        item_id = add_resp.json()["data"]["cart_item_id"]

        # Update quantity
        response = client.put(
            f"/api/v1/carts/{cart_id}/items/{item_id}",
            headers={"Authorization": f"Bearer {user_id}"},
            json={"quantity": 5},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["quantity"] == 5

    def test_remove_item_from_cart_returns_204(self, client, user_id):
        """DELETE /carts/{id}/items/{item_id} should remove item."""
        # Create cart and add item
        cart_resp = client.post(
            "/api/v1/carts",
            headers={"Authorization": f"Bearer {user_id}"},
            json={"user_id": user_id},
        )
        cart_id = cart_resp.json()["data"]["cart_id"]

        add_resp = client.post(
            f"/api/v1/carts/{cart_id}/items",
            headers={"Authorization": f"Bearer {user_id}"},
            json={
                "product_id": str(uuid4()),
                "product_name": "Test Product",
                "quantity": 1,
                "unit_price": "29.99",
            },
        )
        item_id = add_resp.json()["data"]["cart_item_id"]

        # Delete item
        response = client.delete(
            f"/api/v1/carts/{cart_id}/items/{item_id}",
            headers={"Authorization": f"Bearer {user_id}"},
        )
        assert response.status_code == 204

    def test_list_user_carts_returns_200(self, client, user_id):
        """GET /carts should list all carts for user."""
        # Create a cart
        client.post(
            "/api/v1/carts",
            headers={"Authorization": f"Bearer {user_id}"},
            json={"user_id": user_id},
        )

        # List carts
        response = client.get(
            "/api/v1/carts",
            headers={"Authorization": f"Bearer {user_id}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

    def test_unauthorized_user_cannot_access_other_cart(self, client):
        """User should not access another user's cart."""
        user1 = str(uuid4())
        user2 = str(uuid4())

        # User1 creates cart
        cart_resp = client.post(
            "/api/v1/carts",
            headers={"Authorization": f"Bearer {user1}"},
            json={"user_id": user1},
        )
        cart_id = cart_resp.json()["data"]["cart_id"]

        # User2 tries to access it
        response = client.get(
            f"/api/v1/carts/{cart_id}",
            headers={"Authorization": f"Bearer {user2}"},
        )
        assert response.status_code == 403  # Forbidden

    def test_cart_response_includes_items_list(self, client, user_id):
        """GET /carts/{id} should include items array."""
        cart_resp = client.post(
            "/api/v1/carts",
            headers={"Authorization": f"Bearer {user_id}"},
            json={"user_id": user_id},
        )
        cart_id = cart_resp.json()["data"]["cart_id"]

        response = client.get(
            f"/api/v1/carts/{cart_id}",
            headers={"Authorization": f"Bearer {user_id}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data["data"]
        assert isinstance(data["data"]["items"], list)
