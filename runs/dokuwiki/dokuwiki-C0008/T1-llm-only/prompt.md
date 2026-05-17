You are assisting with bounded reengineering of a legacy PHP-based monolithic web application.

Task:
Improve maintainability of the selected PHP code region while preserving observable behavior.

Candidate:
- Candidate ID: dokuwiki-C0008
- Project: dokuwiki
- File: install.php
- Lines: 254-326
- Candidate type: long_method_or_region

Rules:
- Return a unified diff only.
- Do not change public routes, request parameters, session keys, database table names, DOM selectors, or form field names.
- Do not migrate framework, architecture, database schema, or application structure.
- Keep the change local and bounded.

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
