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
    
    def __init__(self, hero_1_id, hero_2_id):
        self.hero_1_id = hero_1_id
        self.hero_1_moto_id = session.query(Heroes_moto).filter(Heroes_moto.hero_id == hero_1_id).order_by(func.random())[0].id
        self.hero_2_id = hero_2_id
        self.hero_2_moto_id = session.query(Heroes_moto).filter(Heroes_moto.hero_id == hero_2_id).order_by(func.random())[0].id
        power1 = session.query(Hero).filter(Hero.id == hero_1_id)[0].power
        power2 = session.query(Hero).filter(Hero.id == hero_2_id)[0].power
        if power1 > power2:
            self.winner = 1
        elif power2>power1:
            self.winner = 2
        else:
            self.winner = 0
    
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
            f"{hero1.name} attacks {hero2.name} \n"
            f"{hero1.side} versus {hero2.side} \n"
            f"{hero1.name}: {moto1} \n"
            f"{hero2.name}: {moto2} \n"
            f"Winner: {winner}"
        )
        return battlelog
    