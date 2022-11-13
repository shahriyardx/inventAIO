from datetime import datetime

from nextcord import File
from nextcord.embeds import Embed
from nextcord.interactions import Interaction
from nextcord.ui import Modal, TextInput
from tabulate import tabulate

from .models import InventAIOModel


def date_converter(day, month, year):
    return datetime(year, month, day, 0, 0, 0, 0)


class BuySellModal(Modal):
    def __init__(self, bot: InventAIOModel, title: str, action: str):
        super().__init__(title=title)
        self.bot = bot
        self.action = action

        self.name_sku = TextInput(
            label="SKU and Name",
            min_length=1,
            required=True,
            placeholder="SKU - Name",
        )

        self.price = TextInput(
            label="Price",
            min_length=1,
            required=True,
            placeholder="Enter price",
        )

        self.size = TextInput(
            label="Size",
            min_length=1,
            required=True,
            placeholder="Enter Size",
        )

        self.quantity = TextInput(
            label="Amount",
            min_length=1,
            required=True,
            placeholder="Enter amount",
        )

        self.date = TextInput(
            label="Date (DD-MM-YYYY)",
            min_length=1,
            required=True,
            placeholder="DD-MM-YYYY",
        )

        self.add_item(self.name_sku)
        self.add_item(self.price)
        self.add_item(self.size)
        self.add_item(self.quantity)
        self.add_item(self.date)

    async def send_error(self, interaction: Interaction, message: str):
        await interaction.response.send_message(content=message)

    async def callback(self, interaction: Interaction):
        name_and_sku = self.name_sku.value.rsplit(",", maxsplit=1)

        if len(name_and_sku) < 2:
            return await self.send_error(
                interaction,
                f"Unable to find **Name** and **SKU** from `{self.name_sku.value}`. Make sure to put a command bwtween them",
            )

        shoe_sku = name_and_sku[0]
        shoe_name = name_and_sku[1]
        shoe_price = 0

        try:
            shoe_price = float(self.price.value)
        except ValueError:
            return await self.send_error(
                interaction,
                f"Unable to convert `{self.price.value}` to a floating point number. Please enter connect price",
            )

        try:
            day, month, year = self.date.value.split("-")
            day = int(day)
            month = int(month)
            year = int(year)
        except Exception as e:
            print(e)
            return await self.send_error(
                interaction,
                f"Unable to convert `{self.date.value}` to a date. Please enter date in day-month-year format",
            )

        try:
            shoe_quantity = int(self.quantity.value)
        except ValueError:
            return await self.send_error(
                interaction,
                f"Unable to convert `{self.quantity.value}` to a number. Please enter correct amount",
            )

        date = date_converter(day, month, year)

        product = await self.bot.prisma.inventory.create(
            data={
                "sku": shoe_sku,
                "shoe_name": shoe_name,
                "price": shoe_price,
                "size": self.size.value,
                "quantity": shoe_quantity,
                "action": self.action,
                "date": date,
            }
        )

        embed = Embed(
            title=f"Item {'Sold' if self.action == 'sell' else 'Bought'}",
            description="",
            color=0xFFFFFF,
        )

        table = tabulate(
            [
                ["ID", product.id],
                ["Date", f"{day}-{month}-{year}"],
                ["Name", shoe_name],
                ["SKU", shoe_sku],
                ["Size", self.size.value],
                ["Amount", shoe_quantity],
                ["Retail", shoe_price],
            ],
            tablefmt="fancy_grid",
        )

        embed.description = f"```{table.__str__()}```"
        embed.set_footer(text="You can use the ID to delete this record from database")
        embed.set_thumbnail(url=self.bot.logo)
        await interaction.response.send_message(embed=embed)
