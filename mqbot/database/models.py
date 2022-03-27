from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column

from .database import Base


class UserShoppingList(Base):
    __tablename__ = 'users_shopping_list'
    user_id = Column(ForeignKey('users.tg_id'), primary_key=True)
    shopping_list_id = Column(ForeignKey('shopping_list.id'), primary_key=True)
    shopping_list_name = Column(String(50))
    owner = Column(Boolean)

    user = relationship("User", back_populates="shopping_lists")
    shopping_list = relationship("ShoppingList", back_populates="users")

    def __repr__(self):
        return f'<UserShoppingList user_id: {self.user_id}, ' \
               f'Shopping_list_id: {self.shopping_list_id}, ' \
               f'shopping_list_name: {self.shopping_list_name}, ' \
               f'is_user_owner: {self.owner}>'




class User(Base):
    __tablename__ = 'users'

    tg_id = Column(Integer, primary_key=True)
    current_shopping_list_id = Column(Integer)

    shopping_lists = relationship("UserShoppingList", back_populates="user")

    def __repr__(self):
        return f'<User tg_id: {self.tg_id},' \
               f' current_shopping_list_id: ' \
               f'{self.current_shopping_list_id}>'


class ShoppingList(Base):
    __tablename__ = 'shopping_list'

    id = Column(Integer, primary_key=True)
    products = Column(String())

    users = relationship("UserShoppingList")

    def __repr__(self):
        return f'<ShoppingList {self.id}>'
