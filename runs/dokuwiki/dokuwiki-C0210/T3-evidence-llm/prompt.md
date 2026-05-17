You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0210
- Project: dokuwiki
- File: inc/template.php
- Lines: 851-916
- Candidate type: long_method_or_region
- Oracle IDs: dokuwiki_home_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0210",
  "subject_id": "dokuwiki",
  "file": "inc/template.php",
  "lines": [
    851,
    916
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
function tpl_pageinfo($ret = false) {
    global $conf;
    global $lang;
    global $INFO;
    global $ID;

    // return if we are not allowed to view the page
    if(!auth_quickaclcheck($ID)) {
        return false;
    }

    // prepare date and path
    $fn = $INFO['filepath'];
    if(!$conf['fullpath']) {
        if($INFO['rev']) {
            $fn = str_replace($conf['olddir'].'/', '', $fn);
        } else {
            $fn = str_replace($conf['datadir'].'/', '', $fn);
        }
    }
    $fn   = utf8_decodeFN($fn);
    $date = dformat($INFO['lastmod']);

    // print it
    if($INFO['exists']) {
        $out = '';
        $out .= '<bdi>'.$fn.'</bdi>';
        $out .= ' · ';
        $out .= $lang['lastmod'];
        $out .= ' ';
        $out .= $date;
        if($INFO['editor']) {
            $out .= ' '.$lang['by'].' ';
            $out .= '<bdi>'.editorinfo($INFO['editor']).'</bdi>';
        } else {
            $out .= ' ('.$lang['external_edit'].')';
        }
        if($INFO['locked']) {
            $out .= ' · ';
            $out .= $lang['lockedby'];
            $out .= ' ';
            $out .= '<bdi>'.editorinfo($INFO['locked']).'</bdi>';
        }
        if($ret) {
            return $out;
        } else {
            echo $out;
            return true;
        }
    }
    return false;
}

/**
 * Prints or returns the name of the given page (current one if none given).
 *
 * If useheading is enabled this will use the first headline else
 * the given ID is used.
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 *
 * @param string $id page id
 * @param bool   $ret return content instead of printing
 * @return bool|string
 */
function tpl_pagetitle($id = null, $ret = false) {
```
