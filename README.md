# cppcheck-action

A github action to perform C/C++ code analysis and get report back to master branch.

## What is cppcheck?

Cppcheck is a static analysis tool for C/C++ code. It provides unique code analysis to detect bugs and focuses on detecting undefined behaviour and dangerous coding constructs.
The goal is to have very few false positives. Cppcheck is designed to be able to analyze your C/C++ code even if it has non-standard syntax (common in embedded projects).

## How to use?
Create ``cppcheck.yml`` under ``.github/workflows``
With the following contents

```yml
name: cppcheck
on: [push]

jobs:
  build:
    name: cppcheck
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: autopy-lot 
        uses: deep5050/cppcheck-action@master
        with:
          github_token: ${{ secrets.GITHUB_TOKEN}}

```
