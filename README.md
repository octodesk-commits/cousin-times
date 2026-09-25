# The Cousin Times public site

Static daily newspaper site for `https://cousintimes.shamrock.click/ct-6f30fc5c/`.

- Source editions: `~/clawd/newspaper/mic-times-YYYY-MM-DD.html`
- Build/publish: `./scripts/publish.sh [YYYY-MM-DD]`
- Output: root `index.html` is a 404-style placeholder with no links. The paper lives at `/ct-6f30fc5c/` (`index.html` latest, `editions/` dated copies, `archive.html`).

DNS: `cousintimes.shamrock.click` should be a CNAME to `octodesk-commits.github.io`.

Privacy: this site is intentionally not indexed and the paper is behind an unguessable path. `robots.txt` disallows all crawlers, every HTML page carries `noindex, nofollow, noarchive`, and no sitemap is generated. This is obscurity, not access control.
