You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0010
- Project: dokuwiki
- File: install.php
- Lines: 526-568
- Candidate type: session_dependent_logic
- Oracle IDs: dokuwiki_install_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0010",
  "subject_id": "dokuwiki",
  "file": "install.php",
  "lines": [
    526,
    568
  ],
  "candidate_type": "session_dependent_logic",
  "issues": [
    {
      "type": "Session-Dependent Logic",
      "evidence": "Detected by pre-treatment heuristic extractor; join with PHPMD/PHPStan logs for final static evidence."
    },
    {
      "type": "Complexity Proxy",
      "metric": "branch_keyword_count_plus_one",
      "value": 6
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
    "Extract Guard",
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
function check_functions(){
    global $error;
    global $lang;
    $ok = true;

    if(version_compare(phpversion(),'5.6.0','<')){
        $error[] = sprintf($lang['i_phpver'],phpversion(),'5.6.0');
        $ok = false;
    }

    if(ini_get('mbstring.func_overload') != 0){
        $error[] = $lang['i_mbfuncoverload'];
        $ok = false;
    }

    $funcs = explode(' ','addslashes call_user_func chmod copy fgets '.
                         'file file_exists fseek flush filesize ftell fopen '.
                         'glob header ignore_user_abort ini_get mail mkdir '.
                         'ob_start opendir parse_ini_file readfile realpath '.
                         'rename rmdir serialize session_start unlink usleep '.
                         'preg_replace file_get_contents htmlspecialchars_decode '.
                         'spl_autoload_register stream_select fsockopen pack');

    if (!function_exists('mb_substr')) {
        $funcs[] = 'utf8_encode';
        $funcs[] = 'utf8_decode';
    }

    foreach($funcs as $func){
        if(!function_exists($func)){
            $error[] = sprintf($lang['i_funcna'],$func);
            $ok = false;
        }
    }
    return $ok;
}

/**
 * Print language selection
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 */
function langsel(){
```
