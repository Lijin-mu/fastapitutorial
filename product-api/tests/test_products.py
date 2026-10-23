from app.models import Product, User
from sqlalchemy import select

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Product API is running"}


def test_create_product(client, auth_headers):
    response = client.post(
        "/products",
        json={
            "name": "Notebook",
            "price": 120,
            "description": "A ruled notebook",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Notebook"
    assert data["price"] == 120
    assert data["description"] == "A ruled notebook"
    assert isinstance(data["id"], int)



def test_list_products(client, auth_headers):
    client.post(
        "/products",
        json={
            "name": "Notebook",
            "price": 120,
            "description": "Ruled pages",
        },
        headers=auth_headers,
    )

    response = client.get("/products")
    data = response.json()

    assert response.status_code == 200
    assert len(data["items"]) == 1
    assert data["total"] == 1
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_pages"] == 1
    assert data["items"][0]["name"] == "Notebook"



def test_update_product(client, auth_headers):
    created = client.post(
        "/products",
        json={"name": "Notebook", "price": 120},
        headers=auth_headers,
    )
    assert created.status_code == 201

    product_id = created.json()["id"]

    response = client.patch(
        f"/products/{product_id}",
        json={"description": "Updated description"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["description"] == "Updated description"


def test_get_missing_product(client):
    response = client.get("/products/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_reject_invalid_price(client, auth_headers):
    response = client.post(
        "/products",
        json={"name": "Notebook", "price": -10},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_delete_product(client, auth_headers):
    created = client.post(
        "/products",
        json={"name": "Notebook", "price": 120},
        headers=auth_headers,
    )
    assert created.status_code == 201

    product_id = created.json()["id"]

    response = client.delete(
        f"/products/{product_id}",
        headers=auth_headers,
    )

    assert response.status_code == 204

    check = client.get(f"/products/{product_id}")
    assert check.status_code == 404


def test_create_product_without_token_returns_401(client):
    response = client.post(
        "/products",
        json={"name": "Notebook", "price": 120},
    )

    assert response.status_code == 401



def test_create_product_assigns_owner(client, auth_headers, db_session):

    response = client.post(
        "/products",
        json={"name": "My Notebook", "price": 120},
        headers=auth_headers,
    )

    assert response.status_code == 201
    product_id = response.json()["id"]

    product = db_session.get(Product, product_id)
    user = db_session.scalar(
        select(User).where(User.email == "testuser@example.com")
    )

    assert product is not None
    assert user is not None
    assert product.owner_id == user.id




def test_owner_can_update_product(client, auth_headers):
    created = client.post(
        "/products",
        json={"name": "Notebook", "price": 120},
        headers=auth_headers,
    )
    assert created.status_code == 201

    product_id = created.json()["id"]

    response = client.patch(
        f"/products/{product_id}",
        json={"price": 150},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["price"] == 150


def test_owner_can_delete_product(client, auth_headers):
    created = client.post(
        "/products",
        json={"name": "Notebook", "price": 120},
        headers=auth_headers,
    )
    assert created.status_code == 201

    product_id = created.json()["id"]

    response = client.delete(
        f"/products/{product_id}",
        headers=auth_headers,
    )

    assert response.status_code in (200, 204)

    get_response = client.get(f"/products/{product_id}")
    assert get_response.status_code == 404


def register_and_login(client, email):
    credentials = {
        "email": email,
        "password": "TestPassword123!",
    }

    register_response = client.post("/auth/register", json=credentials)
    assert register_response.status_code == 201

    login_response = client.post("/auth/login", json=credentials)
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_other_user_cannot_update_product(client, auth_headers):
    created = client.post(
        "/products",
        json={"name": "Private Notebook", "price": 120},
        headers=auth_headers,
    )
    assert created.status_code == 201

    product_id = created.json()["id"]
    another_user_headers = register_and_login(
        client, "anotheruser@example.com"
    )

    response = client.patch(
        f"/products/{product_id}",
        json={"price": 1},
        headers=another_user_headers,
    )

    assert response.status_code == 403


def test_other_user_cannot_delete_product(client, auth_headers):
    created = client.post(
        "/products",
        json={"name": "Private Notebook", "price": 120},
        headers=auth_headers,
    )
    assert created.status_code == 201

    product_id = created.json()["id"]
    another_user_headers = register_and_login(
        client, "anotheruser@example.com"
    )

    response = client.delete(
        f"/products/{product_id}",
        headers=another_user_headers,
    )

    assert response.status_code == 403

    # Verify the product still exists after the rejected deletion.
    check = client.get(f"/products/{product_id}")
    assert check.status_code == 200


def test_product_pagination(client, auth_headers):
    for i in range(5):
        response = client.post(
            "/products",
            json={"name": f"Product {i}", "price": 100 + i},
            headers=auth_headers,
        )
        assert response.status_code == 201

    response = client.get("/products?page=1&page_size=2")

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total_pages"] == 3



def test_product_search(client, auth_headers):
    for name in ["Notebook", "Laptop", "Notebook Stand"]:
        response = client.post(
            "/products",
            json={"name": name, "price": 100},
            headers=auth_headers,
        )
        assert response.status_code == 201

    response = client.get("/products?search=notebook")

    assert response.status_code == 200

    data = response.json()
    names = [product["name"] for product in data["items"]]

    assert names == ["Notebook", "Notebook Stand"]
    assert data["total"] == 2


def test_product_price_filter(client, auth_headers):
    for name, price in [
        ("Pen", 20),
        ("Notebook", 120),
        ("Laptop", 50000),
    ]:
        response = client.post(
            "/products",
            json={"name": name, "price": price},
            headers=auth_headers,
        )
        assert response.status_code == 201

    response = client.get("/products?min_price=50&max_price=500")

    assert response.status_code == 200

    data = response.json()
    products = data["items"]

    assert len(products) == 1
    assert data["total"] == 1
    assert products[0]["name"] == "Notebook"
    assert products[0]["price"] == 120


def test_product_sorting_by_price_ascending(client, auth_headers):
    for name, price in [
        ("Laptop", 50000),
        ("Pen", 20),
        ("Notebook", 120),
    ]:
        response = client.post(
            "/products",
            json={"name": name, "price": price},
            headers=auth_headers,
        )
        assert response.status_code == 201

    response = client.get("/products?sort_by=price&order=asc")

    assert response.status_code == 200

    products = response.json()["items"]
    prices = [product["price"] for product in products]

    assert prices == [20, 120, 50000]



def test_product_pagination_metadata(client, auth_headers):
    for i in range(5):
        response = client.post(
            "/products",
            json={"name": f"Product {i + 1}", "price": (i + 1) * 10},
            headers=auth_headers,
        )
        assert response.status_code == 201

    response = client.get("/products?page=2&page_size=2")

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["page"] == 2
    assert data["page_size"] == 2
    assert data["total_pages"] == 3



def test_product_search_returns_empty_items_when_no_match(
    client, auth_headers
):
    response = client.get("/products?search=does-not-exist")

    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["total_pages"] == 0


def test_product_page_beyond_last_page_returns_empty_items(
    client, auth_headers
):
    client.post(
        "/products",
        json={"name": "Notebook", "price": 120},
        headers=auth_headers,
    )

    response = client.get("/products?page=10&page_size=10")

    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 1
    assert data["page"] == 10
    assert data["total_pages"] == 1


def test_product_list_rejects_invalid_sort_field(client):
    response = client.get("/products?sort_by=unknown")

    assert response.status_code == 422


def test_product_list_rejects_invalid_sort_order(client):
    response = client.get("/products?order=random")

    assert response.status_code == 422


def test_product_list_rejects_zero_page(client):
    response = client.get("/products?page=0")

    assert response.status_code == 422


def test_product_list_rejects_page_size_above_limit(client):
    response = client.get("/products?page_size=101")

    assert response.status_code == 422


def test_product_list_rejects_negative_min_price(client):
    response = client.get("/products?min_price=-1")

    assert response.status_code == 422



def test_product_list_rejects_conflicting_price_filters(client):
    response = client.get("/products?min_price=500&max_price=100")

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "min_price cannot be greater than max_price"
    )
