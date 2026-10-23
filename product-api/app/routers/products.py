
from typing import Annotated

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Product, User
from app.schemas import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


# Protected: valid login token required
@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    product_data: ProductCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    product = Product(
        **product_data.model_dump(),
        owner_id=current_user.id,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


# Public: no token required
@router.get("", response_model=ProductListResponse)
def get_products(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    search: str | None = None,
    min_price: Annotated[float | None, Query(ge=0)] = None,
    max_price: Annotated[float | None, Query(ge=0)] = None,
    sort_by: Annotated[
        str, Query(pattern="^(id|name|price)$")
    ] = "id",
    order: Annotated[
        str, Query(pattern="^(asc|desc)$")
    ] = "asc",
    db: Session = Depends(get_db),
):
    # Validate price range.
    if (
        min_price is not None
        and max_price is not None
        and min_price > max_price
    ):
        raise HTTPException(
            status_code=422,
            detail="min_price cannot be greater than max_price",
        )

    # Build filters once for counting and fetching products.
    filters = []

    if search and search.strip():
        search_term = f"%{search.strip()}%"
        filters.append(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
            )
        )

    if min_price is not None:
        filters.append(Product.price >= min_price)

    if max_price is not None:
        filters.append(Product.price <= max_price)

    # Count matching products before pagination.
    total = db.scalar(
        select(func.count(Product.id)).where(*filters)
    ) or 0

    # Build the product query.
    query = select(Product).where(*filters)

    # Choose an allowed sorting column.
    sort_column = {
        "id": Product.id,
        "name": Product.name,
        "price": Product.price,
    }[sort_by]

    # Apply sorting with a stable tie-breaker.
    if order == "desc":
        query = query.order_by(
            sort_column.desc(),
            Product.id.asc(),
        )
    else:
        query = query.order_by(
            sort_column.asc(),
            Product.id.asc(),
        )

    # Apply pagination.
    offset = (page - 1) * page_size

    items = db.scalars(
        query.offset(offset).limit(page_size)
    ).all()

    # Calculate total pages.
    total_pages = (total + page_size - 1) // page_size

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }






# Public: no token required
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product


# Protected: valid login token required
@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    if product.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own products",
        )

    updates = product_data.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one field to update",
        )

    for field, value in updates.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


# Protected: valid login token required
@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product(
    product_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    if product.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own products",
        )

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}
