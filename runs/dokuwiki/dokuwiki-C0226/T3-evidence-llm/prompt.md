You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0226
- Project: dokuwiki
- File: lib/exe/js.php
- Lines: 29-163
- Candidate type: long_method_or_region
- Oracle IDs: dokuwiki_js_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0226",
  "subject_id": "dokuwiki",
  "file": "lib/exe/js.php",
  "lines": [
    29,
    163
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
      "value": 19
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
function js_out(){
    global $conf;
    global $lang;
    global $config_cascade;
    global $INPUT;

    // decide from where to get the template
    $tpl = trim(preg_replace('/[^\w-]+/','',$INPUT->str('t')));
    if(!$tpl) $tpl = $conf['template'];

    // array of core files
    $files = array(
                DOKU_INC.'lib/scripts/jquery/jquery.cookie.js',
                DOKU_INC.'inc/lang/'.$conf['lang'].'/jquery.ui.datepicker.js',
                DOKU_INC."lib/scripts/fileuploader.js",
                DOKU_INC."lib/scripts/fileuploaderextended.js",
                DOKU_INC.'lib/scripts/helpers.js',
                DOKU_INC.'lib/scripts/delay.js',
                DOKU_INC.'lib/scripts/cookie.js',
                DOKU_INC.'lib/scripts/script.js',
                DOKU_INC.'lib/scripts/qsearch.js',
                DOKU_INC.'lib/scripts/search.js',
                DOKU_INC.'lib/scripts/tree.js',
                DOKU_INC.'lib/scripts/index.js',
                DOKU_INC.'lib/scripts/textselection.js',
                DOKU_INC.'lib/scripts/toolbar.js',
                DOKU_INC.'lib/scripts/edit.js',
                DOKU_INC.'lib/scripts/editor.js',
                DOKU_INC.'lib/scripts/locktimer.js',
                DOKU_INC.'lib/scripts/linkwiz.js',
                DOKU_INC.'lib/scripts/media.js',
                DOKU_INC.'lib/scripts/compatibility.js',
# disabled for FS#1958                DOKU_INC.'lib/scripts/hotkeys.js',
                DOKU_INC.'lib/scripts/behaviour.js',
                DOKU_INC.'lib/scripts/page.js',
                tpl_incdir($tpl).'script.js',
            );

    // add possible plugin scripts and userscript
    $files   = array_merge($files,js_pluginscripts());
    if(!empty($config_cascade['userscript']['default'])) {
        foreach($config_cascade['userscript']['default'] as $userscript) {
            $files[] = $userscript;
        }
    }

    // Let plugins decide to either put more scripts here or to remove some
    trigger_event('JS_SCRIPT_LIST', $files);

    // The generated script depends on some dynamic options
    $cache = new cache('scripts'.$_SERVER['HTTP_HOST'].$_SERVER['SERVER_PORT'].md5(serialize($files)),'.js');
    $cache->_event = 'JS_CACHE_USE';

    $cache_files = array_merge($files, getConfigFiles('main'));
    $cache_files[] = __FILE__;

    // check cache age & handle conditional request
    // This may exit if a cache can be used
    $cache_ok = $cache->useCache(array('files' => $cache_files));
    http_cached($cache->cache, $cache_ok);

    // start output buffering and build the script
    ob_start();

    $json = new JSON();
    // add some global variables
    print "var DOKU_BASE   = '".DOKU_BASE."';";
    print "var DOKU_TPL    = '".tpl_basedir($tpl)."';";
    print "var DOKU_COOKIE_PARAM = " . $json->encode(
            array(
                 'path' => empty($conf['cookiedir']) ? DOKU_REL : $conf['cookiedir'],
                 'secure' => $conf['securecookie'] && is_ssl()
            )).";";
    // FIXME: Move those to JSINFO
    print "Object.defineProperty(window, 'DOKU_UHN', { get: function() { console.warn('Using DOKU_UHN is deprecated. Please use JSINFO.useHeadingNavigation instead'); return JSINFO.useHeadingNavigation; } });";
    print "Object.defineProperty(window, 'DOKU_UHC', { get: function() { console.warn('Using DOKU_UHC is deprecated. Please use JSINFO.useHeadingContent instead'); return JSINFO.useHeadingContent; } });";

    // load JS specific translations
    $lang['js']['plugins'] = js_pluginstrings();
    $templatestrings = js_templatestrings($tpl);
    if(!empty($templatestrings)) {
        $lang['js']['template'] = $templatestrings;
    }
    echo 'LANG = '.$json->encode($lang['js']).";\n";

    // load toolbar
    toolbar_JSdefines('toolbar');

    // load files
    foreach($files as $file){
        if(!file_exists($file)) continue;
        $ismin = (substr($file,-7) == '.min.js');
        $debugjs = ($conf['allowdebug'] && strpos($file, DOKU_INC.'lib/scripts/') !== 0);

        echo "\n\n/* XXXXXXXXXX begin of ".str_replace(DOKU_INC, '', $file) ." XXXXXXXXXX */\n\n";
        if($ismin) echo "\n/* BEGIN NOCOMPRESS */\n";
        if ($debugjs) echo "\ntry {\n";
        js_load($file);
        if ($debugjs) echo "\n} catch (e) {\n   logError(e, '".str_replace(DOKU_INC, '', $file)."');\n}\n";
        if($ismin) echo "\n/* END NOCOMPRESS */\n";
        echo "\n\n/* XXXXXXXXXX end of " . str_replace(DOKU_INC, '', $file) . " XXXXXXXXXX */\n\n";
    }

    // init stuff
    if($conf['locktime'] != 0){
        js_runonstart("dw_locktimer.init(".($conf['locktime'] - 60).",".$conf['usedraft'].")");
    }
    // init hotkeys - must have been done after init of toolbar
# disabled for FS#1958    js_runonstart('initializeHotkeys()');

    // end output buffering and get contents
    $js = ob_get_contents();
    ob_end_clean();

    // strip any source maps
    stripsourcemaps($js);

    // compress whitespace and comments
    if($conf['compress']){
        $js = js_compress($js);
    }

    $js .= "\n"; // https://bugzilla.mozilla.org/show_bug.cgi?id=316033

    http_cached_finish($cache->cache, $js);
}

/**
 * Load the given file, handle include calls and print it
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 *
 * @param string $file filename path to file
 */
function js_load($file){
```
