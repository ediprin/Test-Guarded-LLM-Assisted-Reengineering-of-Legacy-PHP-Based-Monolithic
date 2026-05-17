You are assisting with bounded reengineering of a legacy PHP-based monolithic web application.

Task:
Improve maintainability of the selected PHP code region while preserving observable behavior.

Candidate:
- Candidate ID: dokuwiki-C0003
- Project: dokuwiki
- File: feed.php
- Lines: 189-461
- Candidate type: long_method_or_region

Rules:
- Return a unified diff only.
- Do not change public routes, request parameters, session keys, database table names, DOM selectors, or form field names.
- Do not migrate framework, architecture, database schema, or application structure.
- Keep the change local and bounded.

Code region:
```php
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
            if($ditem['date']) {
                $date = $ditem['date'];
            } elseif ($ditem['media']) {
                $date = @filemtime(mediaFN($id));
            } elseif (file_exists(wikiFN($id))) {
                $date = @filemtime(wikiFN($id));
            } elseif($meta['date']['modified']) {
                $date = $meta['date']['modified'];
            } else {
                $date = 0;
            }
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
            switch($opt['link_to']) {
                case 'page':
                    if($ditem['media']) {
                        $item->link = media_managerURL(
                            array(
                                 'image' => $id,
                                 'ns'    => getNS($id),
                                 'rev'   => $date
                            ), '&', true
                        );
                    } else {
                        $item->link = wl($id, 'rev='.$date, true, '&');
                    }
                    break;
                case 'rev':
                    if($ditem['media']) {
                        $item->link = media_managerURL(
                            array(
                                 'image'       => $id,
                                 'ns'          => getNS($id),
                                 'rev'         => $date,
                                 'tab_details' => 'history'
                            ), '&', true
                        );
                    } else {
                        $item->link = wl($id, 'do=revisions&rev='.$date, true, '&');
                    }
                    break;
                case 'current':
                    if($ditem['media']) {
                        $item->link = media_managerURL(
                            array(
                                 'image' => $id,
                                 'ns'    => getNS($id)
                            ), '&', true
                        );
                    } else {
                        $item->link = wl($id, '', true, '&');
                    }
                    break;
                case 'diff':
                default:
                    if($ditem['media']) {
                        $item->link = media_managerURL(
                            array(
                                 'image'       => $id,
                                 'ns'          => getNS($id),
                                 'rev'         => $date,
                                 'tab_details' => 'history',
                                 'mediado'     => 'diff'
                            ), '&', true
                        );
                    } else {
                        $item->link = wl($id, 'rev='.$date.'&do=diff', true, '&');
                    }
            }

            // add item content
            switch($opt['item_content']) {
                case 'diff':
                case 'htmldiff':
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

                    } else {
                        require_once(DOKU_INC.'inc/DifferenceEngine.php');
                        $pagelog = new PageChangeLog($id);
                        $revs = $pagelog->getRevisions(0, 1);
                        $rev  = $revs[0];

                        if($rev) {
                            $df = new Diff(explode("\n", rawWiki($id, $rev)),
                                           explode("\n", rawWiki($id, '')));
                        } else {
                            $df = new Diff(array(''),
                                           explode("\n", rawWiki($id, '')));
                        }

                        if($opt['item_content'] == 'htmldiff') {
                            // note: no need to escape diff output, TableDiffFormatter provides 'safe' html
                            $tdf     = new TableDiffFormatter();
                            $content = '<table>';
                            $content .= '<tr><th colspan="2" width="50%">'.$rev.'</th>';
                            $content .= '<th colspan="2" width="50%">'.$lang['current'].'</th></tr>';
                            $content .= $tdf->format($df);
                            $content .= '</table>';
                        } else {
                            // note: diff output must be escaped, UnifiedDiffFormatter provides plain text
                            $udf     = new UnifiedDiffFormatter();
                            $content = "<pre>\n".hsc($udf->format($df))."\n</pre>";
                        }
                    }
                    break;
                case 'html':
                    if($ditem['media']) {
                        if($size = media_image_preview_size($id, '', new JpegMeta(mediaFN($id)))) {
                            $more    = 'w='.$size[0].'&h='.$size[1].'&t='.@filemtime(mediaFN($id));
                            $src     = ml($id, $more, true, '&amp;', true);
                            $content = '<img src="'.$src.'" alt="'.$id.'" />';
                        } else {
                            $content = '';
                        }
                    } else {
                        if (@filemtime(wikiFN($id)) === $date) {
                            $content = p_wiki_xhtml($id, '', false);
                        } else {
                            $content = p_wiki_xhtml($id, $date, false);
                        }
                        // no TOC in feeds
                        $content = preg_replace('/(<!-- TOC START -->).*(<!-- TOC END -->)/s', '', $content);

                        // add alignment for images
                        $content = preg_replace('/(<img .*?class="medialeft")/s', '\\1 align="left"', $content);
                        $content = preg_replace('/(<img .*?class="mediaright")/s', '\\1 align="right"', $content);

                        // make URLs work when canonical is not set, regexp instead of rerendering!
                        if(!$conf['canonical']) {
                            $base    = preg_quote(DOKU_REL, '/');
                            $content = preg_replace('/(<a href|<img src)="('.$base.')/s', '$1="'.DOKU_URL, $content);
                        }
                    }

                    break;
                case 'abstract':
                default:
                    if($ditem['media']) {
                        if($size = media_image_preview_size($id, '', new JpegMeta(mediaFN($id)))) {
                            $more    = 'w='.$size[0].'&h='.$size[1].'&t='.@filemtime(mediaFN($id));
                            $src     = ml($id, $more, true, '&amp;', true);
                            $content = '<img src="'.$src.'" alt="'.$id.'" />';
                        } else {
                            $content = '';
                        }
                    } else {
                        $content = $meta['description']['abstract'];
                    }
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
```
