You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0205
- Project: dokuwiki
- File: inc/template.php
- Lines: 379-418
- Candidate type: long_method_or_region
- Oracle IDs: dokuwiki_home_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0205",
  "subject_id": "dokuwiki",
  "file": "inc/template.php",
  "lines": [
    379,
    418
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
      "value": 12
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
function _tpl_metaheaders_action($data) {
    foreach($data as $tag => $inst) {
        if($tag == 'script') {
            echo "<!--[if gte IE 9]><!-->\n"; // no scripts for old IE
        }
        foreach($inst as $attr) {
            if ( empty($attr) ) { continue; }
            echo '<', $tag, ' ', buildAttributes($attr);
            if(isset($attr['_data']) || $tag == 'script') {
                if($tag == 'script' && $attr['_data'])
                    $attr['_data'] = "/*<![CDATA[*/".
                        $attr['_data'].
                        "\n/*!]]>*/";

                echo '>', $attr['_data'], '</', $tag, '>';
            } else {
                echo '/>';
            }
            echo "\n";
        }
        if($tag == 'script') {
            echo "<!--<![endif]-->\n";
        }
    }
}

/**
 * Print a link
 *
 * Just builds a link.
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 *
 * @param string $url
 * @param string $name
 * @param string $more
 * @param bool $return if true return the link html, otherwise print
 * @return bool|string html of the link, or true if printed
 */
function tpl_link($url, $name, $more = '', $return = false) {
```
