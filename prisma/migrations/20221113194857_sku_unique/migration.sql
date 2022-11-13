/*
  Warnings:

  - A unique constraint covering the columns `[sku]` on the table `Products` will be added. If there are existing duplicate values, this will fail.

*/
-- CreateIndex
CREATE UNIQUE INDEX "Products_sku_key" ON "Products"("sku");
