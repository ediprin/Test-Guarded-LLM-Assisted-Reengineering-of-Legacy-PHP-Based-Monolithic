function tpl_youarehere($sep = null, $return = false) {
    global $conf;
    global $ID;
    global $lang;

    // check if enabled
    if(!$conf['youarehere']) return false;

    //set default
    if(is_null($sep)) $sep = ' » ';

    $out = '';

    $parts = explode(':', $ID);
    $count = count($parts);

    $out .= '<span class="bchead">'.$lang['youarehere'].' </span>';

    // always print the startpage
    $out .= '<span class="home">' . tpl_pagelink(':'.$conf['start'], null, true) . '</span>';

    // print intermediate namespace links
    $part = '';
    for($i = 0; $i < $count - 1; $i++) {
        $part .= $parts[$i].':';
        $page = $part;
        if($page == $conf['start']) continue; // Skip startpage

        // output
        $out .= $sep . tpl_pagelink($page, null, true);
    }

    // print current page, skipping start page, skipping for namespace index
    resolve_pageid('', $page, $exists);
    if (isset($page) && $page == $part.$parts[$i]) {
        if($return) return $out;
        print $out;
        return true;
    }
    $page = $part.$parts[$i];
    if($page == $conf['start']) {
        if($return) return $out;
        print $out;
        return true;
    }
    $out .= $sep;
    $out .= tpl_pagelink($page, null, true);
    if($return) return $out;
    print $out;
    return $out ? true : false;
}

/**
 * Print info if the user is logged in
 * and show full name in that case
 *
 * Could be enhanced with a profile link in future?
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 *
 * @return bool
 */
function tpl_userinfo() {
