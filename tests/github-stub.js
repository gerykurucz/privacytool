/**
 * In-memory stand-in for the GitHub Contents API.
 *
 * The state file lives in a public repo, so this is the only "storage" the
 * publisher has. Modelling it faithfully matters: the compare-and-swap on the
 * blob SHA is what stops two simultaneous webhooks from clobbering each other,
 * and a stub that always accepted writes would prove nothing.
 */

export function createFakeGithub(initialContent = null) {
  const calls = [];
  let content = initialContent; // string, or null = file does not exist
  let revision = 0;
  let failNextWith = null;

  const sha = () => (content === null ? null : `blob_sha_${revision}`);

  const fetchImpl = async (url, init = {}) => {
    const u = String(url);
    const method = (init.method || "GET").toUpperCase();
    calls.push({ url: u, method, body: init.body });

    if (!u.includes("api.github.com")) {
      throw new Error(`fake github received a non-GitHub URL: ${u}`);
    }
    if (!init.headers || !/^Bearer .+/.test(init.headers.Authorization || "")) {
      return new Response('{"message":"Bad credentials"}', { status: 401 });
    }
    if (failNextWith) {
      const status = failNextWith;
      failNextWith = null;
      return new Response(`{"message":"injected ${status}"}`, { status });
    }

    // GET contents
    if (method === "GET") {
      if (content === null) {
        return new Response('{"message":"Not Found"}', { status: 404 });
      }
      return new Response(
        JSON.stringify({
          name: "entitlements.json",
          path: "entitlements.json",
          sha: sha(),
          content: btoa(unescape(encodeURIComponent(content))),
          encoding: "base64",
        }),
        { status: 200, headers: { "content-type": "application/json" } }
      );
    }

    // PUT contents
    if (method === "PUT") {
      const payload = JSON.parse(init.body);
      if (payload.sha && payload.sha !== sha()) {
        // This is the compare-and-swap failing: someone else wrote in between.
        return new Response(
          JSON.stringify({
            message: "sha is not the latest version of this file — does not match",
          }),
          { status: 409 }
        );
      }
      content = Buffer.from(payload.content, "base64").toString("utf-8");
      revision += 1;
      return new Response(
        JSON.stringify({
          content: { sha: sha(), name: "entitlements.json", path: "entitlements.json" },
          commit: { sha: `commit_${revision}` },
        }),
        { status: 200, headers: { "content-type": "application/json" } }
      );
    }

    return new Response('{"message":"Not Found"}', { status: 404 });
  };

  return {
    fetch: fetchImpl,
    calls,
    /** The file as it currently stands, parsed. null when never written. */
    get content() {
      return content === null ? null : JSON.parse(content);
    },
    get raw() {
      return content;
    },
    get revisions() {
      return revision;
    },
    /** Force the next GitHub call to fail with this status. */
    failNext(status) {
      failNextWith = status;
    },
    /** Externally mutate the file, simulating a concurrent writer. */
    setExternally(text) {
      content = text;
      revision += 1;
    },
    putCalls() {
      return calls.filter((c) => c.method === "PUT");
    },
  };
}
