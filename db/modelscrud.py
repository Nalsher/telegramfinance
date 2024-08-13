from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.table import user,quest
from users.keys import generate_random_string
async def user_add(sessia:AsyncSession,telegram_id:str,linktg:str,chat_id:int):
    async with sessia() as sess:
        secret = await generate_random_string(length=6,key=telegram_id)
        new_us = user(id=telegram_id,link=linktg,chat_id=chat_id,secret_code=secret)
        sess.add(new_us)
        text = telegram_id + '   ' + secret
        await sess.commit()
        return text
async def user_get_quest(sessia:AsyncSession,secret_key:str):
    async with sessia() as sess:
        user_query = select(user.id).where(user.secret_code==secret_key)
        user_return = await sess.execute(user_query)
        us_id = user_return.scalar_one()
        questions = select(quest).where(quest.userto==us_id)
        quest_return = await sess.execute(questions)
        quests = quest_return.scalars()
        res = quests.fetchall()
        final = ''
        for i in res:
            print(i.text,i.userfrom)
            final += i.text + '---SEND BY :' +  '@'+i.userfrom + '\n'
        return final

async def chat_get(sessia:AsyncSession,id:str):
    async with sessia() as sess:
        query = select(user.chat_id).where(user.id==id)
        result = await sess.execute(query)
        obj = result.scalar_one()
        return obj

async def id_get(sessia:AsyncSession,id:str):
    async with sessia() as sess:
        query = select(user.id).where(user.chat_id==int(id))
        result = await sess.execute(query)
        obj = result.scalar_one()
        return obj

async def quest_add(sessia:AsyncSession,text:str,userfrom:str,userto:str):
    async with sessia() as sess:
        new_quest = quest(text=text,userfrom=userfrom,userto=userto)
        sess.add(new_quest)
        return await sess.commit()

