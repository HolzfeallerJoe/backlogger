import os
from contextlib import asynccontextmanager
from typing import Dict, List

import psycopg
from fastapi import FastAPI, HTTPException, Path, Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.templating import Jinja2Templates

from est_length_service import get_est_length
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
templates = Jinja2Templates(directory='frontend')


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
def get_games(skip: int = 0, limit: int = 100) -> Dict[str, List[Game]]:
	res = get_all_games(app.state.connection, skip, limit)

	if not res.success:
		raise HTTPException(
			status_code=500,
			detail={'error': 'DatabaseError', 'message': res.message},
		)

	if not res.data:
		raise HTTPException(
			status_code=404,
			detail={
				'error': 'NotFound',
				'message': 'No games found',
				'skip': skip,
				'limit': limit,
			},
		)

	return {'games': res.data}


@app.post(
	'/games',
	response_model=Dict[str, int],
	status_code=201,
	summary='Create a new game entry',
	description='Add a new game to the database. Returns the auto-generated game_id.',
)
def post_game(game: Game) -> Dict[str, int]:
	game.est_length = get_est_length(game.name)
	res = add_game(app.state.connection, game)

	if not res.success:
		status = 409 if 'exists' in res.message.lower() else 500
		raise HTTPException(
			status_code=status,
			detail={
				'error': 'Conflict' if status == 409 else 'DatabaseError',
				'message': res.message,
				'game': game.name,
			},
		)

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

	if not res.success:
		raise HTTPException(
			status_code=500,
			detail={
				'error': 'DatabaseError',
				'message': res.message,
				'game_id': game_id,
			},
		)

	if not res.data:
		raise HTTPException(
			status_code=404,
			detail={
				'error': 'NotFound',
				'message': f'No game found with id {game_id}',
				'game_id': game_id,
			},
		)

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
		# If service told us no rows → 404, else 500
		status = 404 if 'not found' in res.message.lower() else 500
		raise HTTPException(
			status_code=status,
			detail={
				'error': 'NotFound' if status == 404 else 'DatabaseError',
				'message': res.message,
				'game_id': game_id,
			},
		)

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

	if not res.success:
		# distinguish “no data yet” vs real exception
		if isinstance(res.data, Exception):
			raise HTTPException(
				status_code=500,
				detail={
					'error': 'DatabaseError',
					'message': str(res.data),
					'game_id': game_id,
				},
			)
		raise HTTPException(
			status_code=404,
			detail={
				'error': 'NotFound',
				'message': res.message,
				'game_id': game_id,
			},
		)
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
		# conflict if data already exists, else internal error
		if isinstance(res.data, Exception):
			raise HTTPException(
				status_code=500,
				detail={
					'error': 'DatabaseError',
					'message': str(res.data),
					'game_id': game_id,
				},
			)
		raise HTTPException(
			status_code=409,
			detail={
				'error': 'Conflict',
				'message': res.message,
				'game_id': game_id,
			},
		)

	return {'patched': res.success}


@app.get('/', response_class=HTMLResponse)
@app.get('/index', response_class=HTMLResponse)
def show_index(request: Request) -> HTMLResponse:
	result = get_all_games(app.state.connection, skip=0, limit=100)
	games = result.data if result.success and result.data else []
	return templates.TemplateResponse(
		'index.html', {'request': request, 'title': 'My Game Backlog', 'games': games}
	)
