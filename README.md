
![cppcheck-action](https://socialify.git.ci/chmorgan/cppcheck-action/image?description=1&logo=https%3A%2F%2Fi.imgur.com%2FbDs8nfo.png&theme=Light)


<div align=center>
<p align=center>
<p><a href=https://www.youtube.com/channel/UCHE71XuJOPKlHSxSr40u5Lw> <img alt="YouTube Channel Views" src="https://img.shields.io/youtube/channel/views/UCHE71XuJOPKlHSxSr40u5Lw?style=social"></a>
<a href=https://www.youtube.com/channel/UCHE71XuJOPKlHSxSr40u5Lw> <img alt="YouTube Channel Subscribers" src="https://img.shields.io/youtube/channel/subscribers/UCHE71XuJOPKlHSxSr40u5Lw?style=social"></a></p>
<img align=center 
src=https://img.shields.io/github/v/release/chmorgan/cppcheck-action?style=flat-square alt=release>
</p>

</div>


## What is cppcheck?

[cppcheck](https://github.com/danmar/cppcheck) is a static analysis tool for
C/C++ code. It provides unique code analysis to detect bugs and focuses on
detecting undefined behavior and dangerous coding constructs. The goal is to
have very few false positives. Cppcheck is designed to be able to analyze your
C/C++ code even if it has non-standard syntax (common in embedded projects).

## How to use?

Create `cppcheck.yml` under `.github/workflows` With the following contents

## What version of cppcheck is being used?

cppcheck v2.9 is the present vesion

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
        uses: chmorgan/cppcheck-action-jackson@main
        with:
          github_token: ${{ secrets.GITHUB_TOKEN}}        
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
        uses: chmorgan/cppcheck-action-jackson@main
        with:
          github_token: ${{ secrets.GITHUB_TOKEN}}
          check_library:
          skip_preprocessor:
          enable:
          exclude_check:
          inconclusive:
          inline_suppression:
          force_language:
          force:
          max_ctu_depth:
          platform:
          std:
          output_file:
          other_options:
```

### Input options

| Option | Value | Description | Default |
| :--- | :--- | :--- | :--- |
| **check_library**  | `enable`, `disable` | Show information messages when library files have incomplete info | `disable` |
| **skip_preprocessor** | `enable`, `disable` | Print preprocessor output on stdout and don't do any further processing | `disable` |
| **enable** | `all`, `warning`, `style`, `performance`, `portability`, `information`, `unusedFunction`, `missingInclude` | Enable additional checks. if you want to enable multiple checking at once, separate them using `,` without any blank space. example: `style,warning,performance` | `all` |
| **exclude_check** | `./path/to/ignore` | Give a file or directory path to exclude from checking. example: `./no_check.cpp` | nothing to ignore |
| **inconclusive** | `enable`, `disable` | Allow that Cppcheck reports even though the analysis is inconclusive | `enable` |
| **inline_suppression** | `enable`, `disable` | Enable inline suppressions. Use them by placing one or more comments, like: '// cppcheck-suppress warningId' | `disable` |
| **force_language** | `c`, `c++` | Forces cppcheck to check all files as the given language. Valid values are: `c`, `c++` | auto-detected |
| **force** | `enable`, `disable` | Force checking of all configurations in files | `disable` |
| **max_ctu_depth** | `number` | Max depth in whole program analysis. A larger value will mean more errors can be found but also means the analysis will be slower. example: `4` | `2` |
| **platform** | `unix32`, `unix64`, `win32A`, `win32W`, `win64`, `avr8`, `elbrus-e1cp`, `pic8`, `pic8-enhanced`, `pic16`, `mips32`, `native`, `unspecified`, | Specifies platform specific types and sizes | `unspecified` |
| **std** | `c89`, `c99`, `c11`, `c++11`, `c++14`, `c++17`, `c++20` | Set the C/C++ standard | `c11`, `c++20` |
| **output_file** | `./path/to/output/file.txt` | Give a filename for the output report | `./cppcheck_report.txt` |
| **other_options** | `--option1 --option2=value -opt3` | Any other options you want to add, separate with a space, wrong options will cause a failure. example: `--bug-hunting --verbose`| `disable` |


<b> For further details check
[cppcheck documentations](http://cppcheck.sourceforge.net/manual.pdf) </b>

## License

> MIT License

> Copyright (c) 2021 Dipankar Pal
> Copyright (c) 2022 Chris Morgan

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
