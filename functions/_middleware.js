/* ============================================================================
   www -> apex, 301.

   www.mnwgroundworks.com and mnwgroundworks.com were both attached to the Pages
   project as active custom domains, and both answered 200 with the full site.
   Two addresses serving identical content splits ranking signals between them
   and lets either one get indexed.

   The `_redirects` file cannot fix this: Pages matches paths there, not
   hostnames, so the rule that had been sitting in it never fired. The
   zero-overhead fix is a zone-level Redirect Rule, but that needs a Cloudflare
   token with Dynamic Redirect edit on the zone, which the deploy token does not
   carry. This does the same job at the Pages edge with the permissions we have.

   Root middleware runs for every request to the project, so it stays as cheap
   as possible: one hostname comparison, then straight through to next().
   Preview deployments on *.pages.dev are left alone deliberately -- they are
   not the canonical host and should not bounce.
   ========================================================================== */

const APEX = 'mnwgroundworks.com';

export const onRequest = async (context) => {
  const url = new URL(context.request.url);

  if (url.hostname === `www.${APEX}`) {
    url.hostname = APEX;
    url.protocol = 'https:';
    url.port = '';
    return new Response(null, {
      status: 301,
      headers: {
        Location: url.toString(),
        // A permanent redirect is worth caching, but not forever: an hour keeps
        // it cheap while leaving room to change our mind without a stuck cache.
        'Cache-Control': 'public, max-age=3600',
      },
    });
  }

  return context.next();
};
