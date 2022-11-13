/*
  Warnings:

  - You are about to drop the `Inventory` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropTable
DROP TABLE "Inventory";

-- DropEnum
DROP TYPE "Action";

-- CreateTable
CREATE TABLE "Products" (
    "id" BIGSERIAL NOT NULL,
    "sku" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "brand" TEXT NOT NULL,
    "quantity" BIGINT NOT NULL
);

-- CreateTable
CREATE TABLE "Buy" (
    "id" BIGSERIAL NOT NULL,
    "price" DOUBLE PRECISION NOT NULL,
    "size" TEXT NOT NULL,
    "quantity" INTEGER NOT NULL,
    "date" TIMESTAMP(3) NOT NULL,
    "source" TEXT,
    "note" TEXT,
    "product_id" BIGINT NOT NULL
);

-- CreateTable
CREATE TABLE "Sell" (
    "id" BIGSERIAL NOT NULL,
    "price" DOUBLE PRECISION NOT NULL,
    "size" TEXT NOT NULL,
    "quantity" INTEGER NOT NULL,
    "date" TIMESTAMP(3) NOT NULL,
    "note" TEXT,
    "product_id" BIGINT NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "Products_id_key" ON "Products"("id");

-- CreateIndex
CREATE UNIQUE INDEX "Buy_id_key" ON "Buy"("id");

-- CreateIndex
CREATE UNIQUE INDEX "Sell_id_key" ON "Sell"("id");

-- AddForeignKey
ALTER TABLE "Buy" ADD CONSTRAINT "Buy_product_id_fkey" FOREIGN KEY ("product_id") REFERENCES "Products"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Sell" ADD CONSTRAINT "Sell_product_id_fkey" FOREIGN KEY ("product_id") REFERENCES "Products"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
