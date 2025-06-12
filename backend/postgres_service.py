from datetime import datetime
from sqlite3 import Connection
from typing import Optional, NamedTuple

from game import Game, PostFinish


class OperationResult(NamedTuple):
	success: bool
	message: str
	data: Optional[any] = None


def create_database(connection: Connection) -> OperationResult:
	try:
		cursor = connection.cursor()
		create_game_table = """
			CREATE TABLE IF NOT EXISTS Game (
					game_id INTEGER PRIMARY KEY AUTOINCREMENT,
					name TEXT NOT NULL UNIQUE,
					est_length INTEGER NOT NULL,
					released INTEGER NOT NULL,
					purchased INTEGER NOT NULL,
					excitement INTEGER NOT NULL,
					dropped INTEGER,
					credits INTEGER,
					time_played INTEGER,
					duration TEXT,
					rating INTEGER,
					worth INTEGER,
					reason TEXT,
					finished_at DateTime
			);
		"""
		cursor.execute(create_game_table)
		connection.commit()
		return OperationResult(True, 'Created Database')
	except Exception as e:
		print(f'Error creating datebase: {e}')
		return OperationResult(False, 'Error creating datebase', e)


def add_game(connection: Connection, game: Game) -> OperationResult:
	try:
		print('~~Insert Game~~')
		insert_game = """
			INSERT INTO Game (name, est_length, released, purchased, excitement) 
			VALUES (?, ?, ?, ?, ?)
		"""

		cursor = connection.cursor()
		cursor.execute(
			insert_game,
			[game.name, game.est_length, game.released, game.purchased, game.excitement],
		)
		connection.commit()
		print('Game was inserted')
		return OperationResult(True, 'Inserted Game', cursor.lastrowid)
	except Exception as e:
		print(f'Error inserting game: {e}')
		return OperationResult(False, 'Error inserting game', e)


def add_post_finish_stats(
	connection: Connection, pfg: PostFinish, game_id: int
) -> OperationResult:
	try:
		print('~~~Update Game~~~')

		if not check_able_to_edit(connection, game_id):
			return OperationResult(
				False, 'Game can not be edited - post finish data already existend'
			)

		cursor = connection.cursor()
		update_statement = """
			UPDATE Game
			SET dropped = ?,
			   credits = ?,
			   time_played = ?,
			   duration = ?,
			   rating = ?,
			   worth = ?,
			   reason = ?,
			   finished_at = ?
			WHERE game_id = ?
		"""

		cursor.execute(
			update_statement,
			[
				pfg.dropped,
				pfg.credits,
				pfg.time_played,
				pfg.duration,
				pfg.rating,
				pfg.worth,
				pfg.reason,
				datetime.now(),
				game_id,
			],
		)
		connection.commit()
		print('Game was updated')
		return OperationResult(True, 'Added Post Finish Stats')
	except Exception as e:
		print(f'Error updating game: {e}')
		return OperationResult(False, 'Error updating game', e)


def delete_game(connection: Connection, game_id: int) -> OperationResult:
	try:
		print('~~Delete Game~~')
		delete_statement = """
			DELETE FROM Game WHERE game_id = ?
		"""

		cursor = connection.cursor()
		cursor.execute(delete_statement, [game_id])
		connection.commit()
		print('Game was deleted')
		return OperationResult(True, 'Deleted Game', game_id)
	except Exception as e:
		print(f'Error deleting game: {e}')
		return OperationResult(False, 'Error deleting game', e)


def get_all_games(connection: Connection) -> OperationResult:
	try:
		print('~~~Selecting all Games~~~')
		select_statement = """
			SELECT * FROM Game
    """

		cursor = connection.cursor()
		cursor.execute(select_statement)
		games = cursor.fetchall()
		print('Games were selected')
		return OperationResult(True, 'Games', [dict(game) for game in games])
	except Exception as e:
		print(f'Error getting all games: {e}')
		return OperationResult(False, 'Error getting all games', e)


def get_game_by_id(connection: Connection, game_id: int) -> OperationResult:
	try:
		print('~~~Selecting Game~~~')
		select_statement = """
			SELECT * FROM Game WHERE game_id = ?
		"""

		cursor = connection.cursor()
		cursor.execute(select_statement, [game_id])
		game = cursor.fetchone()
		if not game:
			game = {}
		print('Game was selected')
		return OperationResult(True, 'Game', dict(game))
	except Exception as e:
		print(f'Error getting game: {e}')
		return OperationResult(False, 'Error getting game', e)


def get_post_finish_game_id(connection: Connection, game_id: int) -> OperationResult:
	try:
		print('~~~Selecting Post Finish~~~')
		select_statement = """
			SELECT * FROM Game WHERE game_id = ?
		"""

		cursor = connection.cursor()
		cursor.execute(select_statement, [game_id])
		post_finish = cursor.fetchone()
		if not post_finish:
			post_finish = {}
		print('Post Finish was selected')
		return OperationResult(True, 'post finish', dict(post_finish))
	except Exception as e:
		print(f'Error getting Post Finish: {e}')
		return OperationResult(False, 'Error getting Post Finish', e)


def check_able_to_edit(connection: Connection, game_id: int) -> bool:
	print('~~~Check if can be edited~~~')
	cursor = connection.cursor()

	select_statement = """
		SELECT finished_at FROM Game WHERE game_id = ?
	"""

	cursor.execute(
		select_statement,
		[game_id],
	)
	row = cursor.fetchone()

	edit = row['finished_at'] is None or row is None
	if not edit:
		print(f'~~~Game {game_id} can not be edited~~~')

	return edit
