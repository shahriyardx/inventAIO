from nextcord.application_command import SlashOption, slash_command
from nextcord.ext import commands
from nextcord.interactions import Interaction

from ..config import default_guild_ids
from ..utils.models import InventAIOModel
from ..utils.capital import update_capital


class Management(commands.Cog):
    def __init__(self, bot: InventAIOModel):
        self.bot = bot

    async def send_message(self, i: Interaction, message: str):
        await i.edit_original_message(content=message, embed=None)

    @slash_command(guild_ids=default_guild_ids)
    async def delete(self, _: Interaction):
        pass

    @delete.subcommand(description="Delete a bought entry from database")
    async def bought(
        self,
        interaction: Interaction,
        bought_id: int = SlashOption(description="Enter bought id"),
    ):
        await interaction.response.defer()
        data = await self.bot.prisma.buy.delete(where={"id": bought_id})
        
        total = data.quantity * data.price 
        await update_capital(self.bot.prisma, total)
        
        await self.send_message(
            i=interaction,
            message=f"Bought record has been deleted with ID: {bought_id}.",
        )

    @delete.subcommand(description="Delete a sold entry from database")
    async def sold(
        self,
        interaction: Interaction,
        sold_id: int = SlashOption(description="Enter sold id"),
    ):
        await interaction.response.defer()
        data = await self.bot.prisma.sell.delete(where={"id": sold_id})

        total = data.quantity * data.price 
        await update_capital(self.bot.prisma, -total)

        await self.send_message(
            i=interaction, message=f"Sold record has been deleted with ID: {sold_id}."
        )


def setup(bot: InventAIOModel):
    bot.add_cog(Management(bot))
