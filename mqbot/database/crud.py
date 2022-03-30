from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
import re

from . import models, schemas


def create_user(db: Session, tg_id: int, username: str) -> schemas.User:
    db_shopping_list = models.ShoppingList(products='')
    db.add(db_shopping_list)
    db.flush()
    db_user = models.User(tg_id=tg_id, current_shopping_list_id=db_shopping_list.id,
                          username=username)
    db.add(db_user)
    db_user_shopping_list = models.UserShoppingList(
        user_id=tg_id, shopping_list_id=db_shopping_list.id,
        shopping_list_name='Main', owner=True)
    db.add(db_user_shopping_list)
    db.commit()
    return db_user


def get_user(db: Session, tg_id: int) -> schemas.User:
    try:
        user = db.query(models.User).filter(models.User.tg_id == tg_id).one()
    except NoResultFound:
        user = None
    return user


def change_current_shopping_list(db: Session, user_id: int, shopping_list_id: int):
    user = get_user(db, user_id)
    user.current_shopping_list_id = shopping_list_id
    db.add(user)
    db.commit()
    return True


def delete_shopping_list(db: Session, user_id: int, shopping_list_id: int):
    user = get_user(db, user_id)
    if user.current_shopping_list_id == shopping_list_id:
        return False
    shopping_list_in_assoc_table = db.query(models.UserShoppingList).filter(
        models.UserShoppingList.shopping_list_id ==
        shopping_list_id, models.UserShoppingList.user_id == user_id).one()

    if shopping_list_in_assoc_table.owner == False:
        db.delete(shopping_list_in_assoc_table)
        db.commit()
        return True

    shopping_list = db.query(models.ShoppingList).filter(models.ShoppingList.id ==
                                                         shopping_list_id).one()
    associations = shopping_list.users
    for assoc in associations:
        db.delete(assoc)
    db.delete(shopping_list)
    db.commit()
    return True


def create_shopping_list(db: Session, user_id: int, name: str) -> str:
    db_shopping_list = models.ShoppingList(products='')
    db.add(db_shopping_list)
    db.flush()

    db_user = db.query(models.User).filter(models.User.tg_id == user_id).one()
    db_user.current_shopping_list_id = db_shopping_list.id
    db.add(db_user)

    db_user_shopping_list = models.UserShoppingList(
        user_id=user_id, shopping_list_id=db_shopping_list.id,
        shopping_list_name=name, owner=True)
    db.add(db_user_shopping_list)
    db.commit()
    return db_user_shopping_list.shopping_list_name


def get_shopping_list(db: Session, user_id: int, shopping_list_id: int) \
        -> [models.UserShoppingList, None]:
    try:
        shopping_list = db.query(models.UserShoppingList).filter(
            models.UserShoppingList.shopping_list_id ==
            shopping_list_id, models.UserShoppingList.user_id == user_id).one()
    except NoResultFound:
        return None
    return shopping_list


def get_shopping_list_attached_users(db: Session, shopping_list_id: int) \
        -> [models.UserShoppingList, None]:
    try:
        shopping_list_additional_users = db.query(models.UserShoppingList).filter(
            models.UserShoppingList.shopping_list_id ==
            shopping_list_id, models.UserShoppingList.owner == False).all()
    except NoResultFound:
        return None
    return shopping_list_additional_users


def join_user_to_shopping_list(db: Session, user_id: int, shopping_list_id: int, name: str):
    db_user_shopping_list = models.UserShoppingList(
        user_id=user_id, shopping_list_id=shopping_list_id,
        shopping_list_name=name, owner=False)
    db.add(db_user_shopping_list)
    db.commit()
    return True


def detach_user_from_shopping_list(db: Session, shopping_list_id: int, detach_user_id: id):
    user_shopping_list = db.query(models.UserShoppingList).filter(
        models.UserShoppingList.shopping_list_id ==
        shopping_list_id, models.UserShoppingList.user_id == detach_user_id).one()
    db.delete(user_shopping_list)
    db.commit()
    return True


def update_products(db: Session, shopping_list: models.ShoppingList, item: str):
    sl_list = [] if not shopping_list.products else shopping_list.products.split(",")
    status = 'Added'
    if re.match(r"^\d", item):
        try:
            sl_list.pop((int(item)-1))
            status = 'Deleted'
        except IndexError:
            return False
    else:
        sl_list.append(item)
    new_products = ','.join(sl_list)
    shopping_list.products = new_products
    db.add(shopping_list)
    db.commit()
    return status

