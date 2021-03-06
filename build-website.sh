#!/usr/bin/env bash

set -e

apt-get update
apt-get -y install git rsync

pip3 install -r docs/requirements.txt
make -C docs clean
make -C docs html

git config --global user.name "${GITHUB_ACTOR}"
git config --global user.email "${GITHUB_ACTOR}@users.noreply.github.com"

docroot=$(mktemp -d)
rsync -av "docs/_build/html/" "${docroot}/"

pushd "${docroot}" || exit 1

git init
git remote add deploy "https://token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
git checkout -b gh-pages
touch .nojekyll
msg="Updating Docs for commit ${GITHUB_SHA} from ${GITHUB_REF} by ${GITHUB_ACTOR}"
git add -A
git commit -am "${msg}"
git push deploy gh-pages --force
popd || exit 1
exit 0
