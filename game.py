from typing import Annotated, Optional

from pydantic import BaseModel, Field, field_validator

NonNegativeInt = Annotated[int, Field(ge=0)]
Rating0to10   = Annotated[int, Field(ge=0, le=10)]
NonEmptyStr = Annotated[str, Field(min_length=1)]


class Game(BaseModel):
	@field_validator('*', mode='before')
	@classmethod
	def _strip_all_strings(cls, v):
		if isinstance(v, str):
			return v.strip()
		return v
	
	game_id: int | None = None
	name: NonEmptyStr
	est_length: NonNegativeInt
	released: bool
	purchased: bool
	excitement: Rating0to10


class PostFinishGame(Game):
	dropped: bool
	credits: bool
	time_played: NonNegativeInt
	duration: str  # put together via a number and then day/week/month/year
	rating: Rating0to10
	worth: bool
	reason: Optional[str]
