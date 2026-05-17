function tpl_breadcrumbs($sep = null, $return = false) {
    global $lang;
    global $conf;

    //check if enabled
    if(!$conf['breadcrumbs']) return false;

    //set default
    if(is_null($sep)) $sep = '•';

    $out='';

    $crumbs = breadcrumbs(); //setup crumb trace

    $crumbs_sep = ' <span class="bcsep">'.$sep.'</span> ';

    //render crumbs, highlight the last one
    $out .= '<span class="bchead">'.$lang['breadcrumb'].'</span>';
    $last = count($crumbs);
    $i    = 0;
    foreach($crumbs as $id => $name) {
        $i++;
        $out .= $crumbs_sep;
        if($i == $last) $out .= '<span class="curid">';
        $out .= '<bdi>' . tpl_link(wl($id), hsc($name), 'class="breadcrumbs" title="'.$id.'"', true) .  '</bdi>';
        if($i == $last) $out .= '</span>';
    }
    if($return) return $out;
    print $out;
    return $out ? true : false;
}

/**
 * Hierarchical breadcrumbs
 *
 * This code was suggested as replacement for the usual breadcrumbs.
 * It only makes sense with a deep site structure.
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 * @author Nigel McNie <oracle.shinoda@gmail.com>
 * @author Sean Coates <sean@caedmon.net>
 * @author <fredrik@averpil.com>
 * @todo   May behave strangely in RTL languages
 *
 * @param string $sep Separator between entries
 * @param bool   $return return or print
 * @return bool|string
 */
function tpl_youarehere($sep = null, $return = false) {
