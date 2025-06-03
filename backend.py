import sqlite3
from contextlib import asynccontextmanager
from os.path import exists
from typing import Dict, List

from fastapi import FastAPI, HTTPException, Path

from database_service import (
	create_database,
	get_all_games,
	get_game_by_id,
	delete_game,
	add_post_finish_stats,
	add_game,
	get_post_finish_game_id,
)
from game import PostFinish, Game


@asynccontextmanager
async def lifespan(app: FastAPI):
	if not exists('./game.db'):
		create_connection = sqlite3.connect('game.db')
		create_database(create_connection)
		create_connection.close()
	app.state.connection = sqlite3.connect('game.db', check_same_thread=False)
	app.state.connection.row_factory = sqlite3.Row

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

# TODO: Error handling needs to be better / Better HTTPExceptions and details and more

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
	summary='Add or update post-finish stats',
	description='Insert or update the post-completion statistics for a given game.',
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
