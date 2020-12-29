
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-2-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->
![cppcheck-action](https://socialify.git.ci/deep5050/cppcheck-action/image?description=1&logo=https%3A%2F%2Fi.imgur.com%2FbDs8nfo.png&theme=Light)



<div align=center>
<p align=center>
<img align=center src=http://hits.dwyl.com/deep5050/cppcheck-action.svg alt=visits>
<img align=center src=https://img.shields.io/github/v/release/deep5050/cppcheck-action?style=flat-square alt=release>
</p>

</div>


## [subscribe to service updates](https://github.com/deep5050/cppcheck-action/issues/11)

> ** Please participate on this
> [poll](https://github.com/deep5050/cppcheck-action/issues/10) for a feature
> planned by me **


## What is cppcheck?

[cppcheck](https://github.com/danmar/cppcheck) is a static analysis tool for
C/C++ code. It provides unique code analysis to detect bugs and focuses on
detecting undefined behavior and dangerous coding constructs. The goal is to
have very few false positives. Cppcheck is designed to be able to analyze your
C/C++ code even if it has non-standard syntax (common in embedded projects).

## How to use?

Create `cppcheck.yml` under `.github/workflows` With the following contents

### Default configuration

```yml
name: cppcheck-action-test
on: [push]

jobs:
  build:
    name: cppcheck-test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
          
      - name: cppcheck
        uses: deep5050/cppcheck-action@main
        with:
          github_token: ${{ secrets.GITHUB_TOKEN}}
          
        
      - name: publish report    
        uses: mikeal/publish-to-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          BRANCH_NAME: 'main' # your branch name goes here
```

### Advanced configuration

```yml
name: cppcheck-action
on: [push]

jobs:
  build:
    name: cppcheck
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: cppcheck
        uses: deep5050/cppcheck-action@main
        with:
          github_token: ${{ secrets.GITHUB_TOKEN}}
          check_library:
          skip_preprocessor:
          enable:
          exclude_check:
          inconclusive:
          inline_suppression:
          force_language:
          max_ctu_depth:
          platform:
          output_file:

      - name: publish report    
        uses: mikeal/publish-to-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          BRANCH_NAME: 'main' # your branch name goes here
```

### Input options

`check_library` : `enable` Show information messages when library files have
incomplete info.

`skip_preprocessor` : `enable` Print preprocessor output on stdout and don't do
any further processing.

`enable` : Enable additional checks. The available ids are: `all`, `warning`
,`style` , `performance` , `portability` ,`information` , `unusedFunction`
,`missingInclude` . Default value is `all` if you want to enable multiple
checking at once, separate them using `,` without any blank space. example:
`style,warning,performance`.

`exclude_check` : Give a file or directory path to exclude from checking.
example: `./no_check.cpp`

`inconclusive` : `disable`, default value is `enable` . Allow that Cppcheck
reports even though the analysis is inconclusive.

`inline_suppression`: `enable` , default is `disable` . Enable inline
suppressions. Use them by placing one or more comments, like: '//
cppcheck-suppress warningId'.

`force_language` : Forces cppcheck to check all files as the given language.
Valid values are: `c`, `c++` .

`max_ctu_depth` : Max depth in whole program analysis. The default value is 2. A
larger value will mean more errors can be found but also means the analysis will
be slower. Example : `4`.

`platform` : Specifies platform specific types and sizes. The available builtin
platforms are: `unix32` ,`unix64` , `win32A` , `win32W` ,`win64` ,`avr8` ,
`native`.

`output_file` : Give a filename for the output report. Default is
`./cppcheck_report.txt`

<b> For further details check
[cppcheck documentations](http://cppcheck.sourceforge.net/manual.pdf) </b>

## License

> MIT License

> Copyright (c) 2020 Dipankar Pal

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Thanks

Icons made by
<a href="https://www.flaticon.com/authors/freepik" title="Freepik">Freepik</a>
from <a href="https://www.flaticon.com/" title="Flaticon"> www.flaticon.com</a>

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="http://badereddineouaich.herokuapp.com"><img src="https://avatars2.githubusercontent.com/u/49657842?v=4" width="100px;" alt=""/><br /><sub><b>Bader</b></sub></a><br /><a href="https://github.com/deep5050/cppcheck-action/commits?author=BaderEddineOuaich" title="Tests">⚠️</a></td>
    <td align="center"><a href="https://stefan-hagen.website"><img src="https://avatars1.githubusercontent.com/u/450800?v=4" width="100px;" alt=""/><br /><sub><b>Stefan Hagen</b></sub></a><br /><a href="#infra-sthagen" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/deep5050/cppcheck-action/commits?author=sthagen" title="Tests">⚠️</a> <a href="https://github.com/deep5050/cppcheck-action/commits?author=sthagen" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!