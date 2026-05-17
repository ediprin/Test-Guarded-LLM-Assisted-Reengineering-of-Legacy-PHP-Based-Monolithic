You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0228
- Project: dokuwiki
- File: lib/exe/js.php
- Lines: 262-305
- Candidate type: long_method_or_region
- Oracle IDs: dokuwiki_js_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0228",
  "subject_id": "dokuwiki",
  "file": "lib/exe/js.php",
  "lines": [
    262,
    305
  ],
  "candidate_type": "long_method_or_region",
  "issues": [
    {
      "type": "Long or Complex Region",
      "evidence": "Detected by pre-treatment heuristic extractor; join with PHPMD/PHPStan logs for final static evidence."
    },
    {
      "type": "Complexity Proxy",
      "metric": "branch_keyword_count_plus_one",
      "value": 10
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
    "Extract Method"
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
function js_templatestrings($tpl) {
    global $conf, $config_cascade;

    $path = tpl_incdir() . 'lang/';

    $templatestrings = array();
    if(file_exists($path . "en/lang.php")) {
        include $path . "en/lang.php";
    }
    foreach($config_cascade['lang']['template'] as $config_file) {
        if(file_exists($config_file . $conf['template'] . '/en/lang.php')) {
            include($config_file . $conf['template'] . '/en/lang.php');
        }
    }
    if(isset($conf['lang']) && $conf['lang'] != 'en' && file_exists($path . $conf['lang'] . "/lang.php")) {
        include $path . $conf['lang'] . "/lang.php";
    }
    if(isset($conf['lang']) && $conf['lang'] != 'en') {
        if(file_exists($path . $conf['lang'] . "/lang.php")) {
            include $path . $conf['lang'] . "/lang.php";
        }
        foreach($config_cascade['lang']['template'] as $config_file) {
            if(file_exists($config_file . $conf['template'] . '/' . $conf['lang'] . '/lang.php')) {
                include($config_file . $conf['template'] . '/' . $conf['lang'] . '/lang.php');
            }
        }
    }

    if(isset($lang['js'])) {
        $templatestrings[$tpl] = $lang['js'];
    }
    return $templatestrings;
}

/**
 * Escapes a String to be embedded in a JavaScript call, keeps \n
 * as newline
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 *
 * @param string $string
 * @return string
 */
function js_escape($string){
```
