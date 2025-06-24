from datetime import datetime
from psycopg import Connection, errors
from typing import Optional, NamedTuple, List, Dict, Any

from psycopg.sql import SQL, Placeholder, Identifier

from game import Game, PostFinish


class OperationResult(NamedTuple):
	success: bool
	message: str
	data: Optional[Any] = None


def create_database(connection: Connection) -> OperationResult:
	try:
		print('Creating database')
		cursor = connection.cursor()

		create_game_table = SQL("""
      CREATE TABLE IF NOT EXISTS Game (
          game_id SERIAL PRIMARY KEY,
          name TEXT NOT NULL UNIQUE,
          est_length INTEGER,
          released BOOLEAN NOT NULL,
          purchased BOOLEAN NOT NULL,
          excitement INTEGER NOT NULL,
          dropped BOOLEAN,
          credits BOOLEAN,
          time_played INTEGER,
          duration TEXT,
          rating INTEGER,
          worth BOOLEAN,
          reason TEXT,
          finished_at TIMESTAMP
      );
    """)

		cursor.execute(create_game_table)
		connection.commit()
		print('created database')
		return OperationResult(True, 'Created Database')
	except Exception as e:
		connection.rollback()
		print(f'Error creating datebase: {e}')
		return OperationResult(False, 'Error creating datebase', e)


def add_game(connection: Connection, game: Game) -> OperationResult:
	try:
		print('~~Insert Game~~')
		insert_game = SQL("""
      INSERT INTO Game (name, est_length, released, purchased, excitement) 
      VALUES (%s, %s, %s, %s, %s)
    """)

		cursor = connection.cursor()

		cursor.execute(
			insert_game,
			[game.name, game.est_length, game.released, game.purchased, game.excitement],
		)
		connection.commit()
		select_statement = SQL("""
      SELECT * FROM Game
      ORDER BY game_id DESC
      LIMIT 1;
    """)

		cursor.execute(select_statement)
		row = cursor.fetchone()
		if row:
			cols = [desc[0] for desc in cursor.description]
			game = dict(zip(cols, row))
		else:
			game = {}
		print(f'Game was inserted as {game.get("game_id")}')
		return OperationResult(True, 'Inserted Game', game.get('game_id'))
	except errors.UniqueViolation as e:
		connection.rollback()
		print(f'Error inserting game: {e}')
		return OperationResult(False, 'Game already exists', e)
	except Exception as e:
		connection.rollback()
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
		update_statement = SQL("""
      UPDATE Game
      SET dropped = %s,
         credits = %s,
         time_played = %s,
         duration = %s,
         rating = %s,
         worth = %s,
         reason = %s,
         finished_at = %s
      WHERE game_id = %s
    """)

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
		connection.rollback()
		print(f'Error updating game: {e}')
		return OperationResult(False, 'Error updating game', e)


def delete_game(connection: Connection, game_id: int) -> OperationResult:
	try:
		print('~~Delete Game~~')
		delete_statement = SQL("""
      DELETE FROM Game WHERE game_id = %s
    """)

		cursor = connection.cursor()
		cursor.execute(delete_statement, [game_id])
		if cursor.rowcount == 0:
			cursor.close()
			connection.rollback()
			return OperationResult(False, f'No game with id {game_id}', None)
		connection.commit()
		cursor.close()
		print('Game was deleted')
		return OperationResult(True, 'Deleted Game', game_id)
	except Exception as e:
		connection.rollback()
		print(f'Error deleting game: {e}')
		return OperationResult(False, 'Error deleting game', e)


def get_all_games(
	connection: Connection,
	parameter: Dict[str, Any] = None,
) -> OperationResult:
	try:
		print('~~~Selecting all Games~~~')
		select_statement: SQL = SQL('SELECT * FROM Game')
		params: List[Any] = []

		skip = parameter.pop('skip', 0)
		limit = parameter.pop('limit', 100)

		if parameter:
			clauses = []
			for col, val in parameter.items():
				if val == "NULL":
					clauses.append(
						SQL("{} IS NULL").format(Identifier(col))
					)
				else:
					clauses.append(SQL('{} = {}').format(Identifier(col), Placeholder()))
					params.append(val)
			select_statement += SQL(' WHERE ') + SQL(' AND ').join(clauses)
		else:
			select_statement += SQL(' OFFSET ') + Placeholder() + SQL(' LIMIT ') + Placeholder()
			params.extend([skip, limit])

		cursor = connection.cursor()
		cursor.execute(select_statement, params)

		games = cursor.fetchall()
		columns = [desc.name for desc in cursor.description]
		result = [dict(zip(columns, row)) for row in games]
		print('Games were selected')

		return OperationResult(True, 'Games', result)
	except Exception as e:
		connection.rollback()
		print(f'Error getting all games: {e}')
		return OperationResult(False, 'Error getting all games', e)


def get_game_by_id(connection: Connection, game_id: int) -> OperationResult:
	try:
		print('~~~Selecting Game~~~')
		select_statement = SQL("""
      SELECT * FROM Game WHERE game_id = %s
    """)

		cursor = connection.cursor()
		cursor.execute(select_statement, [game_id])
		row = cursor.fetchone()
		if row:
			cols = [desc[0] for desc in cursor.description]
			game = dict(zip(cols, row))
		else:
			# explicitly mark “not found”
			cursor.close()
			return OperationResult(False, f'No game with id {game_id}', None)
		cursor.close()
		print('Game was selected')
		return OperationResult(True, 'Game', game)
	except Exception as e:
		connection.rollback()
		print(f'Error getting game: {e}')
		return OperationResult(False, 'Error getting game', e)


def get_post_finish_game_id(connection: Connection, game_id: int) -> OperationResult:
	try:
		if check_able_to_edit(connection, game_id):
			return OperationResult(False, f'No post-finish data for game id {game_id}', None)

		print('~~~Selecting Post Finish~~~')
		select_statement = SQL("""
      SELECT * FROM Game WHERE game_id = %s
    """)

		cursor = connection.cursor()
		cursor.execute(select_statement, [game_id])
		row = cursor.fetchone()
		if not row:
			cursor.close()
			return OperationResult(False, f'No game with id {game_id}', None)
		cols = [desc[0] for desc in cursor.description]
		post_finish = dict(zip(cols, row))
		cursor.close()
		print('Post Finish was selected')
		return OperationResult(True, 'post finish', post_finish)
	except Exception as e:
		connection.rollback()
		print(f'Error getting Post Finish: {e}')
		return OperationResult(False, 'Error getting Post Finish', e)


def check_able_to_edit(connection: Connection, game_id: int) -> bool:
	print('~~~Check if can be edited~~~')
	cursor = connection.cursor()

	select_statement = SQL("""
    SELECT finished_at FROM Game WHERE game_id = %s
  """)

	cursor.execute(
		select_statement,
		[game_id],
	)
	row = cursor.fetchone()
	if row:
		cols = [desc[0] for desc in cursor.description]
		game = dict(zip(cols, row))
	else:
		game = {}

	edit = game.get('finished_at') is None
	if not edit:
		print(f'~~~Game {game_id} can not be edited~~~')

	return edit


def check_connection(connection: Connection) -> bool:
	return not connection.broken and not connection.closed
