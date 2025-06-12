import os
from contextlib import asynccontextmanager
from typing import Dict, List

import psycopg
from fastapi import FastAPI, HTTPException, Path, Request
from starlette.responses import JSONResponse

from postgres_service import (
	get_all_games,
	add_game,
	get_game_by_id,
	delete_game,
	get_post_finish_game_id,
	add_post_finish_stats,
	create_database,
	checkConnection,
)
from game import PostFinish, Game


@asynccontextmanager
async def lifespan(app: FastAPI):
	database_host = os.getenv('POSTGRES_HOST').strip()
	database_username = os.getenv('POSTGRES_USER').strip()
	database_password = os.getenv('POSTGRES_PASSWORD').strip()
	database_name = os.getenv('POSTGRES_DB').strip()

	try:
		app.state.connection = psycopg.connect(
			dbname=database_name,
			user=database_username,
			password=database_password,
			host=database_host,
			port='5432',
		)
		print('Database connection established')
	except Exception as error:
		raise Exception('Database connection failed.', error)
	create_database(app.state.connection)
	yield
	# Code that executes after finish
	app.state.connection.close()


app = FastAPI(
	title='Backlogger',
	version='1.0.0',
	description=(
		'REST API to track games you plan to play and record post-completion stats.'
	),
	lifespan=lifespan,
)

# TODO: Setup and change functions to Postgres
# TODO: All sollte auch query für limit und jump haben - paging
# TODO: Error handling needs to be better / Better HTTPExceptions and details and more


@app.middleware('http')
async def checkDatabaseConnection(request: Request, call_next):
	if not checkConnection(app.state.connection):
		return JSONResponse(
			status_code=503, content={'detail': 'Database connection lost.'}
		)
	return await call_next(request)


@app.get(
	'/games',
	response_model=Dict[str, List[Game]],
	summary='Retrieve all games',
	description='Fetch a list of all games currently stored in the database.',
)
def get_games() -> Dict[str, List[Game]]:
	res = get_all_games(app.state.connection)

	if not res.success or not res.data:
		raise HTTPException(status_code=404, detail='No Games found')

	return {'games': res.data}


@app.post(
	'/games',
	response_model=Dict[str, int],
	status_code=201,
	summary='Create a new game entry',
	description='Add a new game to the database. Returns the auto-generated game_id.',
)
def post_game(game: Game) -> Dict[str, int]:
	res = add_game(app.state.connection, game)

	if not res.success or not res.data:
		raise HTTPException(status_code=409, detail='Game could not be created')

	return {'posted': res.data}


@app.get(
	'/games/{game_id}',
	response_model=Dict[str, Game],
	summary='Get a single game by ID',
	description='Retrieve detailed information for a specific game by its ID.',
)
def get_game(
	game_id: int = Path(..., description='The integer ID of the game to retrieve', ge=1),
) -> Dict[str, Game]:
	res = get_game_by_id(app.state.connection, game_id)

	if not res.success or not res.data:
		raise HTTPException(status_code=404, detail=f'No Game with the id {game_id} found')

	return {'game': res.data}


@app.delete(
	'/games/{game_id}',
	response_model=Dict[str, bool],
	summary='Delete a game by ID',
	description='Remove the specified game from the database.',
)
def delete_one_game(
	game_id: int = Path(..., description='The integer ID of the game to delete', ge=1),
) -> Dict[str, bool]:
	res = delete_game(app.state.connection, game_id)

	if not res.success:
		raise HTTPException(status_code=404, detail=f'No Game with the id {game_id} found')

	return {'deleted': res.success}


@app.get(
	'/games/{game_id}/post_finish',
	response_model=Dict[str, PostFinish],
	summary='Get post-finish stats for a game',
	description='Retrieve post-completion details for a given game.',
)
def get_post_finish(
	game_id: int = Path(
		..., description='The game ID to fetch post-finish data for', ge=1
	),
) -> Dict[str, PostFinish]:
	res = get_post_finish_game_id(app.state.connection, game_id)

	if not res.success or not res.data:
		raise HTTPException(status_code=404, detail=f'No Game with the id {game_id} found')
	return {'Post Finish': res.data}


@app.patch(
	'/games/{game_id}/post_finish',
	response_model=Dict[str, bool],
	summary='Add post-finish stats',
	description='Insert the post-completion statistics for a given game.',
)
def patch_post_finish(
	pfg: PostFinish,
	game_id: int = Path(
		..., description='The ID of the game to patch post-finish stats for', ge=1
	),
) -> Dict[str, bool]:
	res = add_post_finish_stats(app.state.connection, pfg, game_id)

	if not res.success:
		raise HTTPException(status_code=404, detail=f'No Game with the id {game_id} found')

	return {'patched': res.success}
