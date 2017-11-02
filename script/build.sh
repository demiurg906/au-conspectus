#!/bin/bash

# skip if build is triggered by pull request
if [ "$TRAVIS_PULL_REQUEST" == "true" ]; then
  echo "this is PR, exiting"
  exit 0
fi

# enable error reporting to the console
set -e

# cleanup "_site"
rm -rf _site
mkdir _site

# clone remote repo to "_site"
git clone "https://${GH_TOKEN}@github.com/xamgore/au-conspectus.git" --branch gh-pages ./_site

ln -s ./ast/template.html

mkdir ./input

find ./source -name '*.md' -print0 | xargs -n1 --null -t -I {} -- node ./ast/index.js {}

python ./terms/generate_html.py ./source ./_site

# mv ./source/*.html _site/

# push
cd _site
git config user.email "no-reply@github.com"
git config user.name "Travis Bot"
git add --all
git commit -a -m "Travis #$TRAVIS_BUILD_NUMBER"
git push --force origin gh-pages
