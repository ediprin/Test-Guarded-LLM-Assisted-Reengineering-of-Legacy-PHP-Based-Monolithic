You are assisting with bounded reengineering of a legacy PHP-based monolithic web application.

Task:
Improve maintainability of the selected PHP code region while preserving observable behavior.

Candidate:
- Candidate ID: dokuwiki-C0213
- Project: dokuwiki
- File: inc/template.php
- Lines: 1321-1372
- Candidate type: long_method_or_region

Rules:
- Return a unified diff only.
- Do not change public routes, request parameters, session keys, database table names, DOM selectors, or form field names.
- Do not migrate framework, architecture, database schema, or application structure.
- Keep the change local and bounded.

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
