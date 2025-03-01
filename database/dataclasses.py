
from dataclasses import dataclass, field, asdict


###############################################################################


@dataclass(slots=True)
class Team:
	conference: str
	division: str
	code: str
	nhlid: int
	name: str
	rowid: int | None = field(default=None)

	@property
	def as_dict(self):
		return asdict(self)


@dataclass(slots=True)
class Player:
	status: str
	name: str
	position: str
	nhlid: str
	rowid: int | None = field(default=None)

	@property
	def as_dict(self):
		return asdict(self)


@dataclass(slots=True)
class Game:
	status: str
	nhlid: int
	timestamp: str
	start_time: str
	home_team_rowid: int
	home_team_points: int
	away_team_rowid: int
	away_team_points: int
	clock: str
	rowid: int | None = field(default=None)

	@property
	def as_dict(self):
		return asdict(self)


@dataclass(slots=True)
class PStat:
	game_rowid: int
	player_rowid: int
	shots_on_goal: int
	goals: int
	assists: int
	rowid: int | None = field(default=None)

	@property
	def as_dict(self):
		return asdict(self)


###############################################################################