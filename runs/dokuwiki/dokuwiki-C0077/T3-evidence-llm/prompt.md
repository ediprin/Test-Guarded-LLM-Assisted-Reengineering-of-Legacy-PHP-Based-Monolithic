You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0077
- Project: dokuwiki
- File: inc/html.php
- Lines: 661-866
- Candidate type: long_method_or_region
- Oracle IDs: dokuwiki_home_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0077",
  "subject_id": "dokuwiki",
  "file": "inc/html.php",
  "lines": [
    661,
    866
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
      "value": 24
    }
  ],
  "dependencies": {
    "request_parameters": [],
    "session_keys": [],
    "database_tables": []
  },
  "web_contracts": {
    "dom_selectors": [
      ".changeType",
      ".icon",
      ".level1",
      ".minor"
    ],
    "forms": []
  },
  "protected_constraints": {
    "must_preserve_request_parameters": [],
    "must_preserve_session_keys": [],
    "must_preserve_database_tables": [],
    "must_preserve_dom_selectors": [
      ".changeType",
      ".icon",
      ".level1",
      ".minor"
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
function html_recent($first = 0, $show_changes = 'both') {
    global $conf;
    global $lang;
    global $ID;
    /* we need to get one additionally log entry to be able to
     * decide if this is the last page or is there another one.
     * This is the cheapest solution to get this information.
     */
    $flags = 0;
    if($show_changes == 'mediafiles' && $conf['mediarevisions']) {
        $flags = RECENTS_MEDIA_CHANGES;
    } elseif($show_changes == 'pages') {
        $flags = 0;
    } elseif($conf['mediarevisions']) {
        $show_changes = 'both';
        $flags = RECENTS_MEDIA_PAGES_MIXED;
    }

    $recents = getRecents($first, $conf['recent'] + 1, getNS($ID), $flags);
    if(count($recents) == 0 && $first != 0) {
        $first = 0;
        $recents = getRecents($first, $conf['recent'] + 1, getNS($ID), $flags);
    }
    $hasNext = false;
    if(count($recents) > $conf['recent']) {
        $hasNext = true;
        array_pop($recents); // remove extra log entry
    }

    print p_locale_xhtml('recent');

    if(getNS($ID) != '') {
        print '<div class="level1"><p>' . sprintf($lang['recent_global'], getNS($ID), wl('', 'do=recent')) . '</p></div>';
    }

    $form = new Doku_Form(array('id' => 'dw__recent', 'method' => 'GET', 'class' => 'changes'));
    $form->addHidden('sectok', null);
    $form->addHidden('do', 'recent');
    $form->addHidden('id', $ID);

    if($conf['mediarevisions']) {
        $form->addElement('<div class="changeType">');
        $form->addElement(form_makeListboxField(
                    'show_changes',
                    array(
                        'pages'      => $lang['pages_changes'],
                        'mediafiles' => $lang['media_changes'],
                        'both'       => $lang['both_changes']
                    ),
                    $show_changes,
                    $lang['changes_type'],
                    '', '',
                    array('class' => 'quickselect')));

        $form->addElement(form_makeButton('submit', 'recent', $lang['btn_apply']));
        $form->addElement('</div>');
    }

    $form->addElement(form_makeOpenTag('ul'));

    foreach($recents as $recent) {
        $date = dformat($recent['date']);

        $class = '';
        if($recent['type'] === DOKU_CHANGE_TYPE_MINOR_EDIT) {
            $class = 'minor';
        }
        $form->addElement(form_makeOpenTag('li', array('class' => $class)));
        $form->addElement(form_makeOpenTag('div', array('class' => 'li')));

        if(!empty($recent['media'])) {
            $form->addElement(media_printicon($recent['id']));
        } else {
            $icon = DOKU_BASE . 'lib/images/fileicons/file.png';
            $form->addElement('<img src="' . $icon . '" alt="' . $recent['id'] . '" class="icon" />');
        }

        $form->addElement(form_makeOpenTag('span', array('class' => 'date')));
        $form->addElement($date);
        $form->addElement(form_makeCloseTag('span'));

        $diff = false;
        $href = '';

        if(!empty($recent['media'])) {
            $changelog = new MediaChangeLog($recent['id']);
            $revs = $changelog->getRevisions(0, 1);
            $diff = (count($revs) && file_exists(mediaFN($recent['id'])));
            if($diff) {
                $href = media_managerURL(array(
                                            'tab_details' => 'history',
                                            'mediado' => 'diff',
                                            'image' => $recent['id'],
                                            'ns' => getNS($recent['id'])
                                        ), '&');
            }
        } else {
            $href = wl($recent['id'], "do=diff", false, '&');
        }

        if(!empty($recent['media']) && !$diff) {
            $form->addElement('<img src="' . DOKU_BASE . 'lib/images/blank.gif" width="15" height="11" alt="" />');
        } else {
            $form->addElement(form_makeOpenTag('a', array('class' => 'diff_link', 'href' => $href)));
            $form->addElement(form_makeTag('img', array(
                            'src'    => DOKU_BASE . 'lib/images/diff.png',
                            'width'  => 15,
                            'height' => 11,
                            'title'  => $lang['diff'],
                            'alt'    => $lang['diff']
                        )));
            $form->addElement(form_makeCloseTag('a'));
        }

        if(!empty($recent['media'])) {
            $href = media_managerURL(array('tab_details' => 'history', 'image' => $recent['id'], 'ns' => getNS($recent['id'])), '&');
        } else {
            $href = wl($recent['id'], "do=revisions", false, '&');
        }
        $form->addElement(form_makeOpenTag('a', array(
                        'class' => 'revisions_link',
                        'href'  => $href)));
        $form->addElement(form_makeTag('img', array(
                        'src'    => DOKU_BASE . 'lib/images/history.png',
                        'width'  => 12,
                        'height' => 14,
                        'title'  => $lang['btn_revs'],
                        'alt'    => $lang['btn_revs']
                    )));
        $form->addElement(form_makeCloseTag('a'));

        if(!empty($recent['media'])) {
            $href = media_managerURL(array('tab_details' => 'view', 'image' => $recent['id'], 'ns' => getNS($recent['id'])), '&');
            $class = file_exists(mediaFN($recent['id'])) ? 'wikilink1' : 'wikilink2';
            $form->addElement(form_makeOpenTag('a', array(
                        'class' => $class,
                        'href'  => $href)));
            $form->addElement($recent['id']);
            $form->addElement(form_makeCloseTag('a'));
        } else {
            $form->addElement(html_wikilink(':' . $recent['id'], useHeading('navigation') ? null : $recent['id']));
        }
        $form->addElement(form_makeOpenTag('span', array('class' => 'sum')));
        $form->addElement(' – ' . hsc($recent['sum']));
        $form->addElement(form_makeCloseTag('span'));

        $form->addElement(form_makeOpenTag('span', array('class' => 'user')));
        if($recent['user']) {
            $form->addElement('<bdi>' . editorinfo($recent['user']) . '</bdi>');
            if(auth_ismanager()) {
                $form->addElement(' <bdo dir="ltr">(' . $recent['ip'] . ')</bdo>');
            }
        } else {
            $form->addElement('<bdo dir="ltr">' . $recent['ip'] . '</bdo>');
        }
        $form->addElement(form_makeCloseTag('span'));

        html_sizechange($recent['sizechange'], $form);

        $form->addElement(form_makeCloseTag('div'));
        $form->addElement(form_makeCloseTag('li'));
    }
    $form->addElement(form_makeCloseTag('ul'));

    $form->addElement(form_makeOpenTag('div', array('class' => 'pagenav')));
    $last = $first + $conf['recent'];
    if($first > 0) {
        $first -= $conf['recent'];
        if($first < 0) $first = 0;
        $form->addElement(form_makeOpenTag('div', array('class' => 'pagenav-prev')));
        $form->addElement(form_makeOpenTag('button', array(
                        'type'      => 'submit',
                        'name'      => 'first[' . $first . ']',
                        'accesskey' => 'n',
                        'title'     => $lang['btn_newer'] . ' [N]',
                        'class'     => 'button show'
                    )));
        $form->addElement($lang['btn_newer']);
        $form->addElement(form_makeCloseTag('button'));
        $form->addElement(form_makeCloseTag('div'));
    }
    if($hasNext) {
        $form->addElement(form_makeOpenTag('div', array('class' => 'pagenav-next')));
        $form->addElement(form_makeOpenTag('button', array(
                        'type'      => 'submit',
                        'name'      => 'first[' . $last . ']',
                        'accesskey' => 'p',
                        'title'     => $lang['btn_older'] . ' [P]',
                        'class'     => 'button show'
                    )));
        $form->addElement($lang['btn_older']);
        $form->addElement(form_makeCloseTag('button'));
        $form->addElement(form_makeCloseTag('div'));
    }
    $form->addElement(form_makeCloseTag('div'));
    html_form('recent', $form);
}

/**
 * Display page index
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 *
 * @param string $ns
 */
function html_index($ns){
```
