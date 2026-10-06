#!/bin/sh
set -eu

locale_dir="${DJANGO_LOCALE_DIR:-/app/locale}"
locale_seed_dir="/app/locale_seed"

mkdir -p "$locale_dir"

# A named volume hides the catalogs shipped in the image the first time it is
# mounted. Seed only an empty volume so later image rebuilds never overwrite
# translations saved by Rosetta in production.
if [ -d "$locale_seed_dir" ] && [ -z "$(find "$locale_dir" -mindepth 1 -print -quit)" ]; then
    cp -a "$locale_seed_dir"/. "$locale_dir"/
fi

# Rosetta needs to update both PO and MO files in the shared locale volume.
chmod -R u+rwX "$locale_dir"

exec "$@"
