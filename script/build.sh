#!/bin/bash

echo "VERSIONS *********************"
node --version
python --version
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
git clone "https://${GH_TOKEN}@github.com/xamgore/au-conspectus.git" --branch gh-pages --depth=1 ./_site

( cd ./_site && git rm -rf --ignore-unmatch ./* )
( cd ./_site && rm -rf ./* )

rm -f ./_site/README.md
touch ./_site/.nojekyll

ln -s ./ast/template.html

mkdir ./input

find ./source -name '*.md' -print0 | xargs -n1 --null -t -I {} -- node ./ast/index.js {}

python ./terms/generate_html.py ./source ./_site
cp ./source/*.jpg ./source/*.png ./source/*.svg ./_site 2>/dev/null || :
mkdir -p ./_site/assets
cp ./res/*.css ./res/*.js ./_site/assets 2>/dev/null || :

# mv ./source/*.html _site/

# push
cd _site
git config user.email "no-reply@github.com"
git config user.name "Travis Bot"
git add --all
git commit --amend -m "Travis #$TRAVIS_BUILD_NUMBER"
git push --force origin gh-pages

# ssh
# echo 'Send gh-pages to mmcs server...'
# ping users.mmcs.sfedu.ru -c1
# echo sshpass -p "$USERS_PASSWD" ssh xamgore@users.mmcs.sfedu.ru '{rm -rf ./public_html; mkdir public_html;}'
# sshpass -p "$USERS_PASSWD" ssh xamgore@users.mmcs.sfedu.ru '{rm -rf ./public_html; mkdir public_html;}'
# echo sshpass -p "$USERS_PASSWD" scp -r ._site/ xamgore@users.mmcs.sfedu.ru:/home/xamgore/public_html
# sshpass -p "$USERS_PASSWD" scp -r ._site/ xamgore@users.mmcs.sfedu.ru:/home/xamgore/public_html

# sshpass -p "$USERS_PASSWD" ssh xamgore@users.mmcs.sfedu.ru '{ rm -rf ./public_html; git clone "https://github.com/xamgore/au-conspectus.git" --branch gh-pages ./public_html; }'

# telegram
cd ..

git show --name-status --oneline | tail -n +2
message=$(git show --name-status --oneline | tail -n +2 | python ./telegram/message_generator.py)
echo "$message"
TM_TOKEN="$TM_TOKEN" CHAT='-239361319' MSG="$message" node ./telegram/index
