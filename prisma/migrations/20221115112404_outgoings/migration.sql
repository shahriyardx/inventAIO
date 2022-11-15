-- CreateTable
CREATE TABLE "Outgoings" (
    "id" BIGSERIAL NOT NULL,
    "amount" DOUBLE PRECISION NOT NULL,
    "where" TEXT NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "Outgoings_id_key" ON "Outgoings"("id");
