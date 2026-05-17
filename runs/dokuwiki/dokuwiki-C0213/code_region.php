function tpl_mediaContent($fromajax = false, $sort='natural') {
    global $IMG;
    global $AUTH;
    global $INUSE;
    global $NS;
    global $JUMPTO;
    /** @var Input $INPUT */
    global $INPUT;

    $do = $INPUT->extract('do')->str('do');
    if(in_array($do, array('save', 'cancel'))) $do = '';

    if(!$do) {
        if($INPUT->bool('edit')) {
            $do = 'metaform';
        } elseif(is_array($INUSE)) {
            $do = 'filesinuse';
        } else {
            $do = 'filelist';
        }
    }

    // output the content pane, wrapped in an event.
    if(!$fromajax) ptln('<div id="media__content">');
    $data = array('do' => $do);
    $evt  = new Doku_Event('MEDIAMANAGER_CONTENT_OUTPUT', $data);
    if($evt->advise_before()) {
        $do = $data['do'];
        if($do == 'filesinuse') {
            media_filesinuse($INUSE, $IMG);
        } elseif($do == 'filelist') {
            media_filelist($NS, $AUTH, $JUMPTO,false,$sort);
        } elseif($do == 'searchlist') {
            media_searchlist($INPUT->str('q'), $NS, $AUTH);
        } else {
            msg('Unknown action '.hsc($do), -1);
        }
    }
    $evt->advise_after();
    unset($evt);
    if(!$fromajax) ptln('</div>');

}

/**
 * Prints the central column in full-screen media manager
 * Depending on the opened tab this may be a list of
 * files in a namespace, upload form or search form
 *
 * @author Kate Arzamastseva <pshns@ukr.net>
 */
function tpl_mediaFileList() {
