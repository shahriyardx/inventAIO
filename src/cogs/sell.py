import datetime

from nextcord.application_command import SlashOption, slash_command
from nextcord.embeds import Embed
from nextcord.ext import commands
from nextcord.interactions import Interaction
from tabulate import tabulate

from ..config import default_guild_ids
from ..utils.models import InventAIOModel


class Sell(commands.Cog):
    def __init__(self, bot: InventAIOModel):
        self.bot = bot

    async def send_message(self, i: Interaction, message: str):
        await i.edit_original_message(content=message, embed=None)

    def get_table_embed(
        self, action, pid, date, name, sku, size, quantity, buy_price, sell_price
    ):
        data = [
            ["ID", pid],
            ["Date", date],
            ["Name", name],
            ["SKU", sku],
            ["Size", size],
            ["Amount", quantity],
            ["Bought Price", buy_price],
            ["Sold Price", sell_price],
        ]

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

    @slash_command(guild_ids=default_guild_ids)
    async def sold(
        self,
        interaction: Interaction,
        bought_id: str = SlashOption(description="Enter the id of Bought"),
        sold_price: float = SlashOption(description="Enter the price of selling"),
        quantity: int = SlashOption(description="Enter the selling amount"),
        date: str = SlashOption(description="Enter the date of selling"),
        note: str = SlashOption(description="Additional Note for this buy", default=""),
    ):
        await interaction.response.defer()

        try:
            _price = float(sold_price)
        except ValueError:
            return await self.send_message(
                interaction,
                f"Unable to convert `{sold_price}` to a floating point number. Please enter connect price",
            )

        try:
            day, month, year = date.split("-")
            day, month, year = [int(day), int(month), int(year)]
            _date = datetime.datetime(year, month, day, 0, 0, 0, 0)
        except Exception as e:
            print(e)
            return await self.send_message(
                interaction,
                f"Unable to convert `{date}` to a date. Please enter date in day-month-year format",
            )

        try:
            _quantity = int(quantity)
        except ValueError:
            return await self.send_message(
                interaction,
                f"Unable to convert `{quantity}` to a number. Please enter correct amount",
            )

        bought = await self.bot.prisma.buy.find_unique(
            where={"id": bought_id}, include={"product": True}
        )

        if not bought:
            return await self.send_message(
                interaction,
                f"Unable to find bought product with id: {bought_id}. "
                "Please provide correct ID.",
            )

        _bought = await self.bot.prisma.sell.create(
            data={
                "buy_id": bought.id,
                "price": _price,
                "quantity": _quantity,
                "date": _date,
                "note": note,
            }
        )

        await self.bot.prisma.products.update(
            data={"quantity": bought.product.quantity - _quantity},
            where={"sku": bought.product.sku},
        )

        embed = self.get_table_embed(
            "sell",
            _bought.id,
            date,
            bought.product.name,
            bought.product.sku,
            bought.size,
            quantity,
            bought.price,
            _price,
        )
        await interaction.edit_original_message(content=None, embed=embed)


def setup(bot: InventAIOModel):
    bot.add_cog(Sell(bot))
