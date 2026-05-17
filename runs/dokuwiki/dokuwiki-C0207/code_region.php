function tpl_get_action($type) {
    dbg_deprecated('see devel:menus');
    if($type == 'history') $type = 'revisions';
    if($type == 'subscription') $type = 'subscribe';
    if($type == 'img_backto') $type = 'imgBackto';

    $class = '\\dokuwiki\\Menu\\Item\\' . ucfirst($type);
    if(class_exists($class)) {
        try {
            /** @var \dokuwiki\Menu\Item\AbstractItem $item */
            $item = new $class;
            $data = $item->getLegacyData();
            $unknown = false;
        } catch(\RuntimeException $ignored) {
            return false;
        }
    } else {
        global $ID;
        $data = array(
            'accesskey' => null,
            'type' => $type,
            'id' => $ID,
            'method' => 'get',
            'params' => array('do' => $type),
            'nofollow' => true,
            'replacement' => '',
        );
        $unknown = true;
    }

    $evt = new Doku_Event('TPL_ACTION_GET', $data);
    if($evt->advise_before()) {
        //handle unknown types
        if($unknown) {
            $data = '[unknown %s type]';
        }
    }
    $evt->advise_after();
    unset($evt);

    return $data;
}

/**
 * Wrapper around tpl_button() and tpl_actionlink()
 *
 * @author Anika Henke <anika@selfthinker.org>
 *
 * @param string        $type action command
 * @param bool          $link link or form button?
 * @param string|bool   $wrapper HTML element wrapper
 * @param bool          $return return or print
 * @param string        $pre prefix for links
 * @param string        $suf suffix for links
 * @param string        $inner inner HTML for links
 * @return bool|string
 * @deprecated 2017-09-01 see devel:menus
 */
function tpl_action($type, $link = false, $wrapper = false, $return = false, $pre = '', $suf = '', $inner = '') {
