# Restoration Notes

## DokuWiki

- Subject: `dokuwiki`
- Selected tag: `release-2018-04-22b`
- Commit verified locally: `4e34491f07933bfb7e59e6cab0c029799dd381ab`
- Version file: `2018-04-22b "Greebo"`
- PHP requirement detected: `>=5.6`
- Database required: no
- Test command detected: `vendor/bin/phpunit -c _test/phpunit.xml`
- Quick heuristic candidate count: `292`

Docker restoration skeleton:

- `docker/subjects/dokuwiki/Dockerfile`
- `docker/subjects/dokuwiki/docker-compose.yml`
- `docker/subjects/dokuwiki/README.md`

Local build status:

- `docker compose config` passed.
- `docker compose up --build -d` passed after Docker Desktop Linux engine became available.
- Container service: `dokuwiki`
- Published URL: `http://localhost:8102/doku.php`
- Container PHP version: `5.6.40`
- HTTP smoke check: `PASS`, status `200`

Interpretation:

- DokuWiki restoration is now containerized and runnable.
- Syntax gate under target PHP passed for all candidate files: `results/syntax_dokuwiki_php56_container.csv`.
- Basic home-page characterization passed: `results/characterization_dokuwiki_home.csv`.
- DokuWiki still remains `usable_for_experiment=false` at the full subject level until candidate-level or workflow-level characterization tests are mapped to specific candidates.
