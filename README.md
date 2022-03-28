# DE_School_2022_Task1
First task for DE_School_2022

Run:                            docker-compose up --build
Go to app's console:            docker attach test-app-1
                                type "sd"
                You're in the menu
Go to db's console:             docker exec -it test-db-1 /bin/bash
                                psql -d database -U username -W -h db
                                secret
                You're in the db's console
                                SELECT * FROM heroes;
Go to app's log.txt:            docker exec -it test-app-1 /bin/bash
                                cat log.txt
                            

