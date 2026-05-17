You are assisting with bounded reengineering of a legacy PHP-based monolithic web application.

Task:
Improve maintainability of the selected PHP code region while preserving observable behavior.

Candidate:
- Candidate ID: dokuwiki-C0228
- Project: dokuwiki
- File: lib/exe/js.php
- Lines: 262-305
- Candidate type: long_method_or_region

Rules:
- Return a unified diff only.
- Do not change public routes, request parameters, session keys, database table names, DOM selectors, or form field names.
- Do not migrate framework, architecture, database schema, or application structure.
- Keep the change local and bounded.

Code region:
```php
function js_templatestrings($tpl) {
    global $conf, $config_cascade;

    $path = tpl_incdir() . 'lang/';

    $templatestrings = array();
    if(file_exists($path . "en/lang.php")) {
        include $path . "en/lang.php";
    }
    foreach($config_cascade['lang']['template'] as $config_file) {
        if(file_exists($config_file . $conf['template'] . '/en/lang.php')) {
            include($config_file . $conf['template'] . '/en/lang.php');
        }
    }
    if(isset($conf['lang']) && $conf['lang'] != 'en' && file_exists($path . $conf['lang'] . "/lang.php")) {
        include $path . $conf['lang'] . "/lang.php";
    }
    if(isset($conf['lang']) && $conf['lang'] != 'en') {
        if(file_exists($path . $conf['lang'] . "/lang.php")) {
            include $path . $conf['lang'] . "/lang.php";
        }
        foreach($config_cascade['lang']['template'] as $config_file) {
            if(file_exists($config_file . $conf['template'] . '/' . $conf['lang'] . '/lang.php')) {
                include($config_file . $conf['template'] . '/' . $conf['lang'] . '/lang.php');
            }
        }
    }

    if(isset($lang['js'])) {
        $templatestrings[$tpl] = $lang['js'];
    }
    return $templatestrings;
}

/**
 * Escapes a String to be embedded in a JavaScript call, keeps \n
 * as newline
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 *
 * @param string $string
 * @return string
 */
function js_escape($string){
```
