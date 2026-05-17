You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0007
- Project: dokuwiki
- File: install.php
- Lines: 233-254
- Candidate type: mixed_php_html
- Oracle IDs: dokuwiki_install_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0007",
  "subject_id": "dokuwiki",
  "file": "install.php",
  "lines": [
    233,
    254
  ],
  "candidate_type": "mixed_php_html",
  "issues": [
    {
      "type": "Mixed PHP/HTML",
      "evidence": "Detected by pre-treatment heuristic extractor; join with PHPMD/PHPStan logs for final static evidence."
    },
    {
      "type": "Complexity Proxy",
      "metric": "branch_keyword_count_plus_one",
      "value": 8
    }
  ],
  "dependencies": {
    "request_parameters": [],
    "session_keys": [],
    "database_tables": []
  },
  "web_contracts": {
    "dom_selectors": [],
    "forms": []
  },
  "protected_constraints": {
    "must_preserve_request_parameters": [],
    "must_preserve_session_keys": [],
    "must_preserve_database_tables": [],
    "must_preserve_dom_selectors": [],
    "must_preserve_forms": []
  },
  "allowed_transformations": [
    "Separate PHP Logic from Markup",
    "Extract View Helper"
  ],
  "test_support": {
    "existing_tests": null,
    "characterization_tests": null,
    "oracle_status": "pending"
  }
}
```

Constraints:
- Preserve all request parameters, session keys, database tables, forms, DOM selectors, and route behavior listed in the evidence.
- Use only allowed transformations from the evidence.
- Do not introduce new dependencies.
- Do not perform framework migration, database migration, or rewrite.
- Return a unified diff only.

Code region:
```php
function print_retry() {
    global $lang;
    global $LC;
    ?>
    <form action="" method="get">
      <fieldset>
        <input type="hidden" name="l" value="<?php echo $LC ?>" />
        <button type="submit"><?php echo $lang['i_retry'];?></button>
      </fieldset>
    </form>
    <?php
}

/**
 * Check validity of data
 *
 * @author Andreas Gohr
 *
 * @param array $d
 * @return bool ok?
 */
function check_data(&$d){
```
