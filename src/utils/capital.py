from prisma import Prisma


async def get_capital(prisma: Prisma):
    data = await prisma.store.find_first()

    if data:
        return data
    else:
        return await prisma.store.create(data={"capital": 0})


async def update_capital(prisma: Prisma, amount: float):
    capital = await get_capital(prisma)
    return await prisma.store.update(
        where={
            "id": capital.id,
        },
        data={"capital": capital.capital + amount},
    )
