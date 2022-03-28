from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func, select
from datetime import date
from sqlalchemy.schema import DropTable
from sqlalchemy.ext.compiler import compiles
import logging
from sqlalchemy import Column, String, Integer, Date, Table, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref
from random import choice


def_logger = logging.getLogger(__name__)
def_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler = logging.FileHandler("log.txt")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
def zerocut(record): # filters battle's draw
    if record.msg[-1] != "0":
        return True
logfilter = logging.Filter()
logfilter.filter = zerocut

def_logger.addFilter(logfilter)
def_logger.addHandler(file_handler)
def_logger.addHandler(stream_handler)

def_logger.debug("app.py starts")
@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"

db_name = 'database'
db_user = 'username'
db_pass = 'secret'
db_host = 'db'
db_port = '5432'

# Settings as shown in docker-compose.yml
engine = create_engine('postgresql+psycopg2://{}:{}@{}:{}/{}'.format(db_user, db_pass, db_host, db_port, db_name))
def_logger.info("Connection with database is established")
Session = sessionmaker(bind=engine)
Base = declarative_base()

battle_hero = Table('battle_hero_association', Base.metadata,
    Column('battle_id', ForeignKey('battles.id')),
    Column('hero_id', ForeignKey('heroes.id')))

class Hero(Base):
    __tablename__ = 'heroes'
    id = Column(Integer, primary_key = True)
    side = Column('side', String)
    name = Column('name', String)
    birthday = Column('birthday', Date)
    magic = Column('magic', Boolean)
    power = Column('power', Integer)
    moto = relationship("Heroes_moto", cascade="delete")
    heroes_histories = relationship('Heroes_history',back_populates="heroes",uselist=False, cascade="delete")
    battles = relationship("Battle",
                        secondary = battle_hero
                        )
    
    def __init__(self, side, name, birthday, magic, power):
        self.side = side
        self.name = name
        self.birthday = birthday
        self.magic = magic
        self.power = power
    
    def __str__(self):
        return f"ID: {self.id} | Name: {self.name} | Side: {self.side} | Power: {self.power}"
    
class Heroes_moto(Base):
    __tablename__ = 'heroes_motos'
    id = Column(Integer, primary_key = True)
    hero_id = Column('hero_id', Integer, ForeignKey('heroes.id',ondelete="CASCADE"))
    moto_id = Column('moto_id', Integer)
    moto = Column('moto', String)
    
    def __init__(self, hero_id, moto):
        if not(session.query(Hero).filter(Hero.id == hero_id).count()):
            raise NameError("hero_id doesnt exist")
        self.hero_id = hero_id
        self.moto_id = session.query(Heroes_moto).filter(Heroes_moto.hero_id == hero_id).count() + 1
        self.moto = moto
        
    def __str__(self):
        return f"ID: {self.id} | hero_id: {self.hero_id} | moto_id: {self.moto_id} | moto: {self.moto}"
    
class Heroes_history(Base):
    __tablename__ = 'heroes_histories'
    id = Column(Integer, primary_key = True)
    hero_id = Column('hero_id', Integer, ForeignKey('heroes.id',ondelete="CASCADE"))
    story = Column('story', String)
    heroes = relationship("Hero",back_populates="heroes_histories")
    
    def __init__(self, hero_id, story):
        if session.query(Heroes_history).filter(Heroes_history.hero_id == hero_id).count():
            raise NameError("hero_id already exists")
        self.hero_id = hero_id
        self.story = story
        
    def __str__(self):
        return f"Hero_ID {self.hero_id} | Story: {self.story}"

    
class Battle(Base):
    __tablename__ = "battles"
    id = Column(Integer, primary_key = True)
    hero_1_id = Column('hero_1_id',Integer, ForeignKey('heroes.id',ondelete="SET NULL"))
    hero_1_moto_id = Column('hero_1_moto_id', Integer, ForeignKey('heroes_motos.id',ondelete="SET NULL"))
    hero_2_id = Column('hero_2_id',Integer, ForeignKey('heroes.id',ondelete="SET NULL"))
    hero_2_moto_id = Column('hero_2_moto_id', Integer, ForeignKey('heroes_motos.id',ondelete="SET NULL"))
    winner = Column('winner',Integer)
    
    def __str__(self):
        hero1 = session.query(Hero).filter(Hero.id == self.hero_1_id)[0]
        hero2 = session.query(Hero).filter(Hero.id == self.hero_2_id)[0]
        moto1 = session.query(Heroes_moto).filter(Heroes_moto.id == self.hero_1_moto_id)[0].moto
        moto2 = session.query(Heroes_moto).filter(Heroes_moto.id == self.hero_2_moto_id)[0].moto
        if self.winner == 1:
            winner = hero1.name
        elif self.winner == 2:
            winner = hero2.name
        else:
            winner = "Draw"
        battlelog = (
            f"{hero1.name}[{hero1.power}] attacks {hero2.name}[{hero2.power}] \n"
            f"{hero1.side} versus {hero2.side} \n"
            f"{hero1.name}: {moto1} \n"
            f"{hero2.name}: {moto2} \n"
            f"Winner: {winner}"
        )
        return battlelog

    def __init__(self, hero_1_id, hero_2_id):
        self.hero_1_id = hero_1_id
        self.hero_1_moto_id = session.query(Heroes_moto).filter(Heroes_moto.hero_id == hero_1_id).order_by(func.random())[0].id
        self.hero_2_id = hero_2_id
        self.hero_2_moto_id = session.query(Heroes_moto).filter(Heroes_moto.hero_id == hero_2_id).order_by(func.random())[0].id
        power1 = session.query(Hero).filter(Hero.id == hero_1_id)[0].power
        sum_power = 1+ power1 + session.query(Hero).filter(Hero.id == hero_2_id)[0].power
        rand = choice(range(sum_power))
        if rand==0:
            self.winner = 0
        elif rand<=power1:
            self.winner = 1
        else:
            self.winner = 2
        print(self)
        
def add_hero(side:str,name:str,date,magic:bool,power:int):
    session.add(Hero(side,name, date,magic,power))
    session.commit()
    session.close()
    def_logger.debug(f"Hero {name} is created")

def add_moto(hero_id:int,moto:str):
    session.add(Heroes_moto(hero_id,moto))
    session.commit()
    session.close()
    def_logger.debug(f"Moto is created")
    
def add_history(hero_id:int,history:str):
    session.add(Heroes_history(hero_id,history))
    session.commit()
    session.close()
    def_logger.debug(f"History is created")
    
def add_random_battle():
    hero1 = session.query(Hero).order_by(func.random())[0]
    hero2 = session.query(Hero).filter(Hero.side != hero1.side).order_by(func.random())[0]
    battle = Battle(hero1.id,hero2.id)
    winner = battle.winner
    session.add(battle)
    session.commit()
    session.close()
    def_logger.debug(f"Battle is created. Winner: {winner}")

def add_battle(id_hero1,id_hero2):
    hero1 = session.query(Hero).filter(Hero.id == id_hero1)[0]
    hero2 = session.query(Hero).filter(Hero.id == id_hero2)[0]
    if hero1.side == hero2.side:
        print("Heroes are from one side. They salute each other.")
        return 0
    battle = Battle(hero1.id,hero2.id)
    winner = battle.winner
    session.add(battle)
    session.commit()
    session.close()
    def_logger.debug(f"Battle is created. Winner: {winner}")

def delete_hero(hero_id):
    obj1 = session.query(Hero).filter(Hero.id == hero_id).all()[0]
    session.delete(obj1)
    session.commit()
    session.close()
    def_logger.debug(f"Hero {obj1.name} is deleted")

def show_heroes():
    query = session.query(Hero).all()
    for each in query:
        print(each)

# 2 - generate database schema
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

def_logger.info("Tables are created")

session = Session()

def_logger.debug("Main script is over")

import menu