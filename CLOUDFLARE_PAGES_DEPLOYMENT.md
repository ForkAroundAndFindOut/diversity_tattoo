# Cloudflare Pages Deployment

This repository is Cloudflare Pages-ready as a committed static bundle. Cloudflare should deploy the tracked `public/` directory from Git. It should not regenerate the site from the local scrape workspace during the Cloudflare build.

## Pages Settings

- Project type: Cloudflare Pages
- Project name: `diversity-tattoo`
- Production branch: `staging`
- Framework preset: `None`
- Build command: `python3 scripts/validate_cloudflare_public.py`
- Build output directory: `public`
- Root directory: leave blank
- Environment variables: none required

Do not use `npx wrangler deploy`, `wrangler pages deploy`, `build_v1_2_content.py`, or `scripts/validate_production.py` in the Cloudflare Pages build command for this static-bundle workflow.

## Asset Source

Images, CSS, JavaScript, HTML, redirects, headers, sitemap, and site data are served from committed files under `public/`, including `public/assets/...`.

This deployment does not use Cloudflare D1, R2, Cloudflare Images, or the old live Wix site for assets. The old scraped site is only part of the local regeneration workflow.

## Local Regeneration Workflow

Run the full local workflow only on a machine that has the parent scrape workspace with `catalog/` and `site/www.diversitytattoolv.com/`.

```powershell
python build_v1_2_content.py
node --check content-render.js
node --check motion.js
python scripts/build_public_bundle.py
python scripts/validate_production.py
python scripts/validate_cloudflare_public.py
```

After local validation passes, commit the regenerated source and `public/` output to `staging`. Cloudflare Pages can then validate and deploy the committed bundle with only:

```bash
python3 scripts/validate_cloudflare_public.py
```
