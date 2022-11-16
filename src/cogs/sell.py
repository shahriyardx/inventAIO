import datetime
from typing import List

from nextcord import ButtonStyle, Embed
from nextcord.application_command import SlashOption, slash_command
from nextcord.embeds import Embed
from nextcord.ext import commands, menus
from nextcord.interactions import Interaction
from prisma.models import Sell
from tabulate import tabulate

from ..config import default_guild_ids
from ..utils.capital import update_capital
from ..utils.models import InventAIOModel
from ..utils.tables import get_table_embed


class MySource(menus.ListPageSource):
    def __init__(self, solds: List[Sell]):
        super().__init__(solds, per_page=2)

    async def format_page(self, menu, entries: List[Sell]):
        offset = menu.current_page * self.per_page

        data = [["SL", "ID", "SKU", "Name"]]

        for index, sold in enumerate(entries, start=offset):
            data.append(
                [index + 1, sold.id, sold.buy.product.sku, sold.buy.product.name]
            )

        table = tabulate(
            data,
            tablefmt="fancy_grid",
        )
        embed = Embed(title="All Sold")
        embed.description = f"```{table.__str__()}```"

        embed.set_footer(text=f"Page {menu.current_page + 1}/{self._max_pages}")
        return embed


class Sell(commands.Cog):
    def __init__(self, bot: InventAIOModel):
        self.bot = bot

    async def send_message(self, i: Interaction, message: str):
        await i.edit_original_message(content=message, embed=None)

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
            day, month, year = date.split("-")
            day, month, year = [int(day), int(month), int(year)]
            if len(str(year)) == 2:
                year = 2000 + year

            _date = datetime.datetime(year, month, day, 0, 0, 0, 0)
        except Exception as e:
            print(e)
            return await self.send_message(
                interaction,
                f"Unable to convert `{date}` to a date. Please enter date in day-month-year format",
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

        if bought.product.quantity < quantity:
            return await self.send_message(
                interaction,
                f"You only have `{bought.product.quantity}` left on the stock. Can't sell more than you have.",
            )

        _sold = await self.bot.prisma.sell.create(
            data={
                "buy_id": bought.id,
                "price": sold_price,
                "quantity": quantity,
                "date": _date,
                "note": note,
            }
        )

        await self.bot.prisma.products.update(
            data={"quantity": bought.product.quantity - quantity},
            where={"sku": bought.product.sku},
        )
        total = _sold.quantity * _sold.price
        await update_capital(self.bot.prisma, total)

        embed = get_table_embed(
            self.bot,
            "sell",
            _sold.id,
            date,
            bought.product.name,
            bought.product.sku,
            bought.size,
            quantity,
            bought.price,
            sold_price,
            additional_fields=[["Current Stock", bought.product.quantity - quantity]],
        )
        await interaction.edit_original_message(content=None, embed=embed)

    @slash_command(description="See all sold", guild_ids=default_guild_ids)
    async def sold_list(self, interaction: Interaction):
        solds = await self.bot.prisma.sell.find_many(
            order={"date": "desc"}, include={"buy": {"include": {"product": True}}}
        )

        pages = menus.ButtonMenuPages(
            source=MySource(solds=solds),
            clear_buttons_after=True,
            style=ButtonStyle.primary,
        )

        await pages.start(interaction=interaction)


def setup(bot: InventAIOModel):
    bot.add_cog(Sell(bot))
