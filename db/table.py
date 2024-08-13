from sqlalchemy import Column, BigInteger, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy import String
from sqlalchemy import ForeignKey,ARRAY
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from db.conf import engine
from sqlalchemy_utils import database_exists
from sqlalchemy import UniqueConstraint


Base = declarative_base()

class user(Base):
    __tablename__ = 'user'
    id = Column(String,primary_key=True)
    link = Column(String)
    chat_id = Column(BigInteger)
    secret_code = Column(String)

class quest(Base):
    __tablename__ = 'quest'
    id = Column(Integer,primary_key=True)
    text = Column(String,nullable=True)
    userfrom = Column(ForeignKey("user.id"))
    userto = Column(ForeignKey("user.id"))

sessionmaker = async_sessionmaker(engine,expire_on_commit=True)

async def create():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except:
        print(Exception)
        print('NOT CREATED ATEMPTIONIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII')
