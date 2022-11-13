import datetime
from nextcord.application_command import slash_command, SlashOption
from nextcord.ext import commands
from nextcord.interactions import Interaction

from ..config import default_guild_ids
from ..utils.models import InventAIOModel
from ..utils.forms import BuySellModal
from tabulate import tabulate

from nextcord.embeds import Embed
from prisma.models import Inventory


class Inventory(commands.Cog):
    def __init__(self, bot: InventAIOModel):
        self.bot = bot

    async def send_error(self, interaction: Interaction, message: str):
        await interaction.response.edit_message(content=message, embed=None)

    def get_table_embed(
        self, action, pid, date, name, sku, size, quantity, buy_price, sell_price=None
    ):
        data = [
            ["ID", pid],
            ["Date", date],
            ["Name", name],
            ["SKU", sku],
            ["Size", size],
            ["Amount", quantity],
            ["Bought Price", buy_price],
        ]

        if sell_price:
            data.append(["Sold Price", sell_price])

        table = tabulate(
            data,
            tablefmt="fancy_grid",
        )

        embed = Embed(
            title=f"Item {'Sold' if action == 'sell' else 'Bought'}",
            description="",
            color=0xFFFFFF,
        )

        embed.description = f"```{table.__str__()}```"
        embed.set_footer(text="You can use the ID to delete this record from database")
        embed.set_thumbnail(url=self.bot.logo)

        return embed

    @slash_command(name="bought", guild_ids=default_guild_ids)
    async def bought(
        self,
        interaction: Interaction,
        shoe_name: str = SlashOption(name="shoe_name", description="Name of the shoe"),
        shoe_sku: str = SlashOption(name="shoe_sku", description="SKU of the shoe"),
        size: str = SlashOption(name="size", description="Enter size of the shoe"),
        bought_price: float = SlashOption(
            name="shoe_price", description="Price of the shoe"
        ),
        amount: int = SlashOption(name="amount", description="Enter bought amount"),
        date_bought: str = SlashOption(
            name="date_bought", description="Enter the date of bought"
        ),
    ):
        await interaction.response.defer()
        name = shoe_name.strip()
        sku = shoe_sku.strip()

        try:
            price = float(bought_price)
        except ValueError:
            return await self.send_error(
                interaction,
                f"Unable to convert `{bought_price}` to a floating point number. Please enter connect price",
            )

        try:
            day, month, year = date_bought.split("-")
            day = int(day)
            month = int(month)
            year = int(year)
            python_date = datetime.datetime(year, month, day, 0, 0, 0, 0)
        except Exception as e:
            print(e)
            return await self.send_error(
                interaction,
                f"Unable to convert `{date_bought}` to a date. Please enter date in day-month-year format",
            )

        try:
            amount = int(amount)
        except ValueError:
            return await self.send_error(
                interaction,
                f"Unable to convert `{amount}` to a number. Please enter correct amount",
            )

        product = await self.bot.prisma.inventory.create(
            data={
                "shoe_name": name,
                "sku": sku,
                "bought_price": price,
                "sold_price": None,
                "size": size,
                "quantity": amount,
                "date": python_date,
                "action": "buy",
            }
        )

        embed = self.get_table_embed(
            "buy", product.id, date_bought, name, sku, size, amount, price
        )
        await interaction.edit_original_message(embed=embed, content="")

        # @slash_command(name="sold", guild_ids=default_guild_ids)
        # async def sold(self, interaction: Interaction):
        modal = BuySellModal(self.bot, "Sold", "sell")
        await interaction.response.send_modal(modal)

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
                sold_price += entry.price * entry.quantity
            else:
                bought += entry.quantity
                bought_price += entry.price * entry.quantity

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
    bot.add_cog(Inventory(bot))
