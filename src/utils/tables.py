from nextcord.embeds import Embed
from tabulate import tabulate

from .models import InventAIOModel


def get_table_embed(
    bot: InventAIOModel,
    action,
    pid,
    date,
    name,
    sku,
    size,
    quantity,
    buy_price,
    sell_price=None,
    additional_fields=[],
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

    data += additional_fields

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
    embed.set_thumbnail(url=bot.logo)

    return embed
