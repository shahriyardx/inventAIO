from dataclasses import dataclass

from nextcord.ext.commands import AutoShardedBot

from prisma import Prisma


@dataclass
class InventAIOModel(AutoShardedBot):
    prisma: Prisma
    logo: str
