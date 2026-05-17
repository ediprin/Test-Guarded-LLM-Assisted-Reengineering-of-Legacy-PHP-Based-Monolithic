function html_btn($name, $id, $akey, $params, $method='get', $tooltip='', $label=false, $svg=null){
    global $conf;
    global $lang;

    if (!$label)
        $label = $lang['btn_'.$name];

    $ret = '';

    //filter id (without urlencoding)
    $id = idfilter($id,false);

    //make nice URLs even for buttons
    if($conf['userewrite'] == 2){
        $script = DOKU_BASE.DOKU_SCRIPT.'/'.$id;
    }elseif($conf['userewrite']){
        $script = DOKU_BASE.$id;
    }else{
        $script = DOKU_BASE.DOKU_SCRIPT;
        $params['id'] = $id;
    }

    $ret .= '<form class="button btn_'.$name.'" method="'.$method.'" action="'.$script.'"><div class="no">';

    if(is_array($params)){
        foreach($params as $key => $val) {
            $ret .= '<input type="hidden" name="'.$key.'" ';
            $ret .= 'value="'.hsc($val).'" />';
        }
    }

    if ($tooltip!='') {
        $tip = hsc($tooltip);
    }else{
        $tip = hsc($label);
    }

    $ret .= '<button type="submit" ';
    if($akey){
        $tip .= ' ['.strtoupper($akey).']';
        $ret .= 'accesskey="'.$akey.'" ';
    }
    $ret .= 'title="'.$tip.'">';
    if ($svg) {
        $ret .= '<span>' . hsc($label) . '</span>';
        $ret .= inlineSVG($svg);
    } else {
        $ret .= hsc($label);
    }
    $ret .= '</button>';
    $ret .= '</div></form>';

    return $ret;
}
/**
 * show a revision warning
 *
 * @author Szymon Olewniczak <dokuwiki@imz.re>
 */
function html_showrev() {
