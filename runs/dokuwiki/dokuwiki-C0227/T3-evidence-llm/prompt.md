You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0227
- Project: dokuwiki
- File: lib/exe/js.php
- Lines: 219-262
- Candidate type: long_method_or_region
- Oracle IDs: dokuwiki_js_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0227",
  "subject_id": "dokuwiki",
  "file": "lib/exe/js.php",
  "lines": [
    219,
    262
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
      "value": 13
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
function js_pluginstrings() {
    global $conf, $config_cascade;
    $pluginstrings = array();
    $plugins = plugin_list();
    foreach($plugins as $p) {
        $path = DOKU_PLUGIN . $p . '/lang/';

        if(isset($lang)) unset($lang);
        if(file_exists($path . "en/lang.php")) {
            include $path . "en/lang.php";
        }
        foreach($config_cascade['lang']['plugin'] as $config_file) {
            if(file_exists($config_file . $p . '/en/lang.php')) {
                include($config_file . $p . '/en/lang.php');
            }
        }
        if(isset($conf['lang']) && $conf['lang'] != 'en') {
            if(file_exists($path . $conf['lang'] . "/lang.php")) {
                include($path . $conf['lang'] . '/lang.php');
            }
            foreach($config_cascade['lang']['plugin'] as $config_file) {
                if(file_exists($config_file . $p . '/' . $conf['lang'] . '/lang.php')) {
                    include($config_file . $p . '/' . $conf['lang'] . '/lang.php');
                }
            }
        }

        if(isset($lang['js'])) {
            $pluginstrings[$p] = $lang['js'];
        }
    }
    return $pluginstrings;
}

/**
 * Return an two-dimensional array with strings from the language file of current active template.
 *
 * - $lang['js'] must be an array.
 * - Nothing is returned for template without an entry for $lang['js']
 *
 * @param string $tpl
 * @return array
 */
function js_templatestrings($tpl) {
```
