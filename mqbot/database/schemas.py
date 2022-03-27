from datetime import datetime
from typing import List

from pydantic import BaseModel


# class UserCreate(BaseModel):
#     tg_id: int


class User(BaseModel):
    tg_id: int
    current_shopping_list_id: int
    shopping_lists: list

    class Config:
        orm_mode = True


# class ShoppingListCreate(BaseModel):
#     owner_id: int


class ShoppingList(BaseModel):
    id: int
    products: str
    owner_id: int
    users: list

    class Config:
        orm_mode = True


class UserShoppingListCreate(BaseModel):
    user_tg_id = int
    shopping_list_id = int
    shopping_list_name: str
    owner: bool


class UsersShoppingList(UserShoppingListCreate):
    user: User
    shopping_list: ShoppingList

    class Config:
        orm_mode = True




