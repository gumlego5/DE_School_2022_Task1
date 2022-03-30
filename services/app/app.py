import os
import logging
from time import sleep
from datetime import date
from random import choice
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer, Date, Table, ForeignKey, Boolean
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship, backref
from sqlalchemy.schema import DropTable
from sqlalchemy.sql.expression import func, select

sleep(10)

PROD_STATUS = int(os.environ['PROD_STATUS'])

Base = declarative_base()

#Tables configuration
@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"

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
#Tables configuration end

#Scripts configuration
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

#Initial script with default data
def initiates():
    def_logger.info("initiates() is running")
    # 4 - create heroes
    add_hero("Stark","Jon Snow", date(280, 1, 1),False,10)
    add_history(1, "Jon Snow is the bastard son of Eddard Stark, Lord of Winterfell. He has five half-siblings: Robb, Sansa, Arya, Bran, and Rickon Stark. Unaware of the identity of his mother, Jon was raised at Winterfell. At the age of fourteen, he joins the Night's Watch, where he earns the nickname Lord Snow.")
    add_hero("Targaryen","Daenerys Targaryen", date(281, 1, 1),True,15)
    add_history(2,"Daenerys is in her early teens living in exile in Essos. She remains dependent on her abusive older brother, Viserys, and is forced to marry Dothraki horselord Khal Drogo in exchange for an army for Viserys, who wishes to return to Westeros and recapture the Iron Throne.")
    add_hero("Lannister","Joffrey Baratheon", date(282, 1, 1),False,2)
    add_history(3,"Prince Joffrey Baratheon is known to the Seven Kingdoms as the eldest son and heir of King Robert I Baratheon and Queen Cersei Lannister. A member of House Baratheon of King's Landing, his siblings are Princess Myrcella and Prince Tommen.")
    add_hero("Stark","Arya Stark", date(287,1,1),True,13)
    add_history(4, "Princess Arya Stark is the third child and second daughter of Lord Eddard Stark and his wife, Lady Catelyn Stark. She is the sister of the incumbent Westerosi monarchs, Sansa, Queen in the North, and Brandon, King of the Andals and the First Men.")
    add_hero("Targaryen", "Aerys II Targaryen", date(240,1,1), False, 6)
    add_history(5,"King Aerys II Targaryen, commonly called \"the Mad King\", was the sixteenth member of House Targaryen to rule from the Iron Throne. Although his rule began benevolently, he succumbed to the madness caused by his incestuous lineage, and was eventually deposed by Lord Robert Baratheon in a civil war.")
    add_hero("Lannister","Tywin Lannister", date(234,1,1), False, 11)
    add_history(6,"Lord Tywin Lannister was the head of House Lannister, Lord of Casterly Rock, Warden of the West, Lord Paramount of the Westerlands, Hand of the King for three different kings, and Protector of the Realm. He was the father of Cersei, Jaime, and Tyrion Lannister, and sole grandfather of the incest-born Joffrey, Myrcella, and Tommen Baratheon.")
    add_hero("Lannister","Jaime Lannister",date(261,1,1),False,8)
    add_history(7,"Ser Jaime Lannister was the elder son of Lord Tywin Lannister, younger twin brother of Queen Cersei Lannister, and older brother of Tyrion Lannister. He was involved in an incestuous relationship with Cersei, and unknown to most, he was the biological father of her three bastard children, Joffrey, Myrcella, and Tommen, as well as her unborn child.")
    add_hero("Stark", "Eddard Stark",date(263,1,1), False, 5)
    add_history(8,"Lord Eddard Stark, also known as Ned Stark, was the head of House Stark, the Lord of Winterfell, Lord Paramount and Warden of the North, and later Hand of the King to King Robert I Baratheon. He was the older brother of Benjen, Lyanna and the younger brother of Brandon Stark. He is the father of Robb, Sansa, Arya, Bran, and Rickon by his wife, Catelyn Tully, and uncle of Jon Snow, who he raised as his bastard son.")
    add_hero("Targaryen", "Drogo",date(273,1,1),False, 9)
    add_history(9,"Khal Drogo was a chieftain of a Dothraki khalasar. He was often referred to as \"The Great Khal.\" He is also the namesake of the last living dragon in existence, Drogon, who was the personal mount of his late widow.")

    # 4 - create moto
    add_moto(1,"If I Fall, Don't Bring Me Back")
    add_moto(1,"I Do Know Some Things...")
    add_moto(1,"You All Crowned Me Your King. I Never Wanted It...")
    add_moto(2,"They can live in my new world, or they can die in their old one")
    add_moto(2,"I will answer injustice with justice")
    add_moto(2,"My reign has just begun")
    add_moto(3,"I cannot abide the wailing of women")
    add_moto(3,"I am the king! I will punish you!")
    add_moto(3,"Will you forgive me for my rudeness?")
    add_moto(4,"Fear cuts deeper than swords")
    add_moto(4,"Not today")
    add_moto(4,"A girl has no name")
    add_moto(5,"I want him dead, the traitor.")
    add_moto(5,"Burn them all! BURN THEM ALL!")
    add_moto(5,"I want his head, you'll bring me his head, or you'll burn with all the rest.")
    add_moto(6,"A Lion Doesn't Concern Himself With The Opinions Of The Sheep")
    add_moto(6,"Why Is He Still Alive?")
    add_moto(6,"You Really Think A Crown Gives You Power?")
    add_moto(7, "By What Right Does The Wolf Judge The Lion?")
    add_moto(7, "The Things I Do For Love.")
    add_moto(7, "People Have Been Swinging At Me For Years, But They Always Seem To Miss...")
    add_moto(8, "The winters are hard but the Starks will endure. We always have.")
    add_moto(8, "We've come to a dangerous place. We can't afford to fight a war amongst ourselves.")
    add_moto(8, "The man who passes the sentence should swing the sword")
    add_moto(9, "You are no king.")
    add_moto(9, "A Crown For A King!")
    add_moto(9, "No!")

    for i in range(10):
        add_random_battle()

 #Logger configuration      
def_logger = logging.getLogger(__name__)
def_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
file_handler = logging.FileHandler("log.txt")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
def_logger.addHandler(file_handler)
def_logger.addHandler(stream_handler)
def zerocut(record): # filters battle's draw
    if record.msg[-1] != "0":
        return True
logfilter = logging.Filter()
logfilter.filter = zerocut
def_logger.addFilter(logfilter)

def_logger.info(f"PROD VALUE = {PROD_STATUS} ")
def_logger.info(f"START")

#Connection config - Settings as shown in docker-compose.yml
db_name = 'database'
db_user = 'username'
db_pass = 'secret'
db_host = 'db'
db_port = '5432'

engine = create_engine('postgresql+psycopg2://{}:{}@{}:{}/{}'.format(db_user, db_pass, db_host, db_port, db_name))
def_logger.info("Connection with database is established")
Session = sessionmaker(bind=engine)
session = Session()

# 2 - generate database schema
if PROD_STATUS == 0:
    Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

def_logger.info("Tables are created")

if PROD_STATUS == 0:
    initiates()
    def_logger.info("Initilization completed")
else:
    def_logger.info("Initilization isn't required")

# Menu
def printmenu():
    print(
        f"Available options: \n"
        f"1. Add hero \n"
        f"2. Add moto \n"
        f"3. Add history \n"
        f"4. Add battle \n"
        f"5. Add random battle \n"
        f"6. Delete Hero \n"
        f"7. Show All Heroes \n"
    )

def_logger.debug("Menu started")
    
def_logger.removeHandler(file_handler)
file_handler = logging.FileHandler("user_actions.txt")
def_logger.addHandler(file_handler)

while True:
    printmenu()
    s = input()
    try:
        s = int(s)
    except ValueError:
        pass
    if type(s) == int:
        if s in range(1,8):
            if s == 1:
                add_hero(input("Side: "),input("Name: "),date(int(input("Year of birth: ")),1,1),int(input("Magic (1,0): ")),int(input("Power: ")))
                def_logger.info("User added a hero")
            if s == 2:
                add_moto(int(input("hero_id: ")),input("moto: "))
                def_logger.info("User added a moto")
            if s == 3:
                add_history(int(input("hero_id: ")),input("history: "))
                def_logger.info("User added a history")
            if s == 4:
                add_battle(int(input("hero1_id: ")),int(input("hero_id: ")))
                def_logger.info("User added a battle")
            if s == 5:
                add_random_battle()
                def_logger.info("User added a random battle")
            if s == 6:
                delete_hero(int(input("hero_id: ")))
                def_logger.info("User deleted a hero")
            if s == 7:
                show_heroes()
            print("Done")

    
