# Candidate Extraction Summary

## DokuWiki

Subject metadata:

- Project: `dokuwiki`
- Repository: `https://github.com/dokuwiki/dokuwiki.git`
- Selected tag: `release-2018-04-22b`
- Commit: `4e34491f07933bfb7e59e6cab0c029799dd381ab`
- Version: `2018-04-22b "Greebo"`
- Database required: no
- Baseline oracle status: `PENDING`

Generated artifacts:

- Candidate CSV: `results/candidates_dokuwiki.csv`
- Evidence JSON directory: `results/evidence/dokuwiki/`
- Extractor: `tools/extract_candidates.py`
- Syntax gate output: `results/syntax_dokuwiki_php83.csv`
- Target-container syntax gate output: `results/syntax_dokuwiki_php56_container.csv`
- Testability screening output: `results/screening_dokuwiki.csv`
- Target-container screening output: `results/screening_dokuwiki_container.csv`
- Home-page characterization output: `results/characterization_dokuwiki_home.csv`

Candidate counts:

| Candidate type | Count |
|---|---:|
| `long_method_or_region` | 287 |
| `mixed_php_html` | 62 |
| `sql_data_access` | 14 |
| `session_dependent_logic` | 12 |
| `form_handling` | 5 |
| `mixed_php_html_sql` | 5 |
| Total | 385 |

Top files by candidate count:

| File | Count |
|---|---:|
| `inc/JpegMeta.php` | 20 |
| `inc/common.php` | 16 |
| `inc/template.php` | 15 |
| `inc/media.php` | 14 |
| `inc/html.php` | 12 |
| `inc/indexer.php` | 12 |
| `inc/auth.php` | 10 |
| `inc/changelog.php` | 10 |
| `inc/parser/xhtml.php` | 10 |
| `lib/plugins/config/settings/config.class.php` | 8 |
| `inc/parser/handler.php` | 8 |
| `install.php` | 7 |
| `inc/io.php` | 7 |
| `inc/IXR_Library.php` | 7 |
| `lib/plugins/usermanager/admin.php` | 7 |

Interpretation:

- These are initial candidates, not eligible candidates.
- `oracle_status` remains `pending` for all candidates until baseline runtime checks and existing or characterization tests pass.
- The extractor uses conservative pre-treatment heuristics. Final static-analysis evidence should be joined with PHPMD, PHPStan/Psalm, PHPCPD, and syntax logs before candidates are submitted to treatments.
- No LLM transformation has been run.

Pre-treatment screening:

Initial local-PHP screening:

| Screening status | Count | Meaning |
|---|---:|---|
| `NEEDS_CHARACTERIZATION` | 59 | Candidate has an observable request/output contract but no stable oracle yet. |
| `NEEDS_MANUAL_ORACLE_REVIEW` | 211 | Candidate has no obvious extracted web contract and must be mapped to existing tests or manually characterized. |
| `PENDING_TARGET_PHP_SYNTAX` | 115 | Candidate file failed syntax under the current local PHP CLI; rerun syntax gate under the target PHP version before exclusion. |

Target-container screening:

| Screening status | Count | Meaning |
|---|---:|---|
| `NEEDS_CHARACTERIZATION` | 79 | Candidate has an observable request/output contract but no stable candidate-specific oracle yet. |
| `NEEDS_MANUAL_ORACLE_REVIEW` | 306 | Candidate has no obvious extracted web contract and must be mapped to existing tests or manually characterized. |

Syntax and runtime gate note:

- Local PHP syntax gate was run against candidate files and wrote `results/syntax_dokuwiki_php83.csv`.
- The runtime reported by the gate was PHP `8.4.14`.
- 20 of 124 candidate files failed under the local PHP CLI.
- The failures are consistent with legacy syntax such as curly-brace string/array offsets that must be evaluated under the target PHP version declared by DokuWiki (`>=5.6`) before labeling candidates unusable.
- Docker target runtime was then used for DokuWiki.
- Container PHP version: `5.6.40`.
- Target-container syntax gate passed for 124 of 124 candidate files.
- Home-page HTTP characterization passed at `http://localhost:8102/doku.php`.
