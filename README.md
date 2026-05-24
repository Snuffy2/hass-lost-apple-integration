# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/Snuffy2/hass-lost-apple-integration/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                              |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|-------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| custom\_components/lost\_apple/\_\_init\_\_.py    |       13 |        0 |        0 |        0 |    100% |           |
| custom\_components/lost\_apple/api\_client.py     |       23 |       13 |        4 |        0 |     37% |27-31, 35-39, 43-48 |
| custom\_components/lost\_apple/config\_flow.py    |       23 |        1 |        2 |        0 |     96% |        38 |
| custom\_components/lost\_apple/const.py           |        5 |        0 |        0 |        0 |    100% |           |
| custom\_components/lost\_apple/coordinator.py     |       15 |        0 |        0 |        0 |    100% |           |
| custom\_components/lost\_apple/device\_tracker.py |       36 |        0 |        6 |        0 |    100% |           |
| custom\_components/lost\_apple/diagnostics.py     |       20 |        1 |       10 |        1 |     93% |        30 |
| custom\_components/lost\_apple/entity.py          |       49 |        6 |       16 |        6 |     82% |21, 25, 32, 35, 42, 78 |
| custom\_components/lost\_apple/repairs.py         |        1 |        1 |        0 |        0 |      0% |         3 |
| custom\_components/lost\_apple/sensor.py          |       36 |        0 |        6 |        0 |    100% |           |
| **TOTAL**                                         |  **221** |   **22** |   **44** |    **7** | **88%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/Snuffy2/hass-lost-apple-integration/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/Snuffy2/hass-lost-apple-integration/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Snuffy2/hass-lost-apple-integration/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/Snuffy2/hass-lost-apple-integration/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2FSnuffy2%2Fhass-lost-apple-integration%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/Snuffy2/hass-lost-apple-integration/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.