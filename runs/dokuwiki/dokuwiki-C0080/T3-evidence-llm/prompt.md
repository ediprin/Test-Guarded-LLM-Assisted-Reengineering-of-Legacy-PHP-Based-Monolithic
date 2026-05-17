You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0080
- Project: dokuwiki
- File: inc/html.php
- Lines: 1167-1382
- Candidate type: mixed_php_html
- Oracle IDs: dokuwiki_home_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0080",
  "subject_id": "dokuwiki",
  "file": "inc/html.php",
  "lines": [
    1167,
    1382
  ],
  "candidate_type": "mixed_php_html",
  "issues": [
    {
      "type": "Mixed PHP/HTML",
      "evidence": "Detected by pre-treatment heuristic extractor; join with PHPMD/PHPStan logs for final static evidence."
    },
    {
      "type": "Complexity Proxy",
      "metric": "branch_keyword_count_plus_one",
      "value": 59
    }
  ],
  "dependencies": {
    "request_parameters": [],
    "session_keys": [],
    "database_tables": []
  },
  "web_contracts": {
    "dom_selectors": [
      ".diff",
      ".diff-lineheader",
      ".diff_<?php",
      ".diffnav",
      ".diffoptions",
      ".echo",
      ".group",
      ".table",
      ".wikilink1"
    ],
    "forms": []
  },
  "protected_constraints": {
    "must_preserve_request_parameters": [],
    "must_preserve_session_keys": [],
    "must_preserve_database_tables": [],
    "must_preserve_dom_selectors": [
      ".diff",
      ".diff-lineheader",
      ".diff_<?php",
      ".diffnav",
      ".diffoptions",
      ".echo",
      ".group",
      ".table",
      ".wikilink1"
    ],
    "must_preserve_forms": []
  },
  "allowed_transformations": [
    "Separate PHP Logic from Markup",
    "Extract View Helper"
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
function html_diff($text = '', $intro = true, $type = null) {
    global $ID;
    global $REV;
    global $lang;
    global $INPUT;
    global $INFO;
    $pagelog = new PageChangeLog($ID);

    /*
     * Determine diff type
     */
    if(!$type) {
        $type = $INPUT->str('difftype');
        if(empty($type)) {
            $type = get_doku_pref('difftype', $type);
            if(empty($type) && $INFO['ismobile']) {
                $type = 'inline';
            }
        }
    }
    if($type != 'inline') $type = 'sidebyside';

    /*
     * Determine requested revision(s)
     */
    // we're trying to be clever here, revisions to compare can be either
    // given as rev and rev2 parameters, with rev2 being optional. Or in an
    // array in rev2.
    $rev1 = $REV;

    $rev2 = $INPUT->ref('rev2');
    if(is_array($rev2)) {
        $rev1 = (int) $rev2[0];
        $rev2 = (int) $rev2[1];

        if(!$rev1) {
            $rev1 = $rev2;
            unset($rev2);
        }
    } else {
        $rev2 = $INPUT->int('rev2');
    }

    /*
     * Determine left and right revision, its texts and the header
     */
    $r_minor = '';
    $l_minor = '';

    if($text) { // compare text to the most current revision
        $l_rev = '';
        $l_text = rawWiki($ID, '');
        $l_head = '<a class="wikilink1" href="' . wl($ID) . '">' .
            $ID . ' ' . dformat((int) @filemtime(wikiFN($ID))) . '</a> ' .
            $lang['current'];

        $r_rev = '';
        $r_text = cleanText($text);
        $r_head = $lang['yours'];
    } else {
        if($rev1 && isset($rev2) && $rev2) { // two specific revisions wanted
            // make sure order is correct (older on the left)
            if($rev1 < $rev2) {
                $l_rev = $rev1;
                $r_rev = $rev2;
            } else {
                $l_rev = $rev2;
                $r_rev = $rev1;
            }
        } elseif($rev1) { // single revision given, compare to current
            $r_rev = '';
            $l_rev = $rev1;
        } else { // no revision was given, compare previous to current
            $r_rev = '';
            $revs = $pagelog->getRevisions(0, 1);
            $l_rev = $revs[0];
            $REV = $l_rev; // store revision back in $REV
        }

        // when both revisions are empty then the page was created just now
        if(!$l_rev && !$r_rev) {
            $l_text = '';
        } else {
            $l_text = rawWiki($ID, $l_rev);
        }
        $r_text = rawWiki($ID, $r_rev);

        list($l_head, $r_head, $l_minor, $r_minor) = html_diff_head($l_rev, $r_rev, null, false, $type == 'inline');
    }

    /*
     * Build navigation
     */
    $l_nav = '';
    $r_nav = '';
    if(!$text) {
        list($l_nav, $r_nav) = html_diff_navigation($pagelog, $type, $l_rev, $r_rev);
    }
    /*
     * Create diff object and the formatter
     */
    $diff = new Diff(explode("\n", $l_text), explode("\n", $r_text));

    if($type == 'inline') {
        $diffformatter = new InlineDiffFormatter();
    } else {
        $diffformatter = new TableDiffFormatter();
    }
    /*
     * Display intro
     */
    if($intro) print p_locale_xhtml('diff');

    /*
     * Display type and exact reference
     */
    if(!$text) {
        ptln('<div class="diffoptions group">');


        $form = new Doku_Form(array('action' => wl()));
        $form->addHidden('id', $ID);
        $form->addHidden('rev2[0]', $l_rev);
        $form->addHidden('rev2[1]', $r_rev);
        $form->addHidden('do', 'diff');
        $form->addElement(
             form_makeListboxField(
                 'difftype',
                 array(
                     'sidebyside' => $lang['diff_side'],
                     'inline' => $lang['diff_inline']
                 ),
                 $type,
                 $lang['diff_type'],
                 '', '',
                 array('class' => 'quickselect')
             )
        );
        $form->addElement(form_makeButton('submit', 'diff', 'Go'));
        $form->printForm();

        ptln('<p>');
        // link to exactly this view FS#2835
        echo html_diff_navigationlink($type, 'difflink', $l_rev, $r_rev ? $r_rev : $INFO['currentrev']);
        ptln('</p>');

        ptln('</div>'); // .diffoptions
    }

    /*
     * Display diff view table
     */
    ?>
    <div class="table">
    <table class="diff diff_<?php echo $type ?>">

        <?php
        //navigation and header
        if($type == 'inline') {
            if(!$text) { ?>
                <tr>
                    <td class="diff-lineheader">-</td>
                    <td class="diffnav"><?php echo $l_nav ?></td>
                </tr>
                <tr>
                    <th class="diff-lineheader">-</th>
                    <th <?php echo $l_minor ?>>
                        <?php echo $l_head ?>
                    </th>
                </tr>
            <?php } ?>
            <tr>
                <td class="diff-lineheader">+</td>
                <td class="diffnav"><?php echo $r_nav ?></td>
            </tr>
            <tr>
                <th class="diff-lineheader">+</th>
                <th <?php echo $r_minor ?>>
                    <?php echo $r_head ?>
                </th>
            </tr>
        <?php } else {
            if(!$text) { ?>
                <tr>
                    <td colspan="2" class="diffnav"><?php echo $l_nav ?></td>
                    <td colspan="2" class="diffnav"><?php echo $r_nav ?></td>
                </tr>
            <?php } ?>
            <tr>
                <th colspan="2" <?php echo $l_minor ?>>
                    <?php echo $l_head ?>
                </th>
                <th colspan="2" <?php echo $r_minor ?>>
                    <?php echo $r_head ?>
                </th>
            </tr>
        <?php }

        //diff view
        echo html_insert_softbreaks($diffformatter->format($diff)); ?>

    </table>
    </div>
<?php
}

/**
 * Create html for revision navigation
 *
 * @param PageChangeLog $pagelog changelog object of current page
 * @param string        $type    inline vs sidebyside
 * @param int           $l_rev   left revision timestamp
 * @param int           $r_rev   right revision timestamp
 * @return string[] html of left and right navigation elements
 */
function html_diff_navigation($pagelog, $type, $l_rev, $r_rev) {
```
