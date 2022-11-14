-- AlterTable
CREATE SEQUENCE "store_id_seq";
ALTER TABLE "Store" ALTER COLUMN "id" SET DEFAULT nextval('store_id_seq');
ALTER SEQUENCE "store_id_seq" OWNED BY "Store"."id";
