from typing import List, Optional

from nextcord.ext import commands
from nextcord.flags import Intents

from prisma import Prisma

from .config import cogs, default_guild_ids, prefix
from .utils.models import InventAIOModel


class InventAIO(commands.AutoShardedBot):
    def __init__(
        self,
        command_prefix: str,
        intents: Intents,
        description: Optional[str] = None,
        default_guild_ids: Optional[List[int]] = None,
    ):
        super().__init__(
            command_prefix=command_prefix,
            description=description,
            intents=intents,
            default_guild_ids=default_guild_ids,
        )
        self.logo = "https://cdn.discordapp.com/attachments/976227434561163276/1041245977660620820/INVENT.png"

    async def on_ready(self):
        print(f"{self.user} is ready")

        self.prisma = Prisma()
        await self.prisma.connect()


intents = Intents.default()
intents.message_content = True
intents.members = True

bot: InventAIOModel = InventAIO(
    command_prefix=prefix,
    description="Inventory management bot",
    intents=intents,
    default_guild_ids=default_guild_ids,
)

for cog in cogs:
    try:
        bot.load_extension(f"src.cogs.{cog}")
    except Exception as e:
        print(e)
        print("Failled to load extention", e.__traceback__)
