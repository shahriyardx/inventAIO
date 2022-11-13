import datetime

from nextcord.application_command import SlashOption, slash_command
from nextcord.embeds import Embed
from nextcord.ext import commands
from nextcord.interactions import Interaction

from ..config import default_guild_ids
from ..utils.models import InventAIOModel


class Buy(commands.Cog):
    def __init__(self, bot: InventAIOModel):
        self.bot = bot

    async def send_message(self, i: Interaction, message: str):
        await i.edit_original_message(content=message, embed=None)

    @slash_command(name="profit", guild_ids=default_guild_ids)
    async def profit(self, _: Interaction):
        pass

    @profit.subcommand(name="month")
    async def month(
        self,
        interaction: Interaction,
        month: int = SlashOption(
            name="month",
            description="Select the month you want to check porofit",
            choices={
                "January": 1,
                "February": 2,
                "March": 3,
                "April": 4,
                "May": 5,
                "June": 6,
                "July": 7,
                "August": 8,
                "September": 9,
                "October": 10,
                "November": 11,
                "December": 12,
            },
        ),
        year: int = SlashOption(name="year", description="Enter the year"),
    ):
        await interaction.response.defer()
        max_dates = {
            1: ["January", 31],
            2: ["February", 28],
            3: ["March", 31],
            4: ["April", 30],
            5: ["May", 31],
            6: ["June", 30],
            7: ["July", 31],
            8: ["August", 31],
            9: ["September", 30],
            10: ["October", 31],
            11: ["November", 30],
            12: ["December", 31],
        }

        start = datetime.datetime(year, month, 1, 0, 0, 0, 0)
        end = datetime.datetime(year, month, max_dates[month][1], 23, 59, 59, 0)

        entries = await self.bot.prisma.inventory.find_many(
            where={"date": {"gte": start, "lte": end}}
        )

        sold = 0
        bought = 0
        sold_price = 0
        bought_price = 0

        for entry in entries:
            if entry.action == "sell":
                sold += entry.quantity
                sold_price += entry.sold_price * entry.quantity
            else:
                bought += entry.quantity
                bought_price += entry.bought_price * entry.quantity

        embed = Embed(title=f"Profit of {max_dates[month][0]}, {year}", description="")
        embed.description += f"Total shoes sold: {sold} - ${sold_price}\n"
        embed.description += f"Total shoes bought: {bought} - ${bought_price}\n"
        embed.description += f"Profit: {sold_price - bought_price}"

        embed.set_thumbnail(url=self.bot.logo)
        return await interaction.followup.send(embed=embed)

    @profit.subcommand(name="year", description="Show profit of a year")
    async def year(
        self,
        interaction: Interaction,
        year: int = SlashOption(
            name="year", description="Enter the year", min_value=2000, max_value=3000
        ),
    ):
        pass


def setup(bot: InventAIOModel):
    bot.add_cog(Buy(bot))
