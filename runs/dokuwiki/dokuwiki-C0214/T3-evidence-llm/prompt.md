You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0214
- Project: dokuwiki
- File: inc/template.php
- Lines: 1420-1484
- Candidate type: long_method_or_region
- Oracle IDs: dokuwiki_home_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0214",
  "subject_id": "dokuwiki",
  "file": "inc/template.php",
  "lines": [
    1420,
    1484
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
    "request_parameters": [],
    "session_keys": [],
    "database_tables": []
  },
  "web_contracts": {
    "dom_selectors": [
      ".mediafile",
      ".mf_",
      ".panelContent",
      ".panelHeader",
      ".select"
    ],
    "forms": []
  },
  "protected_constraints": {
    "must_preserve_request_parameters": [],
    "must_preserve_session_keys": [],
    "must_preserve_database_tables": [],
    "must_preserve_dom_selectors": [
      ".mediafile",
      ".mf_",
      ".panelContent",
      ".panelHeader",
      ".select"
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
function tpl_mediaFileDetails($image, $rev) {
    global $conf, $DEL, $lang;
    /** @var Input $INPUT */
    global $INPUT;

    $removed = (!file_exists(mediaFN($image)) && file_exists(mediaMetaFN($image, '.changes')) && $conf['mediarevisions']);
    if(!$image || (!file_exists(mediaFN($image)) && !$removed) || $DEL) return;
    if($rev && !file_exists(mediaFN($image, $rev))) $rev = false;
    $ns = getNS($image);
    $do = $INPUT->str('mediado');

    $opened_tab = $INPUT->str('tab_details');

    $tab_array = array('view');
    list(, $mime) = mimetype($image);
    if($mime == 'image/jpeg') {
        $tab_array[] = 'edit';
    }
    if($conf['mediarevisions']) {
        $tab_array[] = 'history';
    }

    if(!$opened_tab || !in_array($opened_tab, $tab_array)) $opened_tab = 'view';
    if($INPUT->bool('edit')) $opened_tab = 'edit';
    if($do == 'restore') $opened_tab = 'view';

    media_tabs_details($image, $opened_tab);

    echo '<div class="panelHeader"><h3>';
    list($ext) = mimetype($image, false);
    $class    = preg_replace('/[^_\-a-z0-9]+/i', '_', $ext);
    $class    = 'select mediafile mf_'.$class;
    $attributes = $rev ? ['rev' => $rev] : [];
    $tabTitle = '<strong><a href="'.ml($image, $attributes).'" class="'.$class.'" title="'.$lang['mediaview'].'">'.$image.'</a>'.'</strong>';
    if($opened_tab === 'view' && $rev) {
        printf($lang['media_viewold'], $tabTitle, dformat($rev));
    } else {
        printf($lang['media_'.$opened_tab], $tabTitle);
    }

    echo '</h3></div>'.NL;

    echo '<div class="panelContent">'.NL;

    if($opened_tab == 'view') {
        media_tab_view($image, $ns, null, $rev);

    } elseif($opened_tab == 'edit' && !$removed) {
        media_tab_edit($image, $ns);

    } elseif($opened_tab == 'history' && $conf['mediarevisions']) {
        media_tab_history($image, $ns);
    }

    echo '</div>'.NL;
}

/**
 * prints the namespace tree in the mediamanager popup
 *
 * Only allowed in mediamanager.php
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 */
function tpl_mediaTree() {
```
