<?php
/**
 * XML feed export
 *
 * @license    GPL 2 (http://www.gnu.org/licenses/gpl.html)
 * @author     Andreas Gohr <andi@splitbrain.org>
 *
 * @global array $conf
 * @global Input $INPUT
 */

if(!defined('DOKU_INC')) define('DOKU_INC', dirname(__FILE__).'/');
require_once(DOKU_INC.'inc/init.php');

//close session
session_write_close();

//feed disabled?
if(!actionOK('rss')) {
    http_status(404);
    echo '<error>RSS feed is disabled.</error>';
    exit;
}

// get params
$opt = rss_parseOptions();

// the feed is dynamic - we need a cache for each combo
// (but most people just use the default feed so it's still effective)
$key   = join('', array_values($opt)).'$'.$_SERVER['REMOTE_USER'].'$'.$_SERVER['HTTP_HOST'].$_SERVER['SERVER_PORT'];
$cache = new cache($key, '.feed');

// prepare cache depends
$depends['files'] = getConfigFiles('main');
$depends['age']   = $conf['rss_update'];
$depends['purge'] = $INPUT->bool('purge');

// check cacheage and deliver if nothing has changed since last
// time or the update interval has not passed, also handles conditional requests
header('Cache-Control: must-revalidate, post-check=0, pre-check=0');
header('Pragma: public');
header('Content-Type: application/xml; charset=utf-8');
header('X-Robots-Tag: noindex');
if($cache->useCache($depends)) {
    http_conditionalRequest($cache->_time);
    if($conf['allowdebug']) header("X-CacheUsed: $cache->cache");
    print $cache->retrieveCache();
    exit;
} else {
    http_conditionalRequest(time());
}

// create new feed
$rss                 = new UniversalFeedCreator();
$rss->title          = $conf['title'].(($opt['namespace']) ? ' '.$opt['namespace'] : '');
$rss->link           = DOKU_URL;
$rss->syndicationURL = DOKU_URL.'feed.php';
$rss->cssStyleSheet  = DOKU_URL.'lib/exe/css.php?s=feed';

$image        = new FeedImage();
$image->title = $conf['title'];
$image->url   = tpl_getMediaFile(array(':wiki:favicon.ico', ':favicon.ico', 'images/favicon.ico'), true);
$image->link  = DOKU_URL;
$rss->image   = $image;

$data  = null;
$modes = array(
    'list'   => 'rssListNamespace',
    'search' => 'rssSearch',
    'recent' => 'rssRecentChanges'
);
if(isset($modes[$opt['feed_mode']])) {
    $data = $modes[$opt['feed_mode']]($opt);
} else {
    $eventData = array(
        'opt'  => &$opt,
        'data' => &$data,
    );
    $event     = new Doku_Event('FEED_MODE_UNKNOWN', $eventData);
    if($event->advise_before(true)) {
        echo sprintf('<error>Unknown feed mode %s</error>', hsc($opt['feed_mode']));
        exit;
    }
    $event->advise_after();
}

rss_buildItems($rss, $data, $opt);
$feed = $rss->createFeed($opt['feed_type']);

// save cachefile
$cache->storeCache($feed);

// finally deliver
print $feed;

// ---------------------------------------------------------------- //

/**
 * Get URL parameters and config options and return an initialized option array
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 */
function rss_parseOptions() {
    global $conf;
    global $INPUT;

    $opt = array();

    foreach(array(
                // Basic feed properties
                // Plugins may probably want to add new values to these
                // properties for implementing own feeds

                // One of: list, search, recent
                'feed_mode'    => array('str', 'mode', 'recent'),
                // One of: diff, page, rev, current
                'link_to'      => array('str', 'linkto', $conf['rss_linkto']),
                // One of: abstract, diff, htmldiff, html
                'item_content' => array('str', 'content', $conf['rss_content']),

                // Special feed properties
                // These are only used by certain feed_modes

                // String, used for feed title, in list and rc mode
                'namespace'    => array('str', 'ns', null),
                // Positive integer, only used in rc mode
                'items'        => array('int', 'num', $conf['recent']),
                // Boolean, only used in rc mode
                'show_minor'   => array('bool', 'minor', false),
                // String, only used in list mode
                'sort'         => array('str', 'sort', 'natural'),
                // String, only used in search mode
                'search_query' => array('str', 'q', null),
                // One of: pages, media, both
                'content_type' => array('str', 'view', $conf['rss_media'])

            ) as $name => $val) {
        $opt[$name] = $INPUT->{$val[0]}($val[1], $val[2], true);
    }

    $opt['items']      = max(0, (int) $opt['items']);
    $opt['show_minor'] = (bool) $opt['show_minor'];
    $opt['sort'] = valid_input_set('sort', array('default' => 'natural', 'date'), $opt);

    $opt['guardmail'] = ($conf['mailguard'] != '' && $conf['mailguard'] != 'none');

    $type = $INPUT->valid(
        'type',
        array( 'rss', 'rss2', 'atom', 'atom1', 'rss1'),
        $conf['rss_type']
    );
    switch($type) {
        case 'rss':
            $opt['feed_type'] = 'RSS0.91';
            $opt['mime_type'] = 'text/xml';
            break;
        case 'rss2':
            $opt['feed_type'] = 'RSS2.0';
            $opt['mime_type'] = 'text/xml';
            break;
        case 'atom':
            $opt['feed_type'] = 'ATOM0.3';
            $opt['mime_type'] = 'application/xml';
            break;
        case 'atom1':
            $opt['feed_type'] = 'ATOM1.0';
            $opt['mime_type'] = 'application/atom+xml';
            break;
        default:
            $opt['feed_type'] = 'RSS1.0';
            $opt['mime_type'] = 'application/xml';
    }

    $eventData = array(
        'opt' => &$opt,
    );
    trigger_event('FEED_OPTS_POSTPROCESS', $eventData);
    return $opt;
}

/**
 * Add recent changed pages to a feed object
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 * @param  FeedCreator $rss the FeedCreator Object
 * @param  array       $data the items to add
 * @param  array       $opt  the feed options
 */
function rss_buildItems(&$rss, &$data, $opt) {
    global $conf;
    global $lang;
    /* @var DokuWiki_Auth_Plugin $auth */
    global $auth;

    $eventData = array(
        'rss'  => &$rss,
        'data' => &$data,
        'opt'  => &$opt,
    );
    $event     = new Doku_Event('FEED_DATA_PROCESS', $eventData);
    if($event->advise_before(false)) {
        foreach($data as $ditem) {
            if(!is_array($ditem)) {
                // not an array? then only a list of IDs was given
                $ditem = array('id' => $ditem);
            }

            $item = new FeedItem();
            $id   = $ditem['id'];
            if(!$ditem['media']) {
                $meta = p_get_metadata($id);
            } else {
                $meta = array();
            }

            // add date
            $date = rss_itemDate($ditem, $id, $meta);
            if($date) $item->date = date('r', $date);

            // add title
            if($conf['useheading'] && $meta['title']) {
                $item->title = $meta['title'];
            } else {
                $item->title = $ditem['id'];
            }
            if($conf['rss_show_summary'] && !empty($ditem['sum'])) {
                $item->title .= ' - '.strip_tags($ditem['sum']);
            }

            // add item link
            $item->link = rss_itemLink($ditem, $id, $date, $opt['link_to']);

            // add item content
            switch($opt['item_content']) {
                case 'diff':
                case 'htmldiff':
                    $content = rss_itemDiffContent($ditem, $id, $opt['item_content'], $lang);
                    break;
                case 'html':
                    $content = rss_itemHtmlContent($ditem, $id, $date, $conf);

                    break;
                case 'abstract':
                default:
                    $content = rss_itemAbstractContent($ditem, $id, $meta);
            }
            $item->description = $content; //FIXME a plugin hook here could be senseful

            // add user
            # FIXME should the user be pulled from metadata as well?
            $user         = @$ditem['user']; // the @ spares time repeating lookup
            if(blank($user)) {
                $item->author = 'Anonymous';
                $item->authorEmail = 'anonymous@undisclosed.example.com';
            } else {
                $item->author = $user;
                $item->authorEmail = $user . '@undisclosed.example.com';

                // get real user name if configured
                if($conf['useacl'] && $auth) {
                    $userInfo = $auth->getUserData($user);
                    if($userInfo) {
                        switch($conf['showuseras']) {
                            case 'username':
                            case 'username_link':
                                $item->author = $userInfo['name'];
                                break;
                            default:
                                $item->author = $user;
                                break;
                        }
                    } else {
                        $item->author = $user;
                    }
                }
            }

            // add category
            if(isset($meta['subject'])) {
                $item->category = $meta['subject'];
            } else {
                $cat = getNS($id);
                if($cat) $item->category = $cat;
            }

            // finally add the item to the feed object, after handing it to registered plugins
            $evdata = array(
                'item'  => &$item,
                'opt'   => &$opt,
                'ditem' => &$ditem,
                'rss'   => &$rss
            );
            $evt    = new Doku_Event('FEED_ITEM_ADD', $evdata);
            if($evt->advise_before()) {
                $rss->addItem($item);
            }
            $evt->advise_after(); // for completeness
        }
    }
    $event->advise_after();
}

/**
 * Add recent changed pages to the feed object
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 */
function rssRecentChanges($opt) {
    global $conf;
    $flags = RECENTS_SKIP_DELETED;
    if(!$opt['show_minor']) $flags += RECENTS_SKIP_MINORS;
    if($opt['content_type'] == 'media' && $conf['mediarevisions']) $flags += RECENTS_MEDIA_CHANGES;
    if($opt['content_type'] == 'both' && $conf['mediarevisions']) $flags += RECENTS_MEDIA_PAGES_MIXED;

    $recents = getRecents(0, $opt['items'], $opt['namespace'], $flags);
    return $recents;
}

/**
 * Add all pages of a namespace to the feed object
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 */
function rssListNamespace($opt) {
    require_once(DOKU_INC.'inc/search.php');
    global $conf;

    $ns = ':'.cleanID($opt['namespace']);
    $ns = utf8_encodeFN(str_replace(':', '/', $ns));

    $data = array();
    $search_opts = array(
        'depth' => 1,
        'pagesonly' => true,
        'listfiles' => true
    );
    search($data, $conf['datadir'], 'search_universal', $search_opts, $ns, $lvl = 1, $opt['sort']);

    return $data;
}

/**
 * Add the result of a full text search to the feed object
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 */
function rssSearch($opt) {
    if(!$opt['search_query']) return array();

    require_once(DOKU_INC.'inc/fulltext.php');
    $data = ft_pageSearch($opt['search_query'], $poswords);
    $data = array_keys($data);

    return $data;
}

/**
 * Return the timestamp for a feed item.
 */
function rss_itemDate($ditem, $id, $meta) {
    if($ditem['date']) {
        return $ditem['date'];
    } elseif ($ditem['media']) {
        return @filemtime(mediaFN($id));
    } elseif (file_exists(wikiFN($id))) {
        return @filemtime(wikiFN($id));
    } elseif($meta['date']['modified']) {
        return $meta['date']['modified'];
    }

    return 0;
}

/**
 * Return the link for a feed item.
 */
function rss_itemLink($ditem, $id, $date, $linkTo) {
    if($linkTo === 'page') {
        if($ditem['media']) {
            return media_managerURL(array('image' => $id, 'ns' => getNS($id), 'rev' => $date), '&', true);
        }
        return wl($id, 'rev='.$date, true, '&');
    }

    if($linkTo === 'rev') {
        if($ditem['media']) {
            return media_managerURL(array('image' => $id, 'ns' => getNS($id), 'rev' => $date, 'tab_details' => 'history'), '&', true);
        }
        return wl($id, 'do=revisions&rev='.$date, true, '&');
    }

    if($linkTo === 'current') {
        if($ditem['media']) {
            return media_managerURL(array('image' => $id, 'ns' => getNS($id)), '&', true);
        }
        return wl($id, '', true, '&');
    }

    if($ditem['media']) {
        return media_managerURL(array('image' => $id, 'ns' => getNS($id), 'rev' => $date, 'tab_details' => 'history', 'mediado' => 'diff'), '&', true);
    }
    return wl($id, 'rev='.$date.'&do=diff', true, '&');
}

/**
 * Return diff content for a feed item.
 */
function rss_itemDiffContent($ditem, $id, $itemContent, $lang) {
    if($ditem['media']) {
        $medialog = new MediaChangeLog($id);
        $revs  = $medialog->getRevisions(0, 1);
        $rev   = $revs[0];
        $src_r = '';
        $src_l = '';

        if($size = media_image_preview_size($id, '', new JpegMeta(mediaFN($id)), 300)) {
            $more  = 'w='.$size[0].'&h='.$size[1].'&t='.@filemtime(mediaFN($id));
            $src_r = ml($id, $more, true, '&amp;', true);
        }
        if($rev && $size = media_image_preview_size($id, $rev, new JpegMeta(mediaFN($id, $rev)), 300)) {
            $more  = 'rev='.$rev.'&w='.$size[0].'&h='.$size[1];
            $src_l = ml($id, $more, true, '&amp;', true);
        }
        $content = '';
        if($src_r) {
            $content = '<table>';
            $content .= '<tr><th width="50%">'.$rev.'</th>';
            $content .= '<th width="50%">'.$lang['current'].'</th></tr>';
            $content .= '<tr align="center"><td><img src="'.$src_l.'" alt="" /></td><td>';
            $content .= '<img src="'.$src_r.'" alt="'.$id.'" /></td></tr>';
            $content .= '</table>';
        }
        return $content;
    }

    require_once(DOKU_INC.'inc/DifferenceEngine.php');
    $pagelog = new PageChangeLog($id);
    $revs = $pagelog->getRevisions(0, 1);
    $rev  = $revs[0];

    if($rev) {
        $df = new Diff(explode("\n", rawWiki($id, $rev)), explode("\n", rawWiki($id, '')));
    } else {
        $df = new Diff(array(''), explode("\n", rawWiki($id, '')));
    }

    if($itemContent == 'htmldiff') {
        $tdf     = new TableDiffFormatter();
        $content = '<table>';
        $content .= '<tr><th colspan="2" width="50%">'.$rev.'</th>';
        $content .= '<th colspan="2" width="50%">'.$lang['current'].'</th></tr>';
        $content .= $tdf->format($df);
        $content .= '</table>';
    } else {
        $udf     = new UnifiedDiffFormatter();
        $content = "<pre>\n".hsc($udf->format($df))."\n</pre>";
    }

    return $content;
}

/**
 * Return HTML content for a feed item.
 */
function rss_itemHtmlContent($ditem, $id, $date, $conf) {
    if($ditem['media']) {
        if($size = media_image_preview_size($id, '', new JpegMeta(mediaFN($id)))) {
            $more    = 'w='.$size[0].'&h='.$size[1].'&t='.@filemtime(mediaFN($id));
            $src     = ml($id, $more, true, '&amp;', true);
            return '<img src="'.$src.'" alt="'.$id.'" />';
        }
        return '';
    }

    if (@filemtime(wikiFN($id)) === $date) {
        $content = p_wiki_xhtml($id, '', false);
    } else {
        $content = p_wiki_xhtml($id, $date, false);
    }
    $content = preg_replace('/(<!-- TOC START -->).*(<!-- TOC END -->)/s', '', $content);
    $content = preg_replace('/(<img .*?class="medialeft")/s', '\\1 align="left"', $content);
    $content = preg_replace('/(<img .*?class="mediaright")/s', '\\1 align="right"', $content);

    if(!$conf['canonical']) {
        $base    = preg_quote(DOKU_REL, '/');
        $content = preg_replace('/(<a href|<img src)="('.$base.')/s', '$1="'.DOKU_URL, $content);
    }

    return $content;
}

/**
 * Return abstract content for a feed item.
 */
function rss_itemAbstractContent($ditem, $id, $meta) {
    if($ditem['media']) {
        if($size = media_image_preview_size($id, '', new JpegMeta(mediaFN($id)))) {
            $more    = 'w='.$size[0].'&h='.$size[1].'&t='.@filemtime(mediaFN($id));
            $src     = ml($id, $more, true, '&amp;', true);
            return '<img src="'.$src.'" alt="'.$id.'" />';
        }
        return '';
    }

    return $meta['description']['abstract'];
}

//Setup VIM: ex: et ts=4 :
