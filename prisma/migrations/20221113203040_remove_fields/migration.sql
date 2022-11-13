/*
  Warnings:

  - You are about to drop the column `product_id` on the `Sell` table. All the data in the column will be lost.
  - You are about to drop the column `size` on the `Sell` table. All the data in the column will be lost.
  - Added the required column `buy_id` to the `Sell` table without a default value. This is not possible if the table is not empty.

*/
-- DropForeignKey
ALTER TABLE "Buy" DROP CONSTRAINT "Buy_product_id_fkey";

-- DropForeignKey
ALTER TABLE "Sell" DROP CONSTRAINT "Sell_product_id_fkey";

-- AlterTable
ALTER TABLE "Sell" DROP COLUMN "product_id",
DROP COLUMN "size",
ADD COLUMN     "buy_id" BIGINT NOT NULL;

-- AddForeignKey
ALTER TABLE "Buy" ADD CONSTRAINT "Buy_product_id_fkey" FOREIGN KEY ("product_id") REFERENCES "Products"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Sell" ADD CONSTRAINT "Sell_buy_id_fkey" FOREIGN KEY ("buy_id") REFERENCES "Buy"("id") ON DELETE CASCADE ON UPDATE CASCADE;
