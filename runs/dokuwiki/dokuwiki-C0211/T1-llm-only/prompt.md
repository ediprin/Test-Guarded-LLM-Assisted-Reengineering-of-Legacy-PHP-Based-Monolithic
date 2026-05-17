You are assisting with bounded reengineering of a legacy PHP-based monolithic web application.

Task:
Improve maintainability of the selected PHP code region while preserving observable behavior.

Candidate:
- Candidate ID: dokuwiki-C0211
- Project: dokuwiki
- File: inc/template.php
- Lines: 916-1003
- Candidate type: long_method_or_region

Rules:
- Return a unified diff only.
- Do not change public routes, request parameters, session keys, database table names, DOM selectors, or form field names.
- Do not migrate framework, architecture, database schema, or application structure.
- Keep the change local and bounded.

Code region:
```php
function tpl_pagetitle($id = null, $ret = false) {
    global $ACT, $INPUT, $conf, $lang;

    if(is_null($id)) {
        global $ID;
        $id = $ID;
    }

    $name = $id;
    if(useHeading('navigation')) {
        $first_heading = p_get_first_heading($id);
        if($first_heading) $name = $first_heading;
    }

    // default page title is the page name, modify with the current action
    switch ($ACT) {
        // admin functions
        case 'admin' :
            $page_title = $lang['btn_admin'];
            // try to get the plugin name
            /** @var $plugin DokuWiki_Admin_Plugin */
            if ($plugin = plugin_getRequestAdminPlugin()){
                $plugin_title = $plugin->getMenuText($conf['lang']);
                $page_title = $plugin_title ? $plugin_title : $plugin->getPluginName();
            }
            break;

        // user functions
        case 'login' :
        case 'profile' :
        case 'register' :
        case 'resendpwd' :
            $page_title = $lang['btn_'.$ACT];
            break;

         // wiki functions
        case 'search' :
        case 'index' :
            $page_title = $lang['btn_'.$ACT];
            break;

        // page functions
        case 'edit' :
            $page_title = "✎ ".$name;
            break;

        case 'revisions' :
            $page_title = $name . ' - ' . $lang['btn_revs'];
            break;

        case 'backlink' :
        case 'recent' :
        case 'subscribe' :
            $page_title = $name . ' - ' . $lang['btn_'.$ACT];
            break;

        default : // SHOW and anything else not included
            $page_title = $name;
    }

    if($ret) {
        return hsc($page_title);
    } else {
        print hsc($page_title);
        return true;
    }
}

/**
 * Returns the requested EXIF/IPTC tag from the current image
 *
 * If $tags is an array all given tags are tried until a
 * value is found. If no value is found $alt is returned.
 *
 * Which texts are known is defined in the functions _exifTagNames
 * and _iptcTagNames() in inc/jpeg.php (You need to prepend IPTC
 * to the names of the latter one)
 *
 * Only allowed in: detail.php
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 *
 * @param array|string $tags tag or array of tags to try
 * @param string       $alt  alternative output if no data was found
 * @param null|string  $src  the image src, uses global $SRC if not given
 * @return string
 */
function tpl_img_getTag($tags, $alt = '', $src = null) {
```
