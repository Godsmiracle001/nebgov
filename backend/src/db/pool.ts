import { Pool } from "pg";
import dotenv from "dotenv";
import { logger } from "../logger";

dotenv.config();

export const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
  allowExitOnIdle: process.env.NODE_ENV === "test",
});

pool.on("error", (err) => {
  logger.error({ err }, "Unexpected error on idle client");
  process.exit(-1);
});

export default pool;
