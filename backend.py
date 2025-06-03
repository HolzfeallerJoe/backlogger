import sqlite3
from contextlib import asynccontextmanager
from os.path import exists
from typing import Dict, List

from fastapi import FastAPI, HTTPException


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


app = FastAPI(lifespan=lifespan)


@app.get('/games')
def get_games() -> Dict[str, List[Game]]:
	res = get_all_games(app.state.connection)

	if not res.success or not res.data:
		raise HTTPException(status_code=404, detail='No Games found')

	return {'games': res.data}


@app.post('/games')
def post_game(game: Game) -> Dict[str, int]:
	res = add_game(app.state.connection, game)

	if not res.success or not res.data:
		raise HTTPException(status_code=409, detail='Game could not be created')

	return {'posted': res.data}


@app.get('/games/{game_id}')
def get_game(game_id: int) -> Dict[str, Game]:
	res = get_game_by_id(app.state.connection, game_id)

	if not res.success or not res.data:
		raise HTTPException(status_code=404, detail=f'No Game with the id {game_id} found')

	return {'game': res.data}


@app.delete('/games/{game_id}')
def delete_one_game(game_id: int) -> Dict[str, bool]:
	res = delete_game(app.state.connection, game_id)

	if not res.success:
		raise HTTPException(status_code=404, detail=f'No Game with the id {game_id} found')

	return {'deleted': res.success}


@app.get('/games/{game_id}/post_finish')
def get_post_finish(game_id: int) -> Dict[str, PostFinish]:
	res = get_post_finish_game_id(app.state.connection, game_id)

	if not res.success or not res.data:
		raise HTTPException(status_code=404, detail=f'No Game with the id {game_id} found')
	return {'Post Finish': res.data}


@app.patch('/games/{game_id}/post_finish')
def patch_post_finish(pfg: PostFinish, game_id: int) -> Dict[str, bool]:
	res = add_post_finish_stats(app.state.connection, pfg, game_id)

	if not res.success:
		raise HTTPException(status_code=404, detail=f'No Game with the id {game_id} found')

	return {'patched': res.success}
