import datetime
import random
import string

from nextcord.application_command import SlashOption, slash_command
from nextcord.embeds import Embed
from nextcord.ext import commands
from nextcord.file import File
from nextcord.interactions import Interaction

from ..config import currency, default_guild_ids
from ..tamplates.profit import template as table_template
from ..utils.capital import get_capital
from ..utils.models import InventAIOModel
from ..utils.pdf import (
    get_final_html,
    get_pdf_from_html,
    get_pdf_to_bytes,
    get_rand_name,
    get_rows_to_table,
)

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

    def get_summary(self, rows):
        template = """
            <div style="padding-top: 30px;">
                {data}
            </div>
        """

        data = ""

        for row in rows:
            data += f"""<p style="font-size: 20px;"><span style="font-weight: bold">{row[0]}</span>: {row[1]}</p>"""
        return template.replace("{data}", data)

    async def get_report(self, start, end, embed_title, pdf_title):
        boughts = await self.bot.prisma.buy.find_many(
            where={"date": {"gte": start, "lte": end}}, include={"product": True}
        )

        solds = await self.bot.prisma.sell.find_many(
            where={"date": {"gte": start, "lte": end}},
            include={"buy": {"include": {"product": True}}},
        )

        bought_data = []
        sold_data = []

        sold = 0
        bought = 0
        sold_price = 0
        bought_price = 0

        for b in boughts:
            bought += b.quantity
            bought_price += b.price * b.quantity

            bought_data.append(
                [
                    b.id,
                    b.date.strftime("%d-%m-%Y"),
                    b.product.name,
                    b.product.sku,
                    b.size,
                    b.quantity,
                    b.price,
                ]
            )

        for s in solds:
            sold += s.quantity
            sold_price += s.price * s.quantity

            sold_data.append(
                [
                    s.id,
                    s.date.strftime("%d-%m-%Y"),
                    s.buy.product.name,
                    s.buy.product.sku,
                    s.buy.size,
                    s.quantity,
                    s.buy.price,
                    s.price,
                    s.quantity * s.price - s.buy.price * s.quantity,
                ]
            )

        bought_headers = ["ID", "Date", "Name", "SKU", "Size", "Quantity", "Price"]
        sold_headers = [
            "ID",
            "Date",
            "Name",
            "SKU",
            "Size",
            "Quantity",
            "Bought Price",
            "Sold Price",
            "Profit",
        ]

        bought_table = get_rows_to_table(
            bought_data, "Bought", table_headers=bought_headers
        )
        sold_table = get_rows_to_table(
            sold_data, "Sold", table_headers=sold_headers, styles="padding-top: 50px;"
        )

        profit = sold_price - bought_price
        capital = await get_capital(self.bot.prisma)
        analytics = self.get_summary(
            rows=[
                ["Total Sold", f"{sold_price} {currency}"],
                ["Total Bought", f"{bought_price} {currency}"],
                [
                    "Profit",
                    f"<span style='color: {'red' if profit < 0 else 'green'}'> {sold_price - bought_price} {currency}</span>",
                ],
                ["Capital", f"{capital.capital} {currency}"],
            ]
        )
        final_html = get_final_html(
            tables=[bought_table, sold_table],
            template=table_template,
            extra_html=analytics,
            prefix_html=f"<h1 style='text-align: center;'>{pdf_title}</h1>",
        )

        final_pdf = get_pdf_from_html(final_html)
        pdf_bytes = get_pdf_to_bytes(final_pdf)

        embed = Embed(title=embed_title, description="")
        embed.description += f"**Total sold:** {sold} - {sold_price} {currency}\n"
        embed.description += f"**Total bought:** {bought} - {bought_price} {currency}\n"
        embed.description += f"**Profit:** {sold_price - bought_price} {currency}"

        embed.set_thumbnail(url=self.bot.logo)

        return {
            "embed": embed,
            "file": pdf_bytes,
            "error": True if len(bought_data) < 1 and len(sold_data) else False,
        }

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
        year: int = SlashOption(description="Enter the year"),
    ):
        await interaction.response.defer()

        start = datetime.datetime(year, month, 1, 0, 0, 0, 0)
        end = datetime.datetime(year, month, max_dates[month][1], 23, 59, 59, 0)

        report = await self.get_report(
            start,
            end,
            embed_title=f"Profit of {max_dates[month][0]}, {year}",
            pdf_title=f"{max_dates[month][0]}, {year}",
        )

        if report["error"]:
            return await interaction.followup.send(
                content=f"No data found for the given Month and Year: {max_dates[month][0]}, {year}"
            )

        await interaction.followup.send(embed=report["embed"])
        await interaction.channel.send(
            file=File(fp=report["file"], filename=f"{get_rand_name()}.pdf")
        )

    @profit.subcommand(description="Show profit of a year")
    async def year(
        self,
        interaction: Interaction,
        year: int = SlashOption(
            description="Enter the year", min_value=2000, max_value=3000
        ),
    ):
        await interaction.response.defer()
        start = datetime.datetime(year, 1, 1, 0, 0, 0, 0)
        end = datetime.datetime(year, 12, 31, 23, 59, 59, 0)

        report = await self.get_report(
            start, end, embed_title=f"Profit Of {year}", pdf_title=f"Year {year}"
        )

        if report["error"]:
            return await interaction.followup.send(
                content=f"No data found for the given year: {2022}"
            )

        await interaction.followup.send(embed=report["embed"])
        await interaction.channel.send(
            file=File(fp=report["file"], filename=f"{get_rand_name()}.pdf")
        )


def setup(bot: InventAIOModel):
    bot.add_cog(Profit(bot))
