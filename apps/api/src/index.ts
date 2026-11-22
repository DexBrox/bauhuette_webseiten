import { createApp } from "./app";
import { connectNeon } from "./db/connection";

// Entry point for Cloudflare Workers
export default createApp((env) => connectNeon(env.DATABASE_URL));
