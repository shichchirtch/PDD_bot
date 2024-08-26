from aiogram.types import CallbackQuery, Message
from aiogram.filters import BaseFilter
from python_db import users_db


class PRE_START(BaseFilter):
    async def __call__(self, message: Message):
        if message.from_user.id not in users_db:
            return True
        return False


class ABC_FILTER(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        if callback.data in ('🟢', '🔴', '🟡'):
            return True
        return False


class SEND_FILTER(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        # print('callback.data2 = ', callback.data)
        if callback.data == 'ОТПРАВИТЬ':
            return True
        return False

class NEXT_FILTER(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        # print('callback.data = ', callback.data)
        if callback.data == 'Следующий':
            return True
        return False

class TICKET_NUMBER_LIST(BaseFilter):
    async def __call__(self, message: Message):
        if message.text.isdigit() and int(message.text) < 31:
            return True
        return False

class NEXT_IN_LIST_FILTER(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        # print('callback.data = ', callback.data)
        if callback.data == 'Folgend':
            return True
        return False

class MORE_30_FILTER(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        # print('callback.data = ', callback.data)
        if callback.data == 'Следующий':
            if users_db[callback.from_user.id]['current_tic_number']==30:
                return True
            return False
        return False

class ZERO_FILTER(BaseFilter):
    async def __call__(self, message: Message):
        if users_db[message.from_user.id]['current_tic_number']==0:
            return True
        return False

class VYBRATb_BILET_FILTER(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        if callback.data == 'Выбрать':
            return True
        return False

class NEW_BILET_FILTER(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        if callback.data == 'Билет':
            return True
        return False

class RESET_FILTER(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        if callback.data == 'Сбросить':
            return True
        return False

class IS_DIGIT(BaseFilter):
    async def __call__(self, message: Message):
        if message.text.isdigit() and int(message.text) < 11:
            return True
        return False

class IS_TIME(BaseFilter):
    async def __call__(self, message: Message):
        work_str = message.text.strip()
        if ':' in work_str:
            arr_str = work_str.split(':')
            if len(arr_str)==2:
                h = arr_str[0]
                m = arr_str[1]
                if -1< int(h)<24 and -1 < int(m)<60:
                    return True
        return False

class TZ_FILTER(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        if callback.data in ('0', '1', '2','3', '4', '5', '6'):
            return True
        return False