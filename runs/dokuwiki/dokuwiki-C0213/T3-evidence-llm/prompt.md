You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0213
- Project: dokuwiki
- File: inc/template.php
- Lines: 1321-1372
- Candidate type: long_method_or_region
- Oracle IDs: dokuwiki_home_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0213",
  "subject_id": "dokuwiki",
  "file": "inc/template.php",
  "lines": [
    1321,
    1372
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
      "value": 11
    }
  ],
  "dependencies": {
    "request_parameters": [],
    "session_keys": [],
    "database_tables": []
  },
  "web_contracts": {
    "dom_selectors": [
      "#media__content"
    ],
    "forms": []
  },
  "protected_constraints": {
    "must_preserve_request_parameters": [],
    "must_preserve_session_keys": [],
    "must_preserve_database_tables": [],
    "must_preserve_dom_selectors": [
      "#media__content"
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
function tpl_mediaContent($fromajax = false, $sort='natural') {
    global $IMG;
    global $AUTH;
    global $INUSE;
    global $NS;
    global $JUMPTO;
    /** @var Input $INPUT */
    global $INPUT;

    $do = $INPUT->extract('do')->str('do');
    if(in_array($do, array('save', 'cancel'))) $do = '';

    if(!$do) {
        if($INPUT->bool('edit')) {
            $do = 'metaform';
        } elseif(is_array($INUSE)) {
            $do = 'filesinuse';
        } else {
            $do = 'filelist';
        }
    }

    // output the content pane, wrapped in an event.
    if(!$fromajax) ptln('<div id="media__content">');
    $data = array('do' => $do);
    $evt  = new Doku_Event('MEDIAMANAGER_CONTENT_OUTPUT', $data);
    if($evt->advise_before()) {
        $do = $data['do'];
        if($do == 'filesinuse') {
            media_filesinuse($INUSE, $IMG);
        } elseif($do == 'filelist') {
            media_filelist($NS, $AUTH, $JUMPTO,false,$sort);
        } elseif($do == 'searchlist') {
            media_searchlist($INPUT->str('q'), $NS, $AUTH);
        } else {
            msg('Unknown action '.hsc($do), -1);
        }
    }
    $evt->advise_after();
    unset($evt);
    if(!$fromajax) ptln('</div>');

}

/**
 * Prints the central column in full-screen media manager
 * Depending on the opened tab this may be a list of
 * files in a namespace, upload form or search form
 *
 * @author Kate Arzamastseva <pshns@ukr.net>
 */
function tpl_mediaFileList() {
```
