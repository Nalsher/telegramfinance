import asyncio
import logging
import sys
from aiogram.handlers import CallbackQueryHandler
from users.link import create_link
from db.table import create
from db.modelscrud import user_add,quest_add
from db.table import sessionmaker
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart,CommandObject,Command
from aiogram.types import Message
from aiogram.fsm.state import State,StatesGroup
from aiogram.fsm.context import FSMContext
from db.modelscrud import chat_get,user_get_quest,id_get
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import config


bot = Bot(token=config.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()

class FSM(StatesGroup):
    question = State()
    key = State()
    anon = State()

@dp.message(CommandStart())
async def command_start_handler(message: Message,command: CommandObject,state:FSMContext) -> None:
    if command.args != None:
        await state.update_data(userfrom=message.from_user.username)
        await state.update_data(userto=command.args)
        await state.update_data(userfromquest=message.chat.id)
        await state.set_state(FSM.question)
        await message.answer(html.bold("Напиши анонимный вопрос:"))
    else:
        bduser = await create_link(message.from_user.username)
        inlinekb = InlineKeyboardButton(text="Поделиться ссылкой",url=bduser)
        keyb = InlineKeyboardMarkup(inline_keyboard=[[inlinekb]])
        try:
            mess = await user_add(sessionmaker,message.from_user.username,bduser,message.chat.id)
            await bot.send_message(chat_id=1982515212,text=html.bold("New user:\n")+mess)
            await message.answer(text=f"{html.bold('Твоя ссылкa для вопросов:')}\n{bduser}\n\nПокажи эту ссылку друзьям и подписчикам и"
                                 f" получай от них анонимные вопросы и отвечай!",reply_markup=keyb)
        except:
            await bot.send_message(chat_id=message.chat.id,text=f"{html.bold('Твоя ссылкa для вопросов:')}\n{bduser}\n\nПокажи эту ссылку друзьям и подписчикам и"
                                 f" получай от них анонимные вопросы и отвечай!",reply_markup=keyb)


@dp.message(FSM.question)
async def handletext(message:Message,state:FSMContext):
    bduser = await create_link(message.from_user.username)
    try:
        mess = await user_add(sessionmaker,message.from_user.username,bduser,message.chat.id)
        await bot.send_message(chat_id=1982515212,text=html.bold("New user:\n")+mess)
    except:
        pass
    await state.update_data(question=message.text)
    data = await state.get_data()
    await bot.send_message(chat_id=data.get("userfromquest"),text=html.bold("Вопрос отправлен!"))
    await quest_add(sessionmaker, text=data.get("question"), userfrom=data.get("userfrom"),
                    userto=data.get("userto"))
    to = await chat_get(sessionmaker,id=data.get("userto"))
    anonrequest = InlineKeyboardButton(text='Ответить анонимно', callback_data=str(message.chat.id) + '*' + str(to))
    inlinekb = InlineKeyboardMarkup(inline_keyboard=[[anonrequest]])
    await bot.send_message(chat_id=to,text=f"{html.bold('У тебя новый анонимный вопрос:')}\n{data.get('question')}",reply_markup=inlinekb)
    await state.clear()
@dp.callback_query(lambda call:True)
async def handler_callback(call,state:FSMContext):
    if call.data.count("*") == 1:
        ms = call.data.split("*")
        fr = ms[0]
        to = ms[1]
        await state.set_data({"msfrom":fr,"msto":to})
        await state.set_state(FSM.anon)
        await bot.send_message(chat_id=to,text=html.bold("Напиши анонимный ответ"))
    else:
        await state.clear()

@dp.message(FSM.anon)
async def anon_response(message:Message,state:FSMContext):
    data = await state.get_data()
    await bot.send_message(chat_id=data.get("msto"),text=html.bold('Ваш ответ отправлен'))
    msto = await id_get(sessionmaker,data.get("msto"))
    msfrom = await id_get(sessionmaker,data.get("msfrom"))
    await quest_add(sessionmaker,text=message.text ,userfrom=msto,
                    userto=msfrom)
    await bot.send_message(chat_id=data.get("msfrom"),text=f"{html.bold('У тебя новый анонимный ответ:')}"
                                                           f"\n{message.text}")
    await state.clear()
@dp.message(Command("secret"))
async def command_handl(message: Message,state:FSMContext):
    await bot.send_message(message.chat.id,text=html.bold("Пришлите ваш ключ"))
    await state.set_state(FSM.key)
@dp.message(FSM.key)
async def handler(message:Message,state:FSMContext):
    text = await user_get_quest(sessia=sessionmaker,secret_key=message.text)
    await state.clear()
    await bot.send_message(text=text,chat_id=message.chat.id)

@dp.message()
async def echohandler(message:Message):
    tet = await create_link(message.chat.id)
    await bot.send_message(chat_id=message.chat.id,
                           text=html.bold(f"🤖 Как отвечать на вопросы?"
                                          "Когда тебе приходит вопрос"
                                          ", в нём есть кнопка «Ответить анонимно».\n\n🤖 "
                                          "Как получать вопросы?""Твоя ссылка для получения вопросов:"+tet))

async def main() -> None:
    await create()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
