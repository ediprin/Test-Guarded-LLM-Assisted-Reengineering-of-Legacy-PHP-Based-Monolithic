You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0207
- Project: dokuwiki
- File: inc/template.php
- Lines: 576-634
- Candidate type: long_method_or_region
- Oracle IDs: dokuwiki_home_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0207",
  "subject_id": "dokuwiki",
  "file": "inc/template.php",
  "lines": [
    576,
    634
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
    "dom_selectors": [
      ".\\\\dokuwiki\\\\Menu\\\\Item\\\\"
    ],
    "forms": []
  },
  "protected_constraints": {
    "must_preserve_request_parameters": [],
    "must_preserve_session_keys": [],
    "must_preserve_database_tables": [],
    "must_preserve_dom_selectors": [
      ".\\\\dokuwiki\\\\Menu\\\\Item\\\\"
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
function tpl_get_action($type) {
    dbg_deprecated('see devel:menus');
    if($type == 'history') $type = 'revisions';
    if($type == 'subscription') $type = 'subscribe';
    if($type == 'img_backto') $type = 'imgBackto';

    $class = '\\dokuwiki\\Menu\\Item\\' . ucfirst($type);
    if(class_exists($class)) {
        try {
            /** @var \dokuwiki\Menu\Item\AbstractItem $item */
            $item = new $class;
            $data = $item->getLegacyData();
            $unknown = false;
        } catch(\RuntimeException $ignored) {
            return false;
        }
    } else {
        global $ID;
        $data = array(
            'accesskey' => null,
            'type' => $type,
            'id' => $ID,
            'method' => 'get',
            'params' => array('do' => $type),
            'nofollow' => true,
            'replacement' => '',
        );
        $unknown = true;
    }

    $evt = new Doku_Event('TPL_ACTION_GET', $data);
    if($evt->advise_before()) {
        //handle unknown types
        if($unknown) {
            $data = '[unknown %s type]';
        }
    }
    $evt->advise_after();
    unset($evt);

    return $data;
}

/**
 * Wrapper around tpl_button() and tpl_actionlink()
 *
 * @author Anika Henke <anika@selfthinker.org>
 *
 * @param string        $type action command
 * @param bool          $link link or form button?
 * @param string|bool   $wrapper HTML element wrapper
 * @param bool          $return return or print
 * @param string        $pre prefix for links
 * @param string        $suf suffix for links
 * @param string        $inner inner HTML for links
 * @return bool|string
 * @deprecated 2017-09-01 see devel:menus
 */
function tpl_action($type, $link = false, $wrapper = false, $return = false, $pre = '', $suf = '', $inner = '') {
```
