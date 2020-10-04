#!/usr/bin/sh

git status
git add .
git commit -m "test"
git push heroku master
