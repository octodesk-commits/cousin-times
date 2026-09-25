# The Cousin Times public site

Static daily newspaper site for `https://cousintimes.shamrock.click`.

- Source editions: `~/clawd/newspaper/mic-times-YYYY-MM-DD.html`
- Build/publish: `./scripts/publish.sh [YYYY-MM-DD]`
- Output: root `index.html` is the latest edition; dated copies live in `editions/`; archive is `archive.html`.

DNS: `cousintimes.shamrock.click` should be a CNAME to `octodesk-commits.github.io`.
