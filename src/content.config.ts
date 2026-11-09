import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

export const CATEGORIES = [
  "cronaca",
  "politica",
  "sport",
  "gossip",
  "cucina",
  "tecnologia",
  "economia",
  "societa",
] as const;

const articles = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/articles" }),
  schema: z.object({
    title: z.string().min(10).max(160),
    description: z.string().min(10).max(300),
    published_at: z.coerce.date(),
    category: z.enum(CATEGORIES),
    tags: z.array(z.string()).default([]),
    featured: z.boolean().default(false),
    homepage_rank: z.number().int().positive().optional(),
    emoji: z.string().default("📰"),
    satire: z.literal(true),
    ai_assisted: z.boolean().default(true),
    sources: z.array(z.object({ name: z.string(), url: z.url() })).default([]),
    real_news_summary: z.string().optional(),
  }),
});

export const collections = { articles };
