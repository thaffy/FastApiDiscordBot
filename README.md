# THIS README IS A WORK IN PROGRESS!
Installation instructions are not yet complete, and the project is not yet ready for use.
---

---

# FastAPI + Discord Bot
*NB: This repo is developed for a specific discord server, and the bot will not work in other servers without modifications.*
# How to run
This project uses pipenv to manage dependencies and docker to run a local postgres database.

* https://pipenv.pypa.io/en/latest/
* https://docs.docker.com/get-started/get-docker/  *(Installing Docker Desktop should set you up with the Docker CLI as well)*
* https://www.jetbrains.com/pycharm/ *(This project was developed using PyCharm, which should be able to manage enviroments)*

## Install pipenv
```bash
pip install pipenv
```


## Local Database
Pull a postgres image with docker and run it:
```bash
docker pull postgres
```
```bash
docker run --name delta-postgres -e POSTGRES_PASSWORD=postgres -d -p 5432:5432 postgres
```
You can verify that it is working by running:
```bash
docker exec -it delta-postgres psql -U postgres -d postgres
```
This will open a psql shell. You can list the databases with:
```psql
\l \q
```
This will list the databases and then quit the psql shell.

### Run migrations
The project uses alembic to manage database migrations. To run the migrations, run the following command:
```bash
pipenv run alembic upgrade head
```

## Api & Bot
```bash
pipenv install
```
You will need to define the following secrets in your .env file for the bot to function properly
```.env
DISCORD_TOKEN=your_discord_token // To connect and run commands on discord
GEMINI_API_KEY=your_gemini_api_key // To enable the bot to create responses with the gemini api
```


To run the project, run:
```bash
pipenv run uvicorn app.main:app --reload
```
You should now be able to access the api at locally, via for example the following URLs
```
http://localhost:8000/docs
```
```
http://127.0.0.1:8000/docs
```

The discord bot starts in mainy.py's lifespan method.
It might take a few seconds to start the bot after the api is up.


## Useful Links
* https://fastapi.tiangolo.com/learn/
* https://discordpy.readthedocs.io/en/stable/