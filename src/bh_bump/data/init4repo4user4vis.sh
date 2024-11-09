#!/usr/bin/env bash
repo=$1
user=$2
vis=$3
echo repo: $repo
echo user: $user
echo vis: $vis
[ -d .git ] || git init
git log > /dev/null 2> /dev/null || {
    # not yet committed.
    uv sync
    uv lock
    git add .bumpversion.cfg
    git add pyproject.toml
    git commit -m "initial commit"
}
gh repo create $repo $vis
git remote add origin git@github.com:${user}/${repo}.git
git branch -M main
git push -u origin main
uv run bh.bump patch
