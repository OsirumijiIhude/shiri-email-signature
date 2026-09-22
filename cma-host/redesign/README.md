# CMA studio rebuild

Release: studio-rebuild-20260922. Canonical editable source is OsirumijiIhude/web-sites/cma/redesign. This directory is the Railway deployment mirror only.

This is a complete replacement of the old template, not an additional polish layer. The old index.html is retained solely as an original artwork registry and rollback source. The build extracts its images without re-encoding their bytes, verifies hashes, and renders site.html with site.css and site.js into /out. Runtime serves only that release.

The Docker build runs test_browser.py against the authentic artwork before publishing. A failed assertion prevents the new image from deploying. Evidence is in /__qa/report.json and /__qa/*.png; build and artwork hashes are in /build-manifest.json. Screenshots are captured before synthetic enquiry text is entered. The suite never sends email or WhatsApp messages.

Local development validation used labeled fixture images due to browser navigation restrictions: 195 assertions passed, zero failures and uncaught errors. This is not a claim that the production build has passed; inspect the Docker run for authentic-artwork results.

Google Fonts delivers Plus Jakarta Sans with a system fallback. No trackers or third-party animation runtime. Original artwork and client information remain the client's. The form prepares email locally; it does not send an enquiry to a server.
