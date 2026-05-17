You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0223
- Project: dokuwiki
- File: lib/exe/css.php
- Lines: 29-183
- Candidate type: long_method_or_region
- Oracle IDs: dokuwiki_css_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0223",
  "subject_id": "dokuwiki",
  "file": "lib/exe/css.php",
  "lines": [
    29,
    183
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
      "value": 25
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
function css_out(){
    global $conf;
    global $lang;
    global $config_cascade;
    global $INPUT;

    if ($INPUT->str('s') == 'feed') {
        $mediatypes = array('feed');
        $type = 'feed';
    } else {
        $mediatypes = array('screen', 'all', 'print', 'speech');
        $type = '';
    }

    // decide from where to get the template
    $tpl = trim(preg_replace('/[^\w-]+/','',$INPUT->str('t')));
    if(!$tpl) $tpl = $conf['template'];

    // load style.ini
    $styleUtil = new \dokuwiki\StyleUtils();
    $styleini = $styleUtil->cssStyleini($tpl, $INPUT->bool('preview'));

    // cache influencers
    $tplinc = tpl_incdir($tpl);
    $cache_files = getConfigFiles('main');
    $cache_files[] = $tplinc.'style.ini';
    $cache_files[] = DOKU_CONF."tpl/$tpl/style.ini";
    $cache_files[] = __FILE__;
    if($INPUT->bool('preview')) $cache_files[] = $conf['cachedir'].'/preview.ini';

    // Array of needed files and their web locations, the latter ones
    // are needed to fix relative paths in the stylesheets
    $media_files = array();
    foreach($mediatypes as $mediatype) {
        $files = array();

        // load core styles
        $files[DOKU_INC.'lib/styles/'.$mediatype.'.css'] = DOKU_BASE.'lib/styles/';

        // load jQuery-UI theme
        if ($mediatype == 'screen') {
            $files[DOKU_INC.'lib/scripts/jquery/jquery-ui-theme/smoothness.css'] = DOKU_BASE.'lib/scripts/jquery/jquery-ui-theme/';
        }
        // load plugin styles
        $files = array_merge($files, css_pluginstyles($mediatype));
        // load template styles
        if (isset($styleini['stylesheets'][$mediatype])) {
            $files = array_merge($files, $styleini['stylesheets'][$mediatype]);
        }
        // load user styles
        if(!empty($config_cascade['userstyle'][$mediatype])) {
            foreach($config_cascade['userstyle'][$mediatype] as $userstyle) {
                $files[$userstyle] = DOKU_BASE;
            }
        }

        // Let plugins decide to either put more styles here or to remove some
        $media_files[$mediatype] = css_filewrapper($mediatype, $files);
        $CSSEvt = new Doku_Event('CSS_STYLES_INCLUDED', $media_files[$mediatype]);

        // Make it preventable.
        if ( $CSSEvt->advise_before() ) {
            $cache_files = array_merge($cache_files, array_keys($media_files[$mediatype]['files']));
        } else {
            // unset if prevented. Nothing will be printed for this mediatype.
            unset($media_files[$mediatype]);
        }

        // finish event.
        $CSSEvt->advise_after();
    }

    // The generated script depends on some dynamic options
    $cache = new cache('styles'.$_SERVER['HTTP_HOST'].$_SERVER['SERVER_PORT'].$INPUT->bool('preview').DOKU_BASE.$tpl.$type,'.css');
    $cache->_event = 'CSS_CACHE_USE';

    // check cache age & handle conditional request
    // This may exit if a cache can be used
    $cache_ok = $cache->useCache(array('files' => $cache_files));
    http_cached($cache->cache, $cache_ok);

    // start output buffering
    ob_start();

    // Fire CSS_STYLES_INCLUDED for one last time to let the
    // plugins decide whether to include the DW default styles.
    // This can be done by preventing the Default.
    $media_files['DW_DEFAULT'] = css_filewrapper('DW_DEFAULT');
    trigger_event('CSS_STYLES_INCLUDED', $media_files['DW_DEFAULT'], 'css_defaultstyles');

    // build the stylesheet
    foreach ($mediatypes as $mediatype) {

        // Check if there is a wrapper set for this type.
        if ( !isset($media_files[$mediatype]) ) {
            continue;
        }

        $cssData = $media_files[$mediatype];

        // Print the styles.
        print NL;
        if ( $cssData['encapsulate'] === true ) print $cssData['encapsulationPrefix'] . ' {';
        print '/* START '.$cssData['mediatype'].' styles */'.NL;

        // load files
        foreach($cssData['files'] as $file => $location){
            $display = str_replace(fullpath(DOKU_INC), '', fullpath($file));
            print "\n/* XXXXXXXXX $display XXXXXXXXX */\n";
            print css_loadfile($file, $location);
        }

        print NL;
        if ( $cssData['encapsulate'] === true ) print '} /* /@media ';
        else print '/*';
        print ' END '.$cssData['mediatype'].' styles */'.NL;
    }

    // end output buffering and get contents
    $css = ob_get_contents();
    ob_end_clean();

    // strip any source maps
    stripsourcemaps($css);

    // apply style replacements
    $css = css_applystyle($css, $styleini['replacements']);

    // parse less
    $css = css_parseless($css);

    // compress whitespace and comments
    if($conf['compress']){
        $css = css_compress($css);
    }

    // embed small images right into the stylesheet
    if($conf['cssdatauri']){
        $base = preg_quote(DOKU_BASE,'#');
        $css = preg_replace_callback('#(url\([ \'"]*)('.$base.')(.*?(?:\.(png|gif)))#i','css_datauri',$css);
    }

    http_cached_finish($cache->cache, $css);
}

/**
 * Uses phpless to parse LESS in our CSS
 *
 * most of this function is error handling to show a nice useful error when
 * LESS compilation fails
 *
 * @param string $css
 * @return string
 */
function css_parseless($css) {
```
