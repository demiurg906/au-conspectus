#!/bin/bash

echo "VERSIONS *********************"
pip --version
python --version
python3 --version
python3.6 --version
echo "VERSIONS *********************"

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

python3 ./terms/generate_html.py ./source ./_site
cp ./source/*.jpg ./source/*.png ./source/*.svg ./site
cp ./res/*.css ./_site/res/

# mv ./source/*.html _site/

# push
cd _site
git config user.email "no-reply@github.com"
git config user.name "Travis Bot"
git add --all
git commit -a -m "Travis #$TRAVIS_BUILD_NUMBER"
git push --force origin gh-pages
