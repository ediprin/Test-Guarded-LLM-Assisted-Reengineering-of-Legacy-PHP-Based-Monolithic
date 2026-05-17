# Full Dataset Construction Status

This is the current empirical dataset status for the Rio-based PHP web-app subject pool.

## Subject Audit

All 8 primary subjects were cloned at pinned Rio-range tags/commits.

| Project | Tag | Commit | PHP requirement detected | Test command status | Initial audit candidate count |
|---|---|---|---|---|---:|
| phpMyAdmin | `RELEASE_4_9_1` | `a00f23711e33a09dd8a472bfc6f938e5ab51ced4` | `>=5.5.0` | `vendor/bin/phpunit` discovered | 784 |
| DokuWiki | `release-2018-04-22b` | `4e34491f07933bfb7e59e6cab0c029799dd381ab` | `>=5.6` | `_test/phpunit.xml` discovered | 292 |
| OpenCart | `3.0.3.2` | `4ba536198a4638b6d3902a7c720ce8503b0dc394` | `>=5.4.0` | tests directory discovered | 874 |
| phpBB | `release-3.2.2` | `77b275181aeddf43e1077d06abce11a9722bb85a` | not detected | `vendor/bin/phpunit` discovered | 988 |
| phpPgAdmin | `REL_7-12-0` | `2acc9154c720f7f3d7e9f36b9f153ca02c69bb37` | `>=5.0` | tests directory discovered | 292 |
| Roundcube | `1.4.1` | `0b1d6841f923be19cfb53de97c1a593d5752475e` | not detected | tests directory discovered | 445 |
| Kanboard | `v1.2.13` | `d983c113da13aad4c022a8832365d04d77adf3a7` | `>=5.6.0` | tests directory discovered | 500 |
| Dolibarr | `10.0.5` | `07b40f043e3992cab80e545d9cc0afdd3a0df1b4` | `>=5.3.0` | no test command discovered | 3434 |

Audit artifact: `results/summary/audit_matrix.csv`.

## Candidate Dataset

The candidate extractor produced 9,453 initial candidates across the 8 subject systems.

| Project | Initial candidates | Long/complex region | Mixed PHP/HTML | SQL/data access | Session-dependent | Form handling | Mixed PHP/HTML/SQL |
|---|---:|---:|---:|---:|---:|---:|---:|
| phpMyAdmin | 972 | 427 | 52 | 229 | 151 | 55 | 58 |
| DokuWiki | 385 | 287 | 62 | 14 | 12 | 5 | 5 |
| OpenCart | 926 | 566 | 10 | 339 | 2 | 1 | 8 |
| phpBB | 1057 | 414 | 21 | 527 | 3 | 5 | 87 |
| phpPgAdmin | 333 | 198 | 4 | 72 | 17 | 24 | 18 |
| Roundcube | 513 | 293 | 16 | 60 | 117 | 15 | 12 |
| Kanboard | 269 | 39 | 141 | 81 | 7 | 0 | 1 |
| Dolibarr | 4998 | 2329 | 414 | 1430 | 181 | 156 | 488 |
| Total | 9453 | 4553 | 720 | 2752 | 490 | 261 | 677 |

Artifacts:

- `results/summary/candidate_summary_all.csv`
- `results/subjects/<project>/candidates/candidates.csv`
- `results/subjects/<project>/evidence/*.json`

## Target Runtime Syntax Gate

Syntax gates were executed inside Docker PHP images, not the host PHP runtime.

| Project | Candidate-bearing files | Syntax pass | Syntax fail | PHP runtime | Image |
|---|---:|---:|---:|---|---|
| phpMyAdmin | 344 | 344 | 0 | 5.6.40 | `php:5.6-cli` |
| DokuWiki | 124 | 124 | 0 | 5.6.40 | `php:5.6-cli` |
| OpenCart | 470 | 470 | 0 | 5.6.40 | `php:5.6-cli` |
| phpBB | 389 | 389 | 0 | 5.6.40 | `php:5.6-cli` |
| phpPgAdmin | 79 | 79 | 0 | 5.6.40 | `php:5.6-cli` |
| Roundcube | 159 | 159 | 0 | 5.6.40 | `php:5.6-cli` |
| Kanboard | 234 | 234 | 0 | 7.2.34 | `php:7.2-cli` |
| Dolibarr | 1822 | 1822 | 0 | 5.6.40 | `php:5.6-cli` |

Artifact: `results/summary/syntax_summary_target.csv`.

## Testability Screening

No candidate is marked eligible merely from extraction. Eligibility requires stable existing or characterization oracles. The current screening status is:

| Project | Initial candidates | Needs characterization | Needs manual oracle review | Pending target PHP syntax | Eligible |
|---|---:|---:|---:|---:|---:|
| phpMyAdmin | 972 | 469 | 503 | 0 | 0 |
| DokuWiki | 385 | 79 | 306 | 0 | 0 |
| OpenCart | 926 | 25 | 901 | 0 | 0 |
| phpBB | 1057 | 163 | 894 | 0 | 0 |
| phpPgAdmin | 333 | 179 | 154 | 0 | 0 |
| Roundcube | 513 | 99 | 414 | 0 | 0 |
| Kanboard | 269 | 136 | 133 | 0 | 0 |
| Dolibarr | 4998 | 1743 | 3255 | 0 | 0 |

Artifact: `results/summary/screening_summary_all.csv`.

## Runtime Restoration and Characterization

Two subjects currently have runnable HTTP containers and passing baseline characterization checks.

| Project | Runtime status | URL | Runtime PHP | Characterization | Oracle mapping |
|---|---|---|---|---|---|
| DokuWiki | container healthy | `http://localhost:8102/doku.php` | 5.6.40 | home page PASS | 28 stable, 32 needs review, 325 pending |
| Kanboard | container healthy | `http://localhost:8107/` | 7.3.14 | login page PASS | 1 stable, 134 needs review, 134 pending |

Artifacts:

- `docker/subjects/dokuwiki/`
- `docker/subjects/kanboard/`
- `results/subjects/dokuwiki/characterization/home.csv`
- `results/subjects/dokuwiki/oracle/home_coverage.csv`
- `results/subjects/kanboard/characterization/login.csv`
- `results/subjects/kanboard/oracle/login_coverage.csv`

## Paper-Ready Interpretation

The empirical dataset is no longer synthetic at the subject, candidate, evidence, and syntax-gate levels. It now contains 8 pinned PHP web applications from the Rio et al. subject pool and 9,453 initial candidate regions with evidence artifacts.

However, the dataset is not yet a completed treatment-comparison dataset. The current results support a paper section on dataset construction, audit, candidate extraction, target-runtime syntax validation, and pilot characterization. The T1/T2/T3 treatment comparison must wait until enough candidates have stable candidate-level or route-level oracles.

Do not report accepted-and-improving transformation counts yet.
