import datetime

from nextcord.application_command import SlashOption, slash_command
from nextcord.embeds import Embed
from nextcord.ext import commands
from nextcord.file import File
from nextcord.interactions import Interaction

from ..config import currency, default_guild_ids
from ..tamplates.profit import template
from ..utils.capital import get_capital, update_capital
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


class Outgoing(commands.Cog):
    def __init__(self, bot: InventAIOModel):
        self.bot = bot

    async def send_message(self, i: Interaction, message: str, embed=None):
        await i.edit_original_message(content=message, embed=embed)

    async def get_report(self, start, end, pdf_title, embed_title):
        data = await self.bot.prisma.outgoings.find_many(
            where={"date": {"gte": start, "lte": end}}
        )
        table_data = []
        headers = ["ID", "Date", "Amount", "Where"]

        total_outgoing = 0

        for b in data:
            total_outgoing += b.amount
            table_data.append(
                [
                    b.id,
                    b.date.strftime("%d-%m-%Y"),
                    b.amount,
                    b.where,
                ]
            )
        capital = await get_capital(self.bot.prisma)

        summary = self.get_summary(
            rows=[
                ["Total Outgoings", f"{total_outgoing} {currency}"],
                ["Current Capital", f"{capital.capital} {currency}"],
            ]
        )
        table = get_rows_to_table(
            table_rows=table_data, table_title="Outgoings", table_headers=headers
        )
        html = get_final_html(
            tables=[table],
            template=template,
            extra_html=summary,
            prefix_html=f"<h1 style='text-align: center;'>{pdf_title}</h1>",
        )
        pdf = get_pdf_from_html(html)
        bytes = get_pdf_to_bytes(pdf)

        embed = Embed(title=embed_title)
        embed.description = f"**Total Outgoings:** {total_outgoing} {currency}\n**Current Capital:** {capital.capital} {currency}"

        return {"embed": embed, "file": bytes, "error": None}

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

    @slash_command(guild_ids=default_guild_ids, description="See your capital")
    async def outgoing(self, i: Interaction):
        pass

    @outgoing.subcommand(description="Add your outgoings")
    async def add(
        self,
        interaction: Interaction,
        amount: float = SlashOption(description="Enter outgoing amount"),
        where: str = SlashOption(description="Where it gone?"),
        date: str = SlashOption(description="Enter the date of selling"),
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

        data = await self.bot.prisma.outgoings.create(
            data={"where": where, "amount": amount, "date": _date}
        )

        await update_capital(self.bot.prisma, -amount)
        await self.send_message(
            interaction,
            message=f"Added outgoing to the database.\n"
            f"**ID** : {data.id}\n"
            f"**Amount** : {amount}{currency}\n"
            f"**Where** : {where}",
        )

    @outgoing.subcommand(name="month")
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
            embed_title=f"Outgoings of {max_dates[month][0]}, {year}",
            pdf_title=f"{max_dates[month][0]}, {year}",
        )

        await interaction.followup.send(embed=report["embed"])
        await interaction.channel.send(
            file=File(fp=report["file"], filename=f"{get_rand_name()}.pdf")
        )

    @outgoing.subcommand(description="Show outgoings of a year")
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
            start,
            end,
            embed_title=f"Outgoings of Year: {year}",
            pdf_title=f"Year - {year}",
        )

        await interaction.followup.send(embed=report["embed"])
        await interaction.channel.send(
            file=File(fp=report["file"], filename=f"{get_rand_name()}.pdf")
        )


def setup(bot: InventAIOModel):
    bot.add_cog(Outgoing(bot))
