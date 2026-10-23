
from pydantic import BaseModel, ConfigDict, Field

from pydantic import EmailStr


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    price: float = Field(gt=0)
    description: str | None = Field(default=None, max_length=500)

class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    price: float | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, max_length=500)


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)

class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
