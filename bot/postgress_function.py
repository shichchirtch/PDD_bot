from postgress_table import session_marker, User
from sqlalchemy import select, func
import translators

async def insert_new_user_in_table(user_tg_id: int, name: str):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        if not needed_data:
            # print('Now we are into first function')
            new_us = User(tg_us_id=user_tg_id, user_name=name)
            session.add(new_us)
            await session.commit()


async def check_user_in_table(user_tg_id:int):
    """Функция проверяет есть ли юзер в БД"""
    async with session_marker() as session:
        # print("Work check_user Function")
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        data = query.one_or_none()
        return data

async def insert_new_ticket(user_tg_id: int, ticket:list):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        # print('works insert_new_ticket')
        needed_data.frage_list = ticket
        await session.commit()

async def total_increment(user_tg_id: int):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        # print('works insert_stars')
        needed_data.total += 1
        await session.commit()

async def reset_ticket_list(user_tg_id:int):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        needed_data.frage_list = []
        await session.commit()

async def return_ticket_list(user_tg_id:int):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        return needed_data.frage_list

async def get_user_count():
    async with session_marker() as session:
        result = await session.execute(select(func.count(User.index)))
        count = result.scalar()
        return count


async def return_total(user_tg_id:int):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        return needed_data.total


async def translates(slovo:str, lan:str)->str:
    if lan == 'fa':
        try:
            res = translators.translate_text(query_text=slovo, from_language='ru', to_language='fa', translator='bing')
        except AttributeError:
                print('\n\n произошла ошибка AttributeError')
                res = 'خطای ترجمه AttributeError'

    else:
        res = slovo
    return res


