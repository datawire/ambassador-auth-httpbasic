#!/usr/bin/env bash
TAG_NAME="$1"

# Check if the tag already exists before proceeding
#
# https://stackoverflow.com/a/17793125/364135
if git rev-parse "$TAG_NAME^{tag}" >/dev/null 2>&1; then
    echo "Tag '$TAG_NAME' already exists!"
    exit 1
fi

git tag -a "$TAG_NAME" -m "release: $TAG_NAME"
git push origin "$TAG_NAME"
