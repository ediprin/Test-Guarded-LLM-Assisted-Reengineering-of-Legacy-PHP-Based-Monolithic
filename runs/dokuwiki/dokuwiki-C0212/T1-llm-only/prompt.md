You are assisting with bounded reengineering of a legacy PHP-based monolithic web application.

Task:
Improve maintainability of the selected PHP code region while preserving observable behavior.

Candidate:
- Candidate ID: dokuwiki-C0212
- Project: dokuwiki
- File: inc/template.php
- Lines: 1090-1150
- Candidate type: long_method_or_region

Rules:
- Return a unified diff only.
- Do not change public routes, request parameters, session keys, database table names, DOM selectors, or form field names.
- Do not migrate framework, architecture, database schema, or application structure.
- Keep the change local and bounded.

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
