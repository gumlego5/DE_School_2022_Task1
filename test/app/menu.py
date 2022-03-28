from time import sleep
from initial_table import initiates, add_hero, add_history, add_moto, add_random_battle, delete_hero, date
from app import show_heroes,add_battle
import logging

INITIATE = True

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

if INITIATE:
    initiates()
    def_logger.debug("Initilization is completed")
else:
    def_logger.debug("Initilization isn't required")

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
        # if s == 0:
        #     initiates()
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
                add_battle(int(input("hero1_id")),int(input("hero_id")))
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

    
