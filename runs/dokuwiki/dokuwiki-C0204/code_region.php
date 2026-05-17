function tpl_metaheaders($alt = true) {
    global $ID;
    global $REV;
    global $INFO;
    global $JSINFO;
    global $ACT;
    global $QUERY;
    global $lang;
    global $conf;
    global $updateVersion;
    /** @var Input $INPUT */
    global $INPUT;

    // prepare the head array
    $head = array();

    // prepare seed for js and css
    $tseed   = $updateVersion;
    $depends = getConfigFiles('main');
    $depends[] = DOKU_CONF."tpl/".$conf['template']."/style.ini";
    foreach($depends as $f) $tseed .= @filemtime($f);
    $tseed   = md5($tseed);

    // the usual stuff
    $head['meta'][] = array('name'=> 'generator', 'content'=> 'DokuWiki');
    if(actionOK('search')) {
        $head['link'][] = array(
            'rel' => 'search', 'type'=> 'application/opensearchdescription+xml',
            'href'=> DOKU_BASE.'lib/exe/opensearch.php', 'title'=> $conf['title']
        );
    }

    $head['link'][] = array('rel'=> 'start', 'href'=> DOKU_BASE);
    if(actionOK('index')) {
        $head['link'][] = array(
            'rel'  => 'contents', 'href'=> wl($ID, 'do=index', false, '&'),
            'title'=> $lang['btn_index']
        );
    }

    if (actionOK('manifest')) {
        $head['link'][] = array('rel'=> 'manifest', 'href'=> DOKU_BASE.'lib/exe/manifest.php');
    }

    $styleUtil = new \dokuwiki\StyleUtils();
    $styleIni = $styleUtil->cssStyleini($conf['template']);
    $replacements = $styleIni['replacements'];
    if (!empty($replacements['__theme_color__'])) {
        $head['meta'][] = array('name' => 'theme-color', 'content' => $replacements['__theme_color__']);
    }

    if($alt) {
        if(actionOK('rss')) {
            $head['link'][] = array(
                'rel'  => 'alternate', 'type'=> 'application/rss+xml',
                'title'=> $lang['btn_recent'], 'href'=> DOKU_BASE.'feed.php'
            );
            $head['link'][] = array(
                'rel'  => 'alternate', 'type'=> 'application/rss+xml',
                'title'=> $lang['currentns'],
                'href' => DOKU_BASE.'feed.php?mode=list&ns='.$INFO['namespace']
            );
        }
        if(($ACT == 'show' || $ACT == 'search') && $INFO['writable']) {
            $head['link'][] = array(
                'rel'  => 'edit',
                'title'=> $lang['btn_edit'],
                'href' => wl($ID, 'do=edit', false, '&')
            );
        }

        if(actionOK('rss') && $ACT == 'search') {
            $head['link'][] = array(
                'rel'  => 'alternate', 'type'=> 'application/rss+xml',
                'title'=> $lang['searchresult'],
                'href' => DOKU_BASE.'feed.php?mode=search&q='.$QUERY
            );
        }

        if(actionOK('export_xhtml')) {
            $head['link'][] = array(
                'rel' => 'alternate', 'type'=> 'text/html', 'title'=> $lang['plainhtml'],
                'href'=> exportlink($ID, 'xhtml', '', false, '&')
            );
        }

        if(actionOK('export_raw')) {
            $head['link'][] = array(
                'rel' => 'alternate', 'type'=> 'text/plain', 'title'=> $lang['wikimarkup'],
                'href'=> exportlink($ID, 'raw', '', false, '&')
            );
        }
    }

    // setup robot tags apropriate for different modes
    if(($ACT == 'show' || $ACT == 'export_xhtml') && !$REV) {
        if($INFO['exists']) {
            //delay indexing:
            if((time() - $INFO['lastmod']) >= $conf['indexdelay'] && !isHiddenPage($ID) ) {
                $head['meta'][] = array('name'=> 'robots', 'content'=> 'index,follow');
            } else {
                $head['meta'][] = array('name'=> 'robots', 'content'=> 'noindex,nofollow');
            }
            $canonicalUrl = wl($ID, '', true, '&');
            if ($ID == $conf['start']) {
                $canonicalUrl = DOKU_URL;
            }
            $head['link'][] = array('rel'=> 'canonical', 'href'=> $canonicalUrl);
        } else {
            $head['meta'][] = array('name'=> 'robots', 'content'=> 'noindex,follow');
        }
    } elseif(defined('DOKU_MEDIADETAIL')) {
        $head['meta'][] = array('name'=> 'robots', 'content'=> 'index,follow');
    } else {
        $head['meta'][] = array('name'=> 'robots', 'content'=> 'noindex,nofollow');
    }

    // set metadata
    if($ACT == 'show' || $ACT == 'export_xhtml') {
        // keywords (explicit or implicit)
        if(!empty($INFO['meta']['subject'])) {
            $head['meta'][] = array('name'=> 'keywords', 'content'=> join(',', $INFO['meta']['subject']));
        } else {
            $head['meta'][] = array('name'=> 'keywords', 'content'=> str_replace(':', ',', $ID));
        }
    }

    // load stylesheets
    $head['link'][] = array(
        'rel' => 'stylesheet', 'type'=> 'text/css',
        'href'=> DOKU_BASE.'lib/exe/css.php?t='.rawurlencode($conf['template']).'&tseed='.$tseed
    );

    $script = "var NS='".$INFO['namespace']."';";
    if($conf['useacl'] && $INPUT->server->str('REMOTE_USER')) {
        $script .= "var SIG='".toolbar_signature()."';";
    }
    jsinfo();
    $script .= 'var JSINFO = ' . json_encode($JSINFO).';';
    $head['script'][] = array('type'=> 'text/javascript', '_data'=> $script);

    // load jquery
    $jquery = getCdnUrls();
    foreach($jquery as $src) {
        $head['script'][] = array(
            'type' => 'text/javascript', 'charset' => 'utf-8', '_data' => '', 'src' => $src
        );
    }

    // load our javascript dispatcher
    $head['script'][] = array(
        'type'=> 'text/javascript', 'charset'=> 'utf-8', '_data'=> '',
        'src' => DOKU_BASE.'lib/exe/js.php'.'?t='.rawurlencode($conf['template']).'&tseed='.$tseed
    );

    // trigger event here
    trigger_event('TPL_METAHEADER_OUTPUT', $head, '_tpl_metaheaders_action', true);
    return true;
}

/**
 * prints the array build by tpl_metaheaders
 *
 * $data is an array of different header tags. Each tag can have multiple
 * instances. Attributes are given as key value pairs. Values will be HTML
 * encoded automatically so they should be provided as is in the $data array.
 *
 * For tags having a body attribute specify the body data in the special
 * attribute '_data'. This field will NOT BE ESCAPED automatically.
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 *
 * @param array $data
 */
function _tpl_metaheaders_action($data) {
