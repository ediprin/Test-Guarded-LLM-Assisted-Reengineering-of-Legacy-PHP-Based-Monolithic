You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0206
- Project: dokuwiki
- File: inc/template.php
- Lines: 520-576
- Candidate type: long_method_or_region
- Oracle IDs: dokuwiki_home_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0206",
  "subject_id": "dokuwiki",
  "file": "inc/template.php",
  "lines": [
    520,
    576
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
      ".action"
    ],
    "forms": []
  },
  "protected_constraints": {
    "must_preserve_request_parameters": [],
    "must_preserve_session_keys": [],
    "must_preserve_database_tables": [],
    "must_preserve_dom_selectors": [
      ".action"
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
function tpl_actionlink($type, $pre = '', $suf = '', $inner = '', $return = false) {
    dbg_deprecated('see devel:menus');
    global $lang;
    $data = tpl_get_action($type);
    if($data === false) {
        return false;
    } elseif(!is_array($data)) {
        $out = sprintf($data, 'link');
    } else {
        /**
         * @var string $accesskey
         * @var string $id
         * @var string $method
         * @var bool   $nofollow
         * @var array  $params
         * @var string $replacement
         */
        extract($data);
        if(strpos($id, '#') === 0) {
            $linktarget = $id;
        } else {
            $linktarget = wl($id, $params);
        }
        $caption = $lang['btn_'.$type];
        if(strpos($caption, '%s')){
            $caption = sprintf($caption, $replacement);
        }
        $akey    = $addTitle = '';
        if($accesskey) {
            $akey     = 'accesskey="'.$accesskey.'" ';
            $addTitle = ' ['.strtoupper($accesskey).']';
        }
        $rel = $nofollow ? 'rel="nofollow" ' : '';
        $out = tpl_link(
            $linktarget, $pre.(($inner) ? $inner : $caption).$suf,
            'class="action '.$type.'" '.
                $akey.$rel.
                'title="'.hsc($caption).$addTitle.'"', true
        );
    }
    if($return) return $out;
    echo $out;
    return true;
}

/**
 * Check the actions and get data for buttons and links
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 * @author Matthias Grimm <matthiasgrimm@users.sourceforge.net>
 * @author Adrian Lang <mail@adrianlang.de>
 *
 * @param string $type
 * @return array|bool|string
 * @deprecated 2017-09-01 see devel:menus
 */
function tpl_get_action($type) {
```
