<?php
/**
 * DokuWiki mainscript
 *
 * @license    GPL 2 (http://www.gnu.org/licenses/gpl.html)
 * @author     Andreas Gohr <andi@splitbrain.org>
 *
 * @global Input $INPUT
 */

// update message version - always use a string to avoid localized floats!
$updateVersion = "50.2";

//  xdebug_start_profiling();

/**
 * Determine the requested action from server and request parameters.
 *
 * @return string
 */
function doku_get_requested_action()
{
    if(isset($_SERVER['HTTP_X_DOKUWIKI_DO'])) {
        return trim(strtolower($_SERVER['HTTP_X_DOKUWIKI_DO']));
    } elseif(!empty($_REQUEST['idx'])) {
        return 'index';
    } elseif(isset($_REQUEST['do'])) {
        return $_REQUEST['do'];
    }

    return 'show';
}

/**
 * Parse a user supplied date value into a timestamp or null.
 *
 * @param string|null $date_at
 * @return int|null
 */
function doku_parse_date_at($date_at)
{
    global $lang;

    if(!$date_at) return null;

    $date_parse = strtotime($date_at);
    if($date_parse) {
        return $date_parse;
    }

    // check for UNIX Timestamp
    $date_parse = @date('Ymd', $date_at);
    if(!$date_parse || $date_parse === '19700101') {
        msg(sprintf($lang['unable_to_parse_date'], hsc($date_at)));
        return null;
    }

    return $date_parse;
}

/**
 * Resolve the revision to use for a selected date.
 *
 * @param string $id
 * @param int|null $date_at
 * @return array{0:int|null,1:int|null}
 */
function doku_resolve_revision_for_date($id, $date_at)
{
    global $conf, $lang;

    if(!$date_at) return array(null, null);

    $pagelog = new PageChangeLog($id);
    $rev_t = $pagelog->getLastRevisionAt($date_at);
    if($rev_t === '') { //current revision
        return array(null, null);
    } else if($rev_t === false) { //page did not exist
        $rev_n = $pagelog->getRelativeRevision($date_at, +1);
        msg(sprintf($lang['page_nonexist_rev'],
            strftime($conf['dformat'], $date_at),
            wl($id, array('rev' => $rev_n)),
            strftime($conf['dformat'], $rev_n)));
        return array($date_at, null); //will result in a page not exists message
    }

    return array($rev_t, $date_at);
}

if(!defined('DOKU_INC')) define('DOKU_INC', dirname(__FILE__).'/');

// define all DokuWiki globals here (needed within test requests but also helps to keep track)
global  $ACT,  $INPUT, $QUERY, $ID, $REV, $DATE_AT, $IDX,
        $DATE, $RANGE, $HIGH, $TEXT, $PRE, $SUF, $SUM, $INFO, $JSINFO;

$ACT = doku_get_requested_action();

// load and initialize the core system
require_once(DOKU_INC.'inc/init.php');

//import variables
$INPUT->set('id', str_replace("\xC2\xAD", '', $INPUT->str('id'))); //soft-hyphen
$QUERY          = trim($INPUT->str('q'));
$ID             = getID();

$REV   = $INPUT->int('rev');
$DATE_AT = $INPUT->str('at');
$IDX   = $INPUT->str('idx');
$DATE  = $INPUT->int('date');
$RANGE = $INPUT->str('range');
$HIGH  = $INPUT->param('s');
if(empty($HIGH)) $HIGH = getGoogleQuery();

if($INPUT->post->has('wikitext')) {
    $TEXT = cleanText($INPUT->post->str('wikitext'));
}
$PRE = cleanText(substr($INPUT->post->str('prefix'), 0, -1));
$SUF = cleanText($INPUT->post->str('suffix'));
$SUM = $INPUT->post->str('summary');


//parse DATE_AT
$DATE_AT = doku_parse_date_at($DATE_AT);

//check for existing $REV related to $DATE_AT
if($DATE_AT) {
    list($REV, $DATE_AT) = doku_resolve_revision_for_date($ID, $DATE_AT);
}

//make infos about the selected page available
$INFO = pageinfo();

// handle debugging
if($conf['allowdebug'] && $ACT == 'debug') {
    html_debug();
    exit;
}

//send 404 for missing pages if configured or ID has special meaning to bots
if(!$INFO['exists'] &&
    ($conf['send404'] || preg_match('/^(robots\.txt|sitemap\.xml(\.gz)?|favicon\.ico|crossdomain\.xml)$/', $ID)) &&
    ($ACT == 'show' || (!is_array($ACT) && substr($ACT, 0, 7) == 'export_'))
) {
    header('HTTP/1.0 404 Not Found');
}

//prepare breadcrumbs (initialize a static var)
if($conf['breadcrumbs']) breadcrumbs();

// check upstream
checkUpdateMessages();

$tmp = array(); // No event data
trigger_event('DOKUWIKI_STARTED', $tmp);

//close session
session_write_close();

//do the work (picks up what to do from global env)
act_dispatch();

$tmp = array(); // No event data
trigger_event('DOKUWIKI_DONE', $tmp);

//  xdebug_dump_function_profile(1);
