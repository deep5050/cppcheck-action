# cppcheck-action

A github action to perform C/C++ code analysis and get report back to master branch.

## What is cppcheck?

Cppcheck is a static analysis tool for C/C++ code. It provides unique code analysis to detect bugs and focuses on detecting undefined behaviour and dangerous coding constructs.
The goal is to have very few false positives. Cppcheck is designed to be able to analyze your C/C++ code even if it has non-standard syntax (common in embedded projects).

## How to use?
Create ``cppcheck.yml`` under ``.github/workflows``
With the following contents

```workflow

name: cppcheck-action

on:
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Install cppcheck
      run: sudo apt-get install cppcheck

    - name: generate report
      run: |
        echo checking flaws in your all c/cpp codes....
        cppcheck --inconclusive --enable=all .  --output-file=cppcheck.txt --report-progress 2>cppcheck_error.txt
    - name: Commit files
      run: |
        git add .
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git commit -m "cppcheck report added" -a
    - name: Push changes
      uses: ad-m/github-push-action@master
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}

```
