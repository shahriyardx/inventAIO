import datetime

from nextcord.application_command import SlashOption, slash_command
from nextcord.embeds import Embed
from nextcord.ext import commands
from nextcord.interactions import Interaction
from prettytable import PrettyTable

from ..config import default_guild_ids
from ..utils.models import InventAIOModel

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

class Profit(commands.Cog):
    def __init__(self, bot: InventAIOModel):
        self.bot = bot

    async def send_message(self, i: Interaction, message: str):
        await i.edit_original_message(content=message, embed=None)

    async def get_report(self, start, end, title):
        boughts = await self.bot.prisma.buy.find_many(
            where={"date": {"gte": start, "lte": end}},
            include={
                "product": True
            }
        )

        solds = await self.bot.prisma.sell.find_many(
            where={"date": {"gte": start, "lte": end}},
            include={
                "buy": {
                    "include": {
                        "product": True
                    }
                }
            }
        )

        sold = 0
        bought = 0
        sold_price = 0
        bought_price = 0

        bought_table = PrettyTable(field_names=[
            "ID",
            "SKU",
            "Name",
            "Price",
            "Size",
            "Quantity",
            "Date",
        ])

        for b in boughts:
            bought += b.quantity
            bought_price += b.price * b.quantity

            bought_table.add_row([
                b.id,
                b.product.sku,
                b.product.name,
                b.price,
                b.size,
                b.quantity,
                b.date.strftime("%d-%m-%Y")
            ])
        
        for s in solds:
            sold += s.quantity
            sold_price += s.price * s.quantity

        print(bought_table.get_csv_string())

        embed = Embed(title=title, description="")
        embed.description += f"**Total sold:** {sold} - ${sold_price}\n"
        embed.description += f"**Total bought:** {bought} - ${bought_price}\n"
        embed.description += f"**Profit:** {sold_price - bought_price}"

        embed.set_thumbnail(url=self.bot.logo)

        return embed

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
        
        start = datetime.datetime(year, month, 1, 0, 0, 0, 0)
        end = datetime.datetime(year, month, max_dates[month][1], 23, 59, 59, 0)

        embed = await self.get_report(start, end, title=f"Profit of {max_dates[month][0]}, {year}")
        return await interaction.followup.send(embed=embed)

    @profit.subcommand(name="year", description="Show profit of a year")
    async def year(
        self,
        interaction: Interaction,
        year: int = SlashOption(
            name="year", description="Enter the year", min_value=2000, max_value=3000
        ),
    ):
        await interaction.response.defer()
        start = datetime.datetime(year, 1, 1, 0, 0, 0, 0)
        end = datetime.datetime(year, 12, 31, 23, 59, 59, 0)

        embed = await self.get_report(start, end, title=f"Profit of year {year}")
        return await interaction.followup.send(embed=embed)

def setup(bot: InventAIOModel):
    bot.add_cog(Profit(bot))
