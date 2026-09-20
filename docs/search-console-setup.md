# Google Search Console setup - location-potential-europe (exact steps)

The site is on github.io, so DNS verification is not available. Use the
URL-prefix property + HTML tag method. Only Millan can do the Google login.

1. Go to https://search.google.com/search-console and sign in with the Google
   account that should own the property.
2. Choose "URL prefix" (right column) and enter exactly:
   https://millantr97.github.io/location-potential-europe/
3. Google shows verification methods. Pick "HTML tag" and copy the meta tag,
   which looks like:
   <meta name="google-site-verification" content="ABC123...">
4. Send that tag to Instinct (or paste it yourself): it goes in the <head> of
   index.html (hub) only, then push. The placeholder line is marked in
   index.html with: <!-- SEARCH-CONSOLE-VERIFICATION -->
5. Back in Search Console, click "Verify".
6. Submit the sitemap: left menu -> Sitemaps -> add:
   sitemap.xml   (full URL: https://millantr97.github.io/location-potential-europe/sitemap.xml)
   The sitemap covers every city page, article, ranking, language version and
   tool page, and is regenerated whenever new pages ship.
7. In "Settings -> Users and permissions", no action needed unless a second
   person should see it.

What to watch after 2-4 weeks
- Coverage: "Page with redirect" notices were previously reported - the
  canonicals all point at the https trailing-slash URLs, so these should
  resolve as Google recrawls.
- Performance: expect the smaller-city pages (thin competition) and the
  concept ranking pages to index first; the hub follows.
- Queries: track "location potential", "best streets for X in [city]",
  "top 10 concepts in [city]", "open a business in [country]".

Also recommended (same login): Bing Webmaster Tools - it can import the
verified Search Console property and sitemap in one click.
