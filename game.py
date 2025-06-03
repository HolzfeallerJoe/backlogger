from pydantic import BaseModel


class Game(BaseModel):
	game_id: int | None = None
	name: str
	est_length: int
	released: bool
	purchased: bool
	excitement: int


class PostFinishGame(Game):
	dropped: bool
	credits: bool
	time_played: int
	duration: str  # put together via a number and then day/week/month/year
	rating: int
	worth: bool
	reason: str | None = None
