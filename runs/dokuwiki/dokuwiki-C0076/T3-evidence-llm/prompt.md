You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0076
- Project: dokuwiki
- File: inc/html.php
- Lines: 399-661
- Candidate type: long_method_or_region
- Oracle IDs: dokuwiki_home_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0076",
  "subject_id": "dokuwiki",
  "file": "inc/html.php",
  "lines": [
    399,
    661
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
      "value": 41
    }
  ],
  "dependencies": {
    "request_parameters": [],
    "session_keys": [],
    "database_tables": []
  },
  "web_contracts": {
    "dom_selectors": [
      ".minor",
      ".pagenav",
      ".pagenav-next",
      ".pagenav-prev"
    ],
    "forms": []
  },
  "protected_constraints": {
    "must_preserve_request_parameters": [],
    "must_preserve_session_keys": [],
    "must_preserve_database_tables": [],
    "must_preserve_dom_selectors": [
      ".minor",
      ".pagenav",
      ".pagenav-next",
      ".pagenav-prev"
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
function html_revisions($first=0, $media_id = false){
    global $ID;
    global $INFO;
    global $conf;
    global $lang;
    $id = $ID;
    if ($media_id) {
        $id = $media_id;
        $changelog = new MediaChangeLog($id);
    } else {
        $changelog = new PageChangeLog($id);
    }

    /* we need to get one additional log entry to be able to
     * decide if this is the last page or is there another one.
     * see html_recent()
     */

    $revisions = $changelog->getRevisions($first, $conf['recent']+1);

    if(count($revisions)==0 && $first!=0){
        $first=0;
        $revisions = $changelog->getRevisions($first, $conf['recent']+1);
    }
    $hasNext = false;
    if (count($revisions)>$conf['recent']) {
        $hasNext = true;
        array_pop($revisions); // remove extra log entry
    }

    if (!$media_id) print p_locale_xhtml('revisions');

    $params = array('id' => 'page__revisions', 'class' => 'changes');
    if($media_id) {
        $params['action'] = media_managerURL(array('image' => $media_id), '&');
    }

    if(!$media_id) {
        $exists = $INFO['exists'];
        $display_name = useHeading('navigation') ? hsc(p_get_first_heading($id)) : $id;
        if(!$display_name) {
            $display_name = $id;
        }
    } else {
        $exists = file_exists(mediaFN($id));
        $display_name = $id;
    }

    $form = new Doku_Form($params);
    $form->addElement(form_makeOpenTag('ul'));

    if($exists && $first == 0) {
        $minor = false;
        if($media_id) {
            $date = dformat(@filemtime(mediaFN($id)));
            $href = media_managerURL(array('image' => $id, 'tab_details' => 'view'), '&');

            $changelog->setChunkSize(1024);
            $revinfo = $changelog->getRevisionInfo(@filemtime(fullpath(mediaFN($id))));

            $summary = $revinfo['sum'];
            if($revinfo['user']) {
                $editor = $revinfo['user'];
            } else {
                $editor = $revinfo['ip'];
            }
            $sizechange = $revinfo['sizechange'];
        } else {
            $date = dformat($INFO['lastmod']);
            if(isset($INFO['meta']) && isset($INFO['meta']['last_change'])) {
                if($INFO['meta']['last_change']['type'] === DOKU_CHANGE_TYPE_MINOR_EDIT) {
                    $minor = true;
                }
                if(isset($INFO['meta']['last_change']['sizechange'])) {
                    $sizechange = $INFO['meta']['last_change']['sizechange'];
                } else {
                    $sizechange = null;
                }
            }
            $pagelog = new PageChangeLog($ID);
            $latestrev = $pagelog->getRevisions(-1, 1);
            $latestrev = array_pop($latestrev);
            $href = wl($id,"rev=$latestrev",false,'&');
            $summary = $INFO['sum'];
            $editor = $INFO['editor'];
        }

        $form->addElement(form_makeOpenTag('li', array('class' => ($minor ? 'minor' : ''))));
        $form->addElement(form_makeOpenTag('div', array('class' => 'li')));
        $form->addElement(form_makeTag('input', array(
                        'type' => 'checkbox',
                        'name' => 'rev2[]',
                        'value' => 'current')));

        $form->addElement(form_makeOpenTag('span', array('class' => 'date')));
        $form->addElement($date);
        $form->addElement(form_makeCloseTag('span'));

        $form->addElement('<img src="'.DOKU_BASE.'lib/images/blank.gif" width="15" height="11" alt="" />');

        $form->addElement(form_makeOpenTag('a', array(
                        'class' => 'wikilink1',
                        'href'  => $href)));
        $form->addElement($display_name);
        $form->addElement(form_makeCloseTag('a'));

        if ($media_id) $form->addElement(form_makeOpenTag('div'));

        if($summary) {
            $form->addElement(form_makeOpenTag('span', array('class' => 'sum')));
            if(!$media_id) $form->addElement(' – ');
            $form->addElement('<bdi>' . hsc($summary) . '</bdi>');
            $form->addElement(form_makeCloseTag('span'));
        }

        $form->addElement(form_makeOpenTag('span', array('class' => 'user')));
        $form->addElement((empty($editor))?('('.$lang['external_edit'].')'):'<bdi>'.editorinfo($editor).'</bdi>');
        $form->addElement(form_makeCloseTag('span'));

        html_sizechange($sizechange, $form);

        $form->addElement('('.$lang['current'].')');

        if ($media_id) $form->addElement(form_makeCloseTag('div'));

        $form->addElement(form_makeCloseTag('div'));
        $form->addElement(form_makeCloseTag('li'));
    }

    foreach($revisions as $rev) {
        $date = dformat($rev);
        $info = $changelog->getRevisionInfo($rev);
        if($media_id) {
            $exists = file_exists(mediaFN($id, $rev));
        } else {
            $exists = page_exists($id, $rev);
        }

        $class = '';
        if($info['type'] === DOKU_CHANGE_TYPE_MINOR_EDIT) {
            $class = 'minor';
        }
        $form->addElement(form_makeOpenTag('li', array('class' => $class)));
        $form->addElement(form_makeOpenTag('div', array('class' => 'li')));
        if($exists){
            $form->addElement(form_makeTag('input', array(
                            'type' => 'checkbox',
                            'name' => 'rev2[]',
                            'value' => $rev)));
        }else{
            $form->addElement('<img src="'.DOKU_BASE.'lib/images/blank.gif" width="15" height="11" alt="" />');
        }

        $form->addElement(form_makeOpenTag('span', array('class' => 'date')));
        $form->addElement($date);
        $form->addElement(form_makeCloseTag('span'));

        if($exists){
            if (!$media_id) {
                $href = wl($id,"rev=$rev,do=diff", false, '&');
            } else {
                $href = media_managerURL(array('image' => $id, 'rev' => $rev, 'mediado' => 'diff'), '&');
            }
            $form->addElement(form_makeOpenTag('a', array(
                            'class' => 'diff_link',
                            'href' => $href)));
            $form->addElement(form_makeTag('img', array(
                            'src'    => DOKU_BASE.'lib/images/diff.png',
                            'width'  => 15,
                            'height' => 11,
                            'title'  => $lang['diff'],
                            'alt'    => $lang['diff'])));
            $form->addElement(form_makeCloseTag('a'));

            if (!$media_id) {
                $href = wl($id,"rev=$rev",false,'&');
            } else {
                $href = media_managerURL(array('image' => $id, 'tab_details' => 'view', 'rev' => $rev), '&');
            }
            $form->addElement(form_makeOpenTag('a', array(
                            'class' => 'wikilink1',
                            'href' => $href)));
            $form->addElement($display_name);
            $form->addElement(form_makeCloseTag('a'));
        }else{
            $form->addElement('<img src="'.DOKU_BASE.'lib/images/blank.gif" width="15" height="11" alt="" />');
            $form->addElement($display_name);
        }

        if ($media_id) $form->addElement(form_makeOpenTag('div'));

        if ($info['sum']) {
            $form->addElement(form_makeOpenTag('span', array('class' => 'sum')));
            if(!$media_id) $form->addElement(' – ');
            $form->addElement('<bdi>'.hsc($info['sum']).'</bdi>');
            $form->addElement(form_makeCloseTag('span'));
        }

        $form->addElement(form_makeOpenTag('span', array('class' => 'user')));
        if($info['user']){
            $form->addElement('<bdi>'.editorinfo($info['user']).'</bdi>');
            if(auth_ismanager()){
                $form->addElement(' <bdo dir="ltr">('.$info['ip'].')</bdo>');
            }
        }else{
            $form->addElement('<bdo dir="ltr">'.$info['ip'].'</bdo>');
        }
        $form->addElement(form_makeCloseTag('span'));

        html_sizechange($info['sizechange'], $form);

        if ($media_id) $form->addElement(form_makeCloseTag('div'));

        $form->addElement(form_makeCloseTag('div'));
        $form->addElement(form_makeCloseTag('li'));
    }
    $form->addElement(form_makeCloseTag('ul'));
    if (!$media_id) {
        $form->addElement(form_makeButton('submit', 'diff', $lang['diff2']));
    } else {
        $form->addHidden('mediado', 'diff');
        $form->addElement(form_makeButton('submit', '', $lang['diff2']));
    }
    html_form('revisions', $form);

    print '<div class="pagenav">';
    $last = $first + $conf['recent'];
    if ($first > 0) {
        $first -= $conf['recent'];
        if ($first < 0) $first = 0;
        print '<div class="pagenav-prev">';
        if ($media_id) {
            print html_btn('newer',$media_id,"p",media_managerURL(array('first' => $first), '&amp;', false, true));
        } else {
            print html_btn('newer',$id,"p",array('do' => 'revisions', 'first' => $first));
        }
        print '</div>';
    }
    if ($hasNext) {
        print '<div class="pagenav-next">';
        if ($media_id) {
            print html_btn('older',$media_id,"n",media_managerURL(array('first' => $last), '&amp;', false, true));
        } else {
            print html_btn('older',$id,"n",array('do' => 'revisions', 'first' => $last));
        }
        print '</div>';
    }
    print '</div>';

}

/**
 * display recent changes
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 * @author Matthias Grimm <matthiasgrimm@users.sourceforge.net>
 * @author Ben Coburn <btcoburn@silicodon.net>
 * @author Kate Arzamastseva <pshns@ukr.net>
 *
 * @param int $first
 * @param string $show_changes
 */
function html_recent($first = 0, $show_changes = 'both') {
```
