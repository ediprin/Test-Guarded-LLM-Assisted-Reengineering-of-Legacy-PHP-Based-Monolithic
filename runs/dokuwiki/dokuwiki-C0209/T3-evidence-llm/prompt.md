You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0209
- Project: dokuwiki
- File: inc/template.php
- Lines: 769-831
- Candidate type: long_method_or_region
- Oracle IDs: dokuwiki_home_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0209",
  "subject_id": "dokuwiki",
  "file": "inc/template.php",
  "lines": [
    769,
    831
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
      "value": 16
    }
  ],
  "dependencies": {
    "request_parameters": [],
    "session_keys": [],
    "database_tables": []
  },
  "web_contracts": {
    "dom_selectors": [
      ".bchead",
      ".home"
    ],
    "forms": []
  },
  "protected_constraints": {
    "must_preserve_request_parameters": [],
    "must_preserve_session_keys": [],
    "must_preserve_database_tables": [],
    "must_preserve_dom_selectors": [
      ".bchead",
      ".home"
    ],
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
function tpl_youarehere($sep = null, $return = false) {
    global $conf;
    global $ID;
    global $lang;

    // check if enabled
    if(!$conf['youarehere']) return false;

    //set default
    if(is_null($sep)) $sep = ' » ';

    $out = '';

    $parts = explode(':', $ID);
    $count = count($parts);

    $out .= '<span class="bchead">'.$lang['youarehere'].' </span>';

    // always print the startpage
    $out .= '<span class="home">' . tpl_pagelink(':'.$conf['start'], null, true) . '</span>';

    // print intermediate namespace links
    $part = '';
    for($i = 0; $i < $count - 1; $i++) {
        $part .= $parts[$i].':';
        $page = $part;
        if($page == $conf['start']) continue; // Skip startpage

        // output
        $out .= $sep . tpl_pagelink($page, null, true);
    }

    // print current page, skipping start page, skipping for namespace index
    resolve_pageid('', $page, $exists);
    if (isset($page) && $page == $part.$parts[$i]) {
        if($return) return $out;
        print $out;
        return true;
    }
    $page = $part.$parts[$i];
    if($page == $conf['start']) {
        if($return) return $out;
        print $out;
        return true;
    }
    $out .= $sep;
    $out .= tpl_pagelink($page, null, true);
    if($return) return $out;
    print $out;
    return $out ? true : false;
}

/**
 * Print info if the user is logged in
 * and show full name in that case
 *
 * Could be enhanced with a profile link in future?
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 *
 * @return bool
 */
function tpl_userinfo() {
```
