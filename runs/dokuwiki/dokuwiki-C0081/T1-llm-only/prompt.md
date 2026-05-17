You are assisting with bounded reengineering of a legacy PHP-based monolithic web application.

Task:
Improve maintainability of the selected PHP code region while preserving observable behavior.

Candidate:
- Candidate ID: dokuwiki-C0081
- Project: dokuwiki
- File: inc/html.php
- Lines: 1382-1517
- Candidate type: long_method_or_region

Rules:
- Return a unified diff only.
- Do not change public routes, request parameters, session keys, database table names, DOM selectors, or form field names.
- Do not migrate framework, architecture, database schema, or application structure.
- Keep the change local and bounded.

Code region:
```php
function html_diff_navigation($pagelog, $type, $l_rev, $r_rev) {
    global $INFO, $ID;

    // last timestamp is not in changelog, retrieve timestamp from metadata
    // note: when page is removed, the metadata timestamp is zero
    if(!$r_rev) {
        if(isset($INFO['meta']['last_change']['date'])) {
            $r_rev = $INFO['meta']['last_change']['date'];
        } else {
            $r_rev = 0;
        }
    }

    //retrieve revisions with additional info
    list($l_revs, $r_revs) = $pagelog->getRevisionsAround($l_rev, $r_rev);
    $l_revisions = array();
    if(!$l_rev) {
        $l_revisions[0] = array(0, "", false); //no left revision given, add dummy
    }
    foreach($l_revs as $rev) {
        $info = $pagelog->getRevisionInfo($rev);
        $l_revisions[$rev] = array(
            $rev,
            dformat($info['date']) . ' ' . editorinfo($info['user'], true) . ' ' . $info['sum'],
            $r_rev ? $rev >= $r_rev : false //disable?
        );
    }
    $r_revisions = array();
    if(!$r_rev) {
        $r_revisions[0] = array(0, "", false); //no right revision given, add dummy
    }
    foreach($r_revs as $rev) {
        $info = $pagelog->getRevisionInfo($rev);
        $r_revisions[$rev] = array(
            $rev,
            dformat($info['date']) . ' ' . editorinfo($info['user'], true) . ' ' . $info['sum'],
            $rev <= $l_rev //disable?
        );
    }

    //determine previous/next revisions
    $l_index = array_search($l_rev, $l_revs);
    $l_prev = $l_revs[$l_index + 1];
    $l_next = $l_revs[$l_index - 1];
    if($r_rev) {
        $r_index = array_search($r_rev, $r_revs);
        $r_prev = $r_revs[$r_index + 1];
        $r_next = $r_revs[$r_index - 1];
    } else {
        //removed page
        if($l_next) {
            $r_prev = $r_revs[0];
        } else {
            $r_prev = null;
        }
        $r_next = null;
    }

    /*
     * Left side:
     */
    $l_nav = '';
    //move back
    if($l_prev) {
        $l_nav .= html_diff_navigationlink($type, 'diffbothprevrev', $l_prev, $r_prev);
        $l_nav .= html_diff_navigationlink($type, 'diffprevrev', $l_prev, $r_rev);
    }
    //dropdown
    $form = new Doku_Form(array('action' => wl()));
    $form->addHidden('id', $ID);
    $form->addHidden('difftype', $type);
    $form->addHidden('rev2[1]', $r_rev);
    $form->addHidden('do', 'diff');
    $form->addElement(
         form_makeListboxField(
             'rev2[0]',
             $l_revisions,
             $l_rev,
             '', '', '',
             array('class' => 'quickselect')
         )
    );
    $form->addElement(form_makeButton('submit', 'diff', 'Go'));
    $l_nav .= $form->getForm();
    //move forward
    if($l_next && ($l_next < $r_rev || !$r_rev)) {
        $l_nav .= html_diff_navigationlink($type, 'diffnextrev', $l_next, $r_rev);
    }

    /*
     * Right side:
     */
    $r_nav = '';
    //move back
    if($l_rev < $r_prev) {
        $r_nav .= html_diff_navigationlink($type, 'diffprevrev', $l_rev, $r_prev);
    }
    //dropdown
    $form = new Doku_Form(array('action' => wl()));
    $form->addHidden('id', $ID);
    $form->addHidden('rev2[0]', $l_rev);
    $form->addHidden('difftype', $type);
    $form->addHidden('do', 'diff');
    $form->addElement(
         form_makeListboxField(
             'rev2[1]',
             $r_revisions,
             $r_rev,
             '', '', '',
             array('class' => 'quickselect')
         )
    );
    $form->addElement(form_makeButton('submit', 'diff', 'Go'));
    $r_nav .= $form->getForm();
    //move forward
    if($r_next) {
        if($pagelog->isCurrentRevision($r_next)) {
            $r_nav .= html_diff_navigationlink($type, 'difflastrev', $l_rev); //last revision is diff with current page
        } else {
            $r_nav .= html_diff_navigationlink($type, 'diffnextrev', $l_rev, $r_next);
        }
        $r_nav .= html_diff_navigationlink($type, 'diffbothnextrev', $l_next, $r_next);
    }
    return array($l_nav, $r_nav);
}

/**
 * Create html link to a diff defined by two revisions
 *
 * @param string $difftype display type
 * @param string $linktype
 * @param int $lrev oldest revision
 * @param int $rrev newest revision or null for diff with current revision
 * @return string html of link to a diff
 */
function html_diff_navigationlink($difftype, $linktype, $lrev, $rrev = null) {
```
