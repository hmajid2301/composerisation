# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]


## [0.1.2-beta.1] - 2021-03-17
### Changed
- New website for demo. Looks a lot cleaner inspired by https://api-platform.com/. 
- README we also support docker-compose version `3.8`.

## [0.1.1-beta.1] - 2020-04-03
### Changed
- Copy to clipboard after converting on the demo website.

### Fixed
- Double quotes instead of single quotes in the Docker CLI commands so we can reference environment variables.
- Ordering of deletion of `docker network`.

## [0.1.0-beta.4] - 2020-04-02
### Added
- `appengine_config.py` to import installed python dependencies.
- Version tags to `cli.py` and `Dockerfile`.
- Favicons to website.
- New app logo.

### Changed
- Added an extra whitespace at before "# Start Commands". This helps with rendering on website.
- Docker example updated.

### Fixed
- Prism not rendering after AJAX request/response on demo website.
- Fixed indented first line in Docker CLI block.
- Deploy website correctly, install pip dependencies first in lib.
- Missing `rst` description in `setup.py`.

### Removed
- Example `docker-compose.yml` from root.

## [0.1.0-beta.3] - 2020-03-31
### Changed
- From Heroku to Google App Engine, because we can use a custom domain for free.

### Fixed
- Getting stuck when listening to stdin.

## [0.1.0-beta.2] - 2020-03-30
### Added
- Added heroku to deploy the website to.

## [0.1.0-beta.1] - 2020-03-30
### Added
- Initial Release.
- Convert docker-compose to Docker CLI syntax.

[Unreleased]: https://gitlab.com/hmajid2301/composerisation/-/compare/release%2F0.1.2-beta.1...master
[0.1.2-beta.1]: https://gitlab.com/hmajid2301/composerisation/-/tags/release%2F0.1.2-beta.1...release%2F0.1.1-beta.1
[0.1.1-beta.1]: https://gitlab.com/hmajid2301/composerisation/-/tags/release%2F0.1.1-beta.1...release%2F0.1.0-beta.4
[0.1.0-beta.4]: https://gitlab.com/hmajid2301/composerisation/-/tags/release%2F0.1.0-beta.3...release%2F0.1.0-beta.2
[0.1.0-beta.3]: https://gitlab.com/hmajid2301/composerisation/-/tags/release%2F0.1.0-beta.3...release%2F0.1.0-beta.2
[0.1.0-beta.2]: https://gitlab.com/hmajid2301/composerisation/-/tags/release%2F0.1.0-beta.2...release%2F0.1.0-beta.1
[0.1.0-beta.1]: https://gitlab.com/hmajid2301/composerisation/-/tags/release%2F0.1.0-beta.1
