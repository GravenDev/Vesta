import datetime
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

import discord
from discord import Embed

from vesta.tables import Guild


class GameMode(Enum):
    """
    Represents a Clash of Code game mode
    """

    FASTEST = 0
    REVERSE = 1
    SHORTEST = 2


class Role(Enum):
    """
    Represents a Clash of Code player role
    """

    OWNER = 0
    STANDARD = 1


@dataclass
class ClashOfCodePlayer:
    """
    Represents a player in a Clash of Code game
    """

    name: str
    role: Role
    rank: int

    def __init__(self, **kwargs):
        """
        Initializes the object with the given data

        :param kwargs: The data to initialize the object with
        :see hydrate
        """
        self.hydrate(**kwargs)

    def hydrate(self, *,
                codingamerNickname: str,
                status: str,
                rank: Optional[int],
                **ignored) -> "ClashOfCodePlayer":
        """
        Hydrates the object with the given data

        :param codingamerNickname: The player's nickname
        :param status: The player's role
        :return: The hydrated object for chaining convenience
        """
        self.name = codingamerNickname
        self.role = Role[status.upper()] or Role.STANDARD
        self.rank = rank

        return self


@dataclass
class ClashOfCodeGame:
    """
    Represents a Clash of Code game
    """

    link: str
    started: bool
    finished: bool
    players: List[ClashOfCodePlayer]
    programming_language: List[str]
    modes: List[GameMode]
    mode: Optional[str]

    start_time: datetime.datetime
    end_time: Optional[datetime.datetime]

    def __init__(self, **kwargs):
        """
        Initializes the object with the given data
        :param kwargs: The data to initialize the object with
        :see hydrate
        """

        self.hydrate(**kwargs)

    def hydrate(self, *,
                publicHandle: str,
                started: bool,
                finished: bool,
                players: List[dict],
                programmingLanguages: List[str],
                modes: List[str],
                mode: Optional[str] = None,
                startTime: str,
                endTime: Optional[str] = None,
                **ignored) -> "ClashOfCodeGame":
        """
        Hydrates the object with the given data

        :param publicHandle: The game id
        :param started: Whether the game has started
        :param finished: Whether the game has finished
        :param players: The players in the game
        :param programmingLanguages: The programming languages used in the game
        :param modes: The possible game modes
        :param mode: The current game mode. Only defined if started is True
        :return: The hydrated object for chaining convenience
        """

        self.link = f"https://www.codingame.com/clashofcode/clash/{publicHandle}"
        self.started = started
        self.finished = finished
        self.players = [
            ClashOfCodePlayer(**player)
            for player in players
        ]
        self.programming_language = programmingLanguages
        self.modes = [
            GameMode[mode.upper()]
            for mode in modes
        ]
        self.mode = mode

        self.start_time = datetime.datetime.strptime(startTime, "%B %d, %Y, %I:%M:%S %p")
        self.end_time = datetime.datetime.strptime(endTime, "%B %d, %Y, %I:%M:%S %p") if endTime else None

        return self

    def embed(self, lang_file, guild: discord.Guild):
        emojis = {
            "True": lang_file.get("general_yes", guild),
            "False": lang_file.get("general_no", guild)
        }

        embed = Embed(
            title=lang_file.get("coc_game_title", guild),
            color=discord.Color.blurple(),
        )

        embed.add_field(name=lang_file.get("coc_started", guild),
                        value=emojis[str(self.started)],
                        inline=True)
        embed.add_field(name=lang_file.get("coc_finished", guild),
                        value=emojis[str(self.finished)],
                        inline=True)

        if not self.mode:
            embed.add_field(name=lang_file.get("coc_game_modes", guild),
                            value=' - ' + "\n - ".join(
                                [lang_file.get(f"coc_mode_{mode.name.lower()}", guild) for mode in self.modes]),
                            inline=False)
        else:
            embed.add_field(name=lang_file.get("coc_game_mode", guild),
                            value=f"`{self.mode.lower()}`",
                            inline=False)

        if not self.finished:
            embed.add_field(name=lang_file.get("coc_game_players", guild),
                            value=f"`{'`, `'.join([player.name for player in self.players])}`",
                            inline=False)

            languages = f"`{'`, `'.join(self.programming_language)}`" \
                if len(self.programming_language) >= 1 \
                else lang_file.get("coc_all_languages", guild)

            embed.add_field(name=lang_file.get("coc_game_languages", guild),
                            value=languages)
        else:
            # winner is player with the best "rank" field
            winner = sorted(self.players, key=lambda player: player.rank)[0]
            embed.add_field(name=lang_file.get("coc_game_winner", guild),
                            value=f"`{winner.name}`",
                            inline=False)

        return embed
