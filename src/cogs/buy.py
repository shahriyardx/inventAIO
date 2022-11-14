import datetime

from nextcord.application_command import SlashOption, slash_command
from nextcord.ext import commands
from nextcord.interactions import Interaction
from tabulate import tabulate

from ..config import default_guild_ids
from ..utils.capital import get_capital, update_capital
from ..utils.models import InventAIOModel
from ..utils.tables import get_table_embed


class Buy(commands.Cog):
    def __init__(self, bot: InventAIOModel):
        self.bot = bot

    async def send_message(self, i: Interaction, message: str):
        await i.edit_original_message(content=message, embed=None)

    @slash_command(name="bought", guild_ids=default_guild_ids)
    async def bought(
        self,
        interaction: Interaction,
        sku: str = SlashOption(description="Enter the SKU of shoe"),
        size: str = SlashOption(description="Enter size of the shoe"),
        price: float = SlashOption(
            description="Enter the price of buying", min_value=0.01
        ),
        quantity: int = SlashOption(description="Enter the buying amount", min_value=1),
        date: str = SlashOption(description="Enter the date of buying"),
        source: str = SlashOption(description="Source of buying", default=""),
        note: str = SlashOption(description="Additional Note for this buy", default=""),
    ):
        await interaction.response.defer()
        _sku = sku.strip()

        try:
            _price = float(price)
        except ValueError:
            return await self.send_message(
                interaction,
                f"Unable to convert `{price}` to a floating point number. Please enter connect price",
            )

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

        try:
            _quantity = int(quantity)
        except ValueError:
            return await self.send_message(
                interaction,
                f"Unable to convert `{quantity}` to a number. Please enter correct amount",
            )
        _size = size

        product = await self.bot.prisma.products.find_unique(where={"sku": _sku})

        if not product:
            return await self.send_message(
                interaction,
                f"Unable to find product with SKU: {_sku}. "
                "Please provide correct SKU. If the product is not on the product list, "
                "Please add it using `/product add` command",
            )

        _bought = await self.bot.prisma.buy.create(
            data={
                "product_id": product.id,
                "price": _price,
                "quantity": _quantity,
                "size": _size,
                "date": _date,
                "source": source,
                "note": note,
            }
        )

        await self.bot.prisma.products.update(
            data={"quantity": product.quantity + _quantity}, where={"sku": _sku}
        )

        capital = await get_capital(self.bot.prisma)
        total = _bought.quantity * _bought.price

        if total > capital.capital:
            total = -capital.capital

        await update_capital(self.bot.prisma, -total)

        embed = get_table_embed(
            self.bot,
            "buy",
            _bought.id,
            date,
            product.name,
            _sku,
            size,
            quantity,
            _price,
            additional_fields=[["Current Stock", product.quantity + _quantity]],
        )
        await interaction.edit_original_message(content=None, embed=embed)


def setup(bot: InventAIOModel):
    bot.add_cog(Buy(bot))
