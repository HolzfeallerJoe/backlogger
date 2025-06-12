from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field, field_validator

NonNegativeInt = Annotated[int, Field(ge=0, description='An integer ≥ 0')]

Rating0to10 = Annotated[
	int, Field(ge=0, le=10, description='A rating between 0 and 10')
]

NonEmptyStr = Annotated[str, Field(min_length=1, description='A non-empty string')]

DurationStr = Annotated[
	str,
	Field(
		pattern=r'^\d+ (day|days|week|weeks|month|months|year|years)$',
		description="e.g. '3 days', '1 month', etc.",
	),
]


class StrippingModel(BaseModel):
	@field_validator('*', mode='before')
	@classmethod
	def _strip_all_strings(cls, v):
		if isinstance(v, str):
			return v.strip()
		return v


class Game(StrippingModel):
	game_id: Optional[int] = Field(
		None,
		description='Unique identifier assigned by the database (read-only)',
		json_schema_extra={'readOnly': True},
	)
	name: NonEmptyStr = Field(..., description='Name/title of the game')
	est_length: Optional[NonNegativeInt] = Field(
		...,
		description='Estimated playtime in hours (must be ≥ 0)',
		json_schema_extra={'readOnly': True},
	)
	released: bool = Field(
		..., description='Whether the game has been officially released'
	)
	purchased: bool = Field(
		..., description='Whether you have already purchased the game'
	)
	excitement: Rating0to10 = Field(
		..., description='How excited you are about this game (0–10)'
	)


class PostFinish(StrippingModel):
	dropped: bool = Field(
		..., description='True if the game was dropped before completion'
	)
	credits: bool = Field(..., description='True if you watched the game’s credits')
	time_played: NonNegativeInt = Field(
		..., description='Number of hours actually played (must be ≥ 0)'
	)
	duration: DurationStr = Field(
		...,
		description=(
			"Duration between start and (drop/finish), e.g., '3 days', '1 month'. "
			'Combine a number with day/week/month/year.'
		),
	)
	rating: Rating0to10 = Field(..., description='Final personal rating (0–10)')
	worth: bool = Field(..., description='True if you consider the game worth your time')
	reason: Optional[str] = Field(
		None, description='Optional explanation for everything you want'
	)
	finished_at: Optional[datetime] = Field(
		None,
		description='When the post finish stats where added',
		json_schema_extra={'readOnly': True},
	)
