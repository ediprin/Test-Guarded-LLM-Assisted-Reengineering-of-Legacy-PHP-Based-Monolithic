You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0008
- Project: dokuwiki
- File: install.php
- Lines: 254-326
- Candidate type: long_method_or_region
- Oracle IDs: dokuwiki_install_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0008",
  "subject_id": "dokuwiki",
  "file": "install.php",
  "lines": [
    254,
    326
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
    "request_parameters": [
      "submit"
    ],
    "session_keys": [],
    "database_tables": []
  },
  "web_contracts": {
    "dom_selectors": [],
    "forms": []
  },
  "protected_constraints": {
    "must_preserve_request_parameters": [
      "submit"
    ],
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
function check_data(&$d){
    static $form_default = array(
        'title'     => '',
        'acl'       => '1',
        'superuser' => '',
        'fullname'  => '',
        'email'     => '',
        'password'  => '',
        'confirm'   => '',
        'policy'    => '0',
        'allowreg'  => '0',
        'license'   => 'cc-by-sa'
    );
    global $lang;
    global $error;

    if(!is_array($d)) $d = array();
    foreach($d as $k => $v) {
        if(is_array($v))
            unset($d[$k]);
        else
            $d[$k] = (string)$v;
    }

    //autolowercase the username
    $d['superuser'] = isset($d['superuser']) ? strtolower($d['superuser']) : "";

    $ok = false;

    if(isset($_REQUEST['submit'])) {
        $ok = true;

        // check input
        if(empty($d['title'])){
            $error[] = sprintf($lang['i_badval'],$lang['i_wikiname']);
            $ok      = false;
        }
        if(isset($d['acl'])){
            if(!preg_match('/^[a-z0-9_]+$/',$d['superuser'])){
                $error[] = sprintf($lang['i_badval'],$lang['i_superuser']);
                $ok      = false;
            }
            if(empty($d['password'])){
                $error[] = sprintf($lang['i_badval'],$lang['pass']);
                $ok      = false;
            }
            elseif(!isset($d['confirm']) || $d['confirm'] != $d['password']){
                $error[] = sprintf($lang['i_badval'],$lang['passchk']);
                $ok      = false;
            }
            if(empty($d['fullname']) || strstr($d['fullname'],':')){
                $error[] = sprintf($lang['i_badval'],$lang['fullname']);
                $ok      = false;
            }
            if(empty($d['email']) || strstr($d['email'],':') || !strstr($d['email'],'@')){
                $error[] = sprintf($lang['i_badval'],$lang['email']);
                $ok      = false;
            }
        }
    }
    $d = array_merge($form_default, $d);
    return $ok;
}

/**
 * Writes the data to the config files
 *
 * @author  Chris Smith <chris@jalakai.co.uk>
 *
 * @param array $d
 * @return bool
 */
function store_data($d){
```
