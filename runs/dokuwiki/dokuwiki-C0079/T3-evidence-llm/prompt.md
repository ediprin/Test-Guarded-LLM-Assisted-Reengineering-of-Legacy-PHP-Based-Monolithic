You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0079
- Project: dokuwiki
- File: inc/html.php
- Lines: 1081-1167
- Candidate type: long_method_or_region
- Oracle IDs: dokuwiki_home_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0079",
  "subject_id": "dokuwiki",
  "file": "inc/html.php",
  "lines": [
    1081,
    1167
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
      ".minor",
      ".sum",
      ".user",
      ".wikilink1"
    ],
    "forms": []
  },
  "protected_constraints": {
    "must_preserve_request_parameters": [],
    "must_preserve_session_keys": [],
    "must_preserve_database_tables": [],
    "must_preserve_dom_selectors": [
      ".minor",
      ".sum",
      ".user",
      ".wikilink1"
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
function html_diff_head($l_rev, $r_rev, $id = null, $media = false, $inline = false) {
    global $lang;
    if ($id === null) {
        global $ID;
        $id = $ID;
    }
    $head_separator = $inline ? ' ' : '<br />';
    $media_or_wikiFN = $media ? 'mediaFN' : 'wikiFN';
    $ml_or_wl = $media ? 'ml' : 'wl';
    $l_minor = $r_minor = '';

    if($media) {
        $changelog = new MediaChangeLog($id);
    } else {
        $changelog = new PageChangeLog($id);
    }
    if(!$l_rev){
        $l_head = '&mdash;';
    }else{
        $l_info   = $changelog->getRevisionInfo($l_rev);
        if($l_info['user']){
            $l_user = '<bdi>'.editorinfo($l_info['user']).'</bdi>';
            if(auth_ismanager()) $l_user .= ' <bdo dir="ltr">('.$l_info['ip'].')</bdo>';
        } else {
            $l_user = '<bdo dir="ltr">'.$l_info['ip'].'</bdo>';
        }
        $l_user  = '<span class="user">'.$l_user.'</span>';
        $l_sum   = ($l_info['sum']) ? '<span class="sum"><bdi>'.hsc($l_info['sum']).'</bdi></span>' : '';
        if ($l_info['type']===DOKU_CHANGE_TYPE_MINOR_EDIT) $l_minor = 'class="minor"';

        $l_head_title = ($media) ? dformat($l_rev) : $id.' ['.dformat($l_rev).']';
        $l_head = '<bdi><a class="wikilink1" href="'.$ml_or_wl($id,"rev=$l_rev").'">'.
        $l_head_title.'</a></bdi>'.
        $head_separator.$l_user.' '.$l_sum;
    }

    if($r_rev){
        $r_info   = $changelog->getRevisionInfo($r_rev);
        if($r_info['user']){
            $r_user = '<bdi>'.editorinfo($r_info['user']).'</bdi>';
            if(auth_ismanager()) $r_user .= ' <bdo dir="ltr">('.$r_info['ip'].')</bdo>';
        } else {
            $r_user = '<bdo dir="ltr">'.$r_info['ip'].'</bdo>';
        }
        $r_user = '<span class="user">'.$r_user.'</span>';
        $r_sum  = ($r_info['sum']) ? '<span class="sum"><bdi>'.hsc($r_info['sum']).'</bdi></span>' : '';
        if ($r_info['type']===DOKU_CHANGE_TYPE_MINOR_EDIT) $r_minor = 'class="minor"';

        $r_head_title = ($media) ? dformat($r_rev) : $id.' ['.dformat($r_rev).']';
        $r_head = '<bdi><a class="wikilink1" href="'.$ml_or_wl($id,"rev=$r_rev").'">'.
        $r_head_title.'</a></bdi>'.
        $head_separator.$r_user.' '.$r_sum;
    }elseif($_rev = @filemtime($media_or_wikiFN($id))){
        $_info   = $changelog->getRevisionInfo($_rev);
        if($_info['user']){
            $_user = '<bdi>'.editorinfo($_info['user']).'</bdi>';
            if(auth_ismanager()) $_user .= ' <bdo dir="ltr">('.$_info['ip'].')</bdo>';
        } else {
            $_user = '<bdo dir="ltr">'.$_info['ip'].'</bdo>';
        }
        $_user = '<span class="user">'.$_user.'</span>';
        $_sum  = ($_info['sum']) ? '<span class="sum"><bdi>'.hsc($_info['sum']).'</span></bdi>' : '';
        if ($_info['type']===DOKU_CHANGE_TYPE_MINOR_EDIT) $r_minor = 'class="minor"';

        $r_head_title = ($media) ? dformat($_rev) : $id.' ['.dformat($_rev).']';
        $r_head  = '<bdi><a class="wikilink1" href="'.$ml_or_wl($id).'">'.
        $r_head_title.'</a></bdi> '.
        '('.$lang['current'].')'.
        $head_separator.$_user.' '.$_sum;
    }else{
        $r_head = '&mdash; ('.$lang['current'].')';
    }

    return array($l_head, $r_head, $l_minor, $r_minor);
}

/**
 * Show diff
 * between current page version and provided $text
 * or between the revisions provided via GET or POST
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 * @param  string $text  when non-empty: compare with this text with most current version
 * @param  bool   $intro display the intro text
 * @param  string $type  type of the diff (inline or sidebyside)
 */
function html_diff($text = '', $intro = true, $type = null) {
```
