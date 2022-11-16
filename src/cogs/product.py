from math import ceil
from typing import List

from nextcord import ButtonStyle, Embed
from nextcord.application_command import SlashOption, slash_command
from nextcord.ext import commands, menus
from nextcord.interactions import Interaction
from prisma.models import Products
from tabulate import tabulate

from ..config import default_guild_ids
from ..utils.models import InventAIOModel


class MySource(menus.ListPageSource):
    def __init__(self, products: List[Products]):
        super().__init__(products, per_page=10)

    async def format_page(self, menu, entries: List[Products]):
        offset = menu.current_page * self.per_page
        print(self._max_pages)

        data = [["ID", "SKU", "Name"]]

        for index, product in enumerate(entries, start=offset):
            data.append([index + 1, product.sku, product.name])

        table = tabulate(
            data,
            tablefmt="fancy_grid",
        )
        embed = Embed(title="All Products")
        embed.description = f"```{table.__str__()}```"

        embed.set_footer(text=f"Page {menu.current_page + 1}/{self._max_pages}")
        return embed


class Product(commands.Cog):
    def __init__(self, bot: InventAIOModel):
        self.bot = bot

    async def send_message(self, i: Interaction, message: str):
        await i.edit_original_message(content=message, embed=None)

    @slash_command(description="Add or remove product", guild_ids=default_guild_ids)
    async def product(self, i: Interaction):
        pass

    @product.subcommand(description="Add product to the database")
    async def add(
        self,
        i: Interaction,
        name: str = SlashOption(description="Name of the product"),
        sku: str = SlashOption(description="SKU of the product"),
        brand: str = SlashOption(description="Brand of the product"),
    ):
        await i.response.defer()

        has_in_db = await self.bot.prisma.products.find_unique(where={"sku": sku})

        if has_in_db:
            return await self.send_message(
                i,
                f"A product with "
                f"SKU: `{sku}` already exists with "
                f"Name: `{has_in_db.name}`",
            )

        product = await self.bot.prisma.products.create(
            data={
                "name": name.strip(),
                "sku": sku.strip(),
                "brand": brand.strip(),
                "quantity": 0,
            }
        )

        await self.send_message(
            i, f"Product `{product.name}` has been added to the db."
        )

    @product.subcommand(description="Delete a product from database with SKU")
    async def delete(
        self, i: Interaction, sku: str = SlashOption(description="SKU of the product")
    ):
        await i.response.defer()
        await self.bot.prisma.products.delete(where={"sku": sku.strip()})

        await self.send_message(
            i, f"Product with SKU: `{sku.strip()}` has been deleted from the db."
        )

    @product.subcommand(description="See all the sku's")
    async def all(self, interaction: Interaction):
        products = await self.bot.prisma.products.find_many()

        pages = menus.ButtonMenuPages(
            source=MySource(products=products),
            clear_buttons_after=True,
            style=ButtonStyle.primary,
        )

        await pages.start(interaction=interaction)


def setup(bot: InventAIOModel):
    bot.add_cog(Product(bot))
