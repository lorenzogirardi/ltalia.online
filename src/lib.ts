import { getCollection, type CollectionEntry } from "astro:content";

export type Article = CollectionEntry<"articles">;

export const CATEGORY_LABELS: Record<string, string> = {
  cronaca: "Cronaca",
  politica: "Politica",
  sport: "Sport",
  gossip: "Gossip",
  cucina: "Cucina",
  tecnologia: "Tecnologia",
  economia: "Economia",
  societa: "Società",
};

export async function allArticles(): Promise<Article[]> {
  const items = await getCollection("articles");
  return items.sort((a, b) => b.data.published_at.getTime() - a.data.published_at.getTime());
}

export const dateIt = (d: Date) =>
  d.toLocaleDateString("it-IT", { day: "numeric", month: "long", year: "numeric", timeZone: "Europe/Rome" });
