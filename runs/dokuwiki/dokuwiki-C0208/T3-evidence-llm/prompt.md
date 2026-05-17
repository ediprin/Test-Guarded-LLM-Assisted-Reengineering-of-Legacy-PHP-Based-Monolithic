You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0208
- Project: dokuwiki
- File: inc/template.php
- Lines: 721-769
- Candidate type: long_method_or_region
- Oracle IDs: dokuwiki_home_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0208",
  "subject_id": "dokuwiki",
  "file": "inc/template.php",
  "lines": [
    721,
    769
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
    "dom_selectors": [
      ".bchead",
      ".bcsep",
      ".breadcrumbs",
      ".curid"
    ],
    "forms": []
  },
  "protected_constraints": {
    "must_preserve_request_parameters": [],
    "must_preserve_session_keys": [],
    "must_preserve_database_tables": [],
    "must_preserve_dom_selectors": [
      ".bchead",
      ".bcsep",
      ".breadcrumbs",
      ".curid"
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
function tpl_breadcrumbs($sep = null, $return = false) {
    global $lang;
    global $conf;

    //check if enabled
    if(!$conf['breadcrumbs']) return false;

    //set default
    if(is_null($sep)) $sep = '•';

    $out='';

    $crumbs = breadcrumbs(); //setup crumb trace

    $crumbs_sep = ' <span class="bcsep">'.$sep.'</span> ';

    //render crumbs, highlight the last one
    $out .= '<span class="bchead">'.$lang['breadcrumb'].'</span>';
    $last = count($crumbs);
    $i    = 0;
    foreach($crumbs as $id => $name) {
        $i++;
        $out .= $crumbs_sep;
        if($i == $last) $out .= '<span class="curid">';
        $out .= '<bdi>' . tpl_link(wl($id), hsc($name), 'class="breadcrumbs" title="'.$id.'"', true) .  '</bdi>';
        if($i == $last) $out .= '</span>';
    }
    if($return) return $out;
    print $out;
    return $out ? true : false;
}

/**
 * Hierarchical breadcrumbs
 *
 * This code was suggested as replacement for the usual breadcrumbs.
 * It only makes sense with a deep site structure.
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 * @author Nigel McNie <oracle.shinoda@gmail.com>
 * @author Sean Coates <sean@caedmon.net>
 * @author <fredrik@averpil.com>
 * @todo   May behave strangely in RTL languages
 *
 * @param string $sep Separator between entries
 * @param bool   $return return or print
 * @return bool|string
 */
function tpl_youarehere($sep = null, $return = false) {
```
