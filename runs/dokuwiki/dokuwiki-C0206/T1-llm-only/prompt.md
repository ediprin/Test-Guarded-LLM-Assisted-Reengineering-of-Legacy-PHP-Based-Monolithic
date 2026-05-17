You are assisting with bounded reengineering of a legacy PHP-based monolithic web application.

Task:
Improve maintainability of the selected PHP code region while preserving observable behavior.

Candidate:
- Candidate ID: dokuwiki-C0206
- Project: dokuwiki
- File: inc/template.php
- Lines: 520-576
- Candidate type: long_method_or_region

Rules:
- Return a unified diff only.
- Do not change public routes, request parameters, session keys, database table names, DOM selectors, or form field names.
- Do not migrate framework, architecture, database schema, or application structure.
- Keep the change local and bounded.

Code region:
```php
function tpl_actionlink($type, $pre = '', $suf = '', $inner = '', $return = false) {
    dbg_deprecated('see devel:menus');
    global $lang;
    $data = tpl_get_action($type);
    if($data === false) {
        return false;
    } elseif(!is_array($data)) {
        $out = sprintf($data, 'link');
    } else {
        /**
         * @var string $accesskey
         * @var string $id
         * @var string $method
         * @var bool   $nofollow
         * @var array  $params
         * @var string $replacement
         */
        extract($data);
        if(strpos($id, '#') === 0) {
            $linktarget = $id;
        } else {
            $linktarget = wl($id, $params);
        }
        $caption = $lang['btn_'.$type];
        if(strpos($caption, '%s')){
            $caption = sprintf($caption, $replacement);
        }
        $akey    = $addTitle = '';
        if($accesskey) {
            $akey     = 'accesskey="'.$accesskey.'" ';
            $addTitle = ' ['.strtoupper($accesskey).']';
        }
        $rel = $nofollow ? 'rel="nofollow" ' : '';
        $out = tpl_link(
            $linktarget, $pre.(($inner) ? $inner : $caption).$suf,
            'class="action '.$type.'" '.
                $akey.$rel.
                'title="'.hsc($caption).$addTitle.'"', true
        );
    }
    if($return) return $out;
    echo $out;
    return true;
}

/**
 * Check the actions and get data for buttons and links
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 * @author Matthias Grimm <matthiasgrimm@users.sourceforge.net>
 * @author Adrian Lang <mail@adrianlang.de>
 *
 * @param string $type
 * @return array|bool|string
 * @deprecated 2017-09-01 see devel:menus
 */
function tpl_get_action($type) {
```
