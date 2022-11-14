from nextcord.application_command import SlashOption, slash_command
from nextcord.ext import commands
from nextcord.interactions import Interaction

from ..config import currency, default_guild_ids
from ..utils.capital import get_capital, update_capital
from ..utils.models import InventAIOModel


class Capital(commands.Cog):
    def __init__(self, bot: InventAIOModel):
        self.bot = bot

    async def send_message(self, i: Interaction, message: str):
        await i.edit_original_message(content=message, embed=None)

    @slash_command(guild_ids=default_guild_ids, description="See your capital")
    async def capital(self, i: Interaction):
        pass

    @capital.subcommand()
    async def check(self, interaction: Interaction):
        await interaction.response.defer()
        capital = await get_capital(self.bot.prisma)
        await interaction.followup.send(
            content=f"Your capital is: **{capital.capital} {currency}**"
        )

    @capital.subcommand(description="Set your capital")
    async def set(
        self,
        interaction: Interaction,
        amount: float = SlashOption(description=f"Amount to set in {currency}"),
    ):
        await interaction.response.defer()
        capital = await get_capital(self.bot.prisma)

        new_cap = await update_capital(self.bot.prisma, -capital.capital)
        new_cap = await update_capital(self.bot.prisma, amount)

        await interaction.followup.send(
            content=f"Capital set to: **{new_cap.capital} {currency}**"
        )

    @capital.subcommand(description="Increase your capital")
    async def increase(
        self,
        interaction: Interaction,
        amount: float = SlashOption(description=f"Amount to increase in {currency}"),
    ):
        await interaction.response.defer()
        new_cap = await update_capital(self.bot.prisma, amount)

        await interaction.followup.send(
            content=f"Capital is now: **{new_cap.capital} {currency}**"
        )

    @capital.subcommand(description="Decrease your capital")
    async def decrease(
        self,
        interaction: Interaction,
        amount: float = SlashOption(description=f"Amount to decrease in {currency}"),
    ):
        await interaction.response.defer()
        new_cap = await update_capital(self.bot.prisma, -amount)

        await interaction.followup.send(
            content=f"Capital is now: **{new_cap.capital} {currency}**"
        )


def setup(bot: InventAIOModel):
    bot.add_cog(Capital(bot))
