You are assisting with bounded reengineering of a legacy PHP-based monolithic web application.

Task:
Improve maintainability of the selected PHP code region while preserving observable behavior.

Candidate:
- Candidate ID: dokuwiki-C0227
- Project: dokuwiki
- File: lib/exe/js.php
- Lines: 219-262
- Candidate type: long_method_or_region

Rules:
- Return a unified diff only.
- Do not change public routes, request parameters, session keys, database table names, DOM selectors, or form field names.
- Do not migrate framework, architecture, database schema, or application structure.
- Keep the change local and bounded.

Code region:
```php
function js_pluginstrings() {
    global $conf, $config_cascade;
    $pluginstrings = array();
    $plugins = plugin_list();
    foreach($plugins as $p) {
        $path = DOKU_PLUGIN . $p . '/lang/';

        if(isset($lang)) unset($lang);
        if(file_exists($path . "en/lang.php")) {
            include $path . "en/lang.php";
        }
        foreach($config_cascade['lang']['plugin'] as $config_file) {
            if(file_exists($config_file . $p . '/en/lang.php')) {
                include($config_file . $p . '/en/lang.php');
            }
        }
        if(isset($conf['lang']) && $conf['lang'] != 'en') {
            if(file_exists($path . $conf['lang'] . "/lang.php")) {
                include($path . $conf['lang'] . '/lang.php');
            }
            foreach($config_cascade['lang']['plugin'] as $config_file) {
                if(file_exists($config_file . $p . '/' . $conf['lang'] . '/lang.php')) {
                    include($config_file . $p . '/' . $conf['lang'] . '/lang.php');
                }
            }
        }

        if(isset($lang['js'])) {
            $pluginstrings[$p] = $lang['js'];
        }
    }
    return $pluginstrings;
}

/**
 * Return an two-dimensional array with strings from the language file of current active template.
 *
 * - $lang['js'] must be an array.
 * - Nothing is returned for template without an entry for $lang['js']
 *
 * @param string $tpl
 * @return array
 */
function js_templatestrings($tpl) {
```
