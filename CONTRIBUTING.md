# Contributing (60 seconds)

1. Add one row to `data/course_catalog.csv`: `id,title,provider,url`.
   - `id`: next serial number (e.g. `354` after `353`).
   - `url`: must be `https://` and unique.
   - Keep the exact header `id,title,provider,url`.
2. Regenerate: `python3 scripts/build_readme.py`
3. Check: row counts reconcile (script asserts 353+ unique ids) and your course appears once in a track + once in the provider index.
4. Commit both files with message `data: add <course title> (<provider>)`.

Please only submit courses that are **free** and grant a **certificate** on completion. No affiliates, no paywalls.
