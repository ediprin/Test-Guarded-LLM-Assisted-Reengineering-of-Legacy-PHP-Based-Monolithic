You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0082
- Project: dokuwiki
- File: inc/html.php
- Lines: 1557-1584
- Candidate type: long_method_or_region
- Oracle IDs: dokuwiki_home_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0082",
  "subject_id": "dokuwiki",
  "file": "inc/html.php",
  "lines": [
    1557,
    1584
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
      "value": 11
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
function html_softbreak_callback($match){
    // if match is an html tag, return it intact
    if ($match[0]{0} == '<') return $match[0];

    // its a long string without a breaking character,
    // make certain characters into breaking characters by inserting a
    // breaking character (zero length space, U+200B / #8203) in front them.
    $regex = <<< REGEX
(?(?=                                 # start a conditional expression with a positive look ahead ...
&\#?\\w{1,6};)                        # ... for html entities - we don't want to split them (ok to catch some invalid combinations)
&\#?\\w{1,6};                         # yes pattern - a quicker match for the html entity, since we know we have one
|
[?/,&\#;:]                            # no pattern - any other group of 'special' characters to insert a breaking character after
)+                                    # end conditional expression
REGEX;

    return preg_replace('<'.$regex.'>xu','\0&#8203;',$match[0]);
}

/**
 * show warning on conflict detection
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 *
 * @param string $text
 * @param string $summary
 */
function html_conflict($text,$summary){
```
