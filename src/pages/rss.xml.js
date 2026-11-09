import rss from "@astrojs/rss";
import { getCollection } from "astro:content";

export async function GET(context) {
  const items = (await getCollection("articles")).sort((a, b) => b.data.published_at - a.data.published_at);
  return rss({
    title: "Ltalia Online",
    description: "Il portale (quasi) di tutti gli italiani. Satira.",
    site: context.site,
    items: items.map((a) => ({
      title: a.data.title,
      description: a.data.description,
      pubDate: a.data.published_at,
      link: `/articoli/${a.id}/`,
    })),
  });
}
