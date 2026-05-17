You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0212
- Project: dokuwiki
- File: inc/template.php
- Lines: 1090-1150
- Candidate type: long_method_or_region
- Oracle IDs: dokuwiki_home_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0212",
  "subject_id": "dokuwiki",
  "file": "inc/template.php",
  "lines": [
    1090,
    1150
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
function tpl_img($maxwidth = 0, $maxheight = 0, $link = true, $params = null) {
    global $IMG;
    /** @var Input $INPUT */
    global $INPUT;
    global $REV;
    $w = (int) tpl_img_getTag('File.Width');
    $h = (int) tpl_img_getTag('File.Height');

    //resize to given max values
    $ratio = 1;
    if($w >= $h) {
        if($maxwidth && $w >= $maxwidth) {
            $ratio = $maxwidth / $w;
        } elseif($maxheight && $h > $maxheight) {
            $ratio = $maxheight / $h;
        }
    } else {
        if($maxheight && $h >= $maxheight) {
            $ratio = $maxheight / $h;
        } elseif($maxwidth && $w > $maxwidth) {
            $ratio = $maxwidth / $w;
        }
    }
    if($ratio) {
        $w = floor($ratio * $w);
        $h = floor($ratio * $h);
    }

    //prepare URLs
    $url = ml($IMG, array('cache'=> $INPUT->str('cache'),'rev'=>$REV), true, '&');
    $src = ml($IMG, array('cache'=> $INPUT->str('cache'),'rev'=>$REV, 'w'=> $w, 'h'=> $h), true, '&');

    //prepare attributes
    $alt = tpl_img_getTag('Simple.Title');
    if(is_null($params)) {
        $p = array();
    } else {
        $p = $params;
    }
    if($w) $p['width'] = $w;
    if($h) $p['height'] = $h;
    $p['class'] = 'img_detail';
    if($alt) {
        $p['alt']   = $alt;
        $p['title'] = $alt;
    } else {
        $p['alt'] = '';
    }
    $p['src'] = $src;

    $data = array('url'=> ($link ? $url : null), 'params'=> $p);
    return trigger_event('TPL_IMG_DISPLAY', $data, '_tpl_img_action', true);
}

/**
 * Default action for TPL_IMG_DISPLAY
 *
 * @param array $data
 * @return bool
 */
function _tpl_img_action($data) {
```
