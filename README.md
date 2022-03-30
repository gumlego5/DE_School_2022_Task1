# DE_School_2022_Task1
First task for DE_School_2022

Tables:
    1) heroes - Store heroes information: id,side,name,birthday year, magic(1,0), power(int), moto relates to heroes_motos, 
        heroes_histories relates to heroes_histories, battle relation to battles
    2) heroes_motos - Store heroes motos: id, hero_id, moto_id, moto
    3) heroes_histories - Store heroes hostories: id, hero_id, story, heroes relates to heroes
    4) battles - id, hero_1_id, hero_1_moto_id, hero_2_id, hero_2_moto_id, winner

How to start project:
1 Go to /services/ folder

2.1 DEBUG:
    Run:                            docker-compose up --build --force-recreate

    Access to app's menu:           
                                    docker attach app
                                    press Enter for menu
                    You're in the menu

    Access to db's console:         
                                    docker exec -it database /bin/bash
                                    psql -d database -U username -W -h db
                                    secret
                    You're in the db's console
                                    SELECT * FROM heroes;

    Access to app's logs:            
                                    docker exec -it database /bin/bash
                                    cat log.txt
                                    cat user_actions.txt

2.2 PROD:
    Run:                            docker-compose -f docker-compose_prod.yml up --build --force-recreate

    Access to app's menu:           
                                    docker attach app_prod
                                    press Enter for menu
                    You're in the menu

    Access to db's console:         
                                    docker exec -it database_prod /bin/bash
                                    psql -d database -U username -W -h db
                                    secret
                    You're in the db's console
                                    SELECT * FROM heroes;

    Access to app's logs:            
                                    docker exec -it database_prod /bin/bash
                                    cat log.txt
                                    cat user_actions.txt
