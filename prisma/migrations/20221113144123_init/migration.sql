-- CreateEnum
CREATE TYPE "Action" AS ENUM ('buy', 'sell');

-- CreateTable
CREATE TABLE "Store" (
    "id" BIGINT NOT NULL,
    "capital" DOUBLE PRECISION NOT NULL
);

-- CreateTable
CREATE TABLE "Inventory" (
    "id" BIGSERIAL NOT NULL,
    "shoe_name" TEXT NOT NULL,
    "sku" TEXT NOT NULL,
    "bought_price" DOUBLE PRECISION NOT NULL,
    "sold_price" DOUBLE PRECISION NOT NULL,
    "size" TEXT NOT NULL,
    "quantity" INTEGER NOT NULL,
    "date" TIMESTAMP(3) NOT NULL,
    "action" "Action" NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "Store_id_key" ON "Store"("id");

-- CreateIndex
CREATE UNIQUE INDEX "Inventory_id_key" ON "Inventory"("id");
