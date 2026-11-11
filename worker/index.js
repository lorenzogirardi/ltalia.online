// Cloudflare Worker: lancia il workflow "Publish" su GitHub agli orari esatti degli slot.
// Il cron di GitHub Actions è inaffidabile (ritarda o salta le esecuzioni), questo no.
export default {
  async scheduled(_event, env) {
    const res = await fetch(
      `https://api.github.com/repos/${env.GITHUB_REPO}/actions/workflows/publish.yml/dispatches`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${env.GITHUB_TOKEN}`,
          Accept: "application/vnd.github+json",
          "User-Agent": "ltalia-online-scheduler",
        },
        body: JSON.stringify({ ref: "main" }),
      },
    );
    if (res.status !== 204) throw new Error(`dispatch fallito: ${res.status} ${await res.text()}`);
  },
};
