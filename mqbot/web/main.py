import uvicorn
from fastapi import Depends, FastAPI, status, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from mqbot.database import crud
# from mqbot.database.database import get_db


# app = FastAPI(title='mq-bot', description='My bot', version='0.1.0')

from mqbot.database.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        while True:
            yield db
    finally:
        db.close()

db = get_db()
# test = crud.create_test(db=db.__next__(), test_c='1001')
# print(test)


# user = crud.create_user(db=db.__next__(), tg_id=1001)
# print(user)
#
# shopping_list = crud.create_shopping_list(db=db.__next__(), owner_id=1001,
#                                           name='main_list', owner=True)
# print(shopping_list)
# shopping_list2 = crud.create_shopping_list(db=db.__next__(), owner_id=1001,
#                                           name='main_list1', owner=True)
# print(shopping_list2)
#
# print(user.shopping_lists)
# print(shopping_list.users)
# for sl in shopping_list.users:
#     print(sl)

user = crud.get_user(db=db.__next__(), tg_id=1001)
for sh_l in user.shopping_lists:
    print(sh_l)



#
# @app.get('/', tags=['Telegram Healthcheck'])
# @logger.catch(reraise=True, message=TEXT_MESSAGE_ERROR)
# @send_alert_if_exception
# def index():
#     """Telegram Healthcheck."""
#     return Response(status_code=status.HTTP_200_OK)
#
#
# @app.get('/health', tags=['Kubernetes'])
# @logger.catch(reraise=True, message=TEXT_MESSAGE_ERROR)
# @send_alert_if_exception
# def health():
#     """Kubernetes Healthcheck"""
#     return HTMLResponse(content='ОК', status_code=200)
#
#
# @app.delete('/client/{client_id}', tags=['Manual db'])
# @logger.catch(reraise=True, message=TEXT_MESSAGE_ERROR)
# @send_alert_if_exception
# def delete_client(client_id: int, db: Session = Depends(get_db)):
#     delete_client_tickets(db=db, client_id=client_id)
#     crud_delete_client(db=db, client_id=client_id)
#     return HTMLResponse(content='ОК', status_code=200)
#
#
# @app.get('/get_usedesk_host', tags=['Usedesk'])
# @logger.catch(reraise=True, message=TEXT_MESSAGE_ERROR)
# def get_usedesk_host():
#     """Vault Healthcheck"""
#     return HTMLResponse(content=USEDESK_HOST, status_code=200)
#
# if __name__ == '__main__':
#     uvicorn.run('main:app', port=8080, reload=True)
