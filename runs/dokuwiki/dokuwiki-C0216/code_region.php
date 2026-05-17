function tpl_getMediaFile($search, $abs = false, &$imginfo = null) {
    $img     = '';
    $file    = '';
    $ismedia = false;
    // loop through candidates until a match was found:
    foreach($search as $img) {
        if(substr($img, 0, 1) == ':') {
            $file    = mediaFN($img);
            $ismedia = true;
        } else {
            $file    = tpl_incdir().$img;
            $ismedia = false;
        }

        if(file_exists($file)) break;
    }

    // fetch image data if requested
    if(!is_null($imginfo)) {
        $imginfo = getimagesize($file);
    }

    // build URL
    if($ismedia) {
        $url = ml($img, '', true, '', $abs);
    } else {
        $url = tpl_basedir().$img;
        if($abs) $url = DOKU_URL.substr($url, strlen(DOKU_REL));
    }

    return $url;
}

/**
 * PHP include a file
 *
 * either from the conf directory if it exists, otherwise use
 * file in the template's root directory.
 *
 * The function honours config cascade settings and looks for the given
 * file next to the ´main´ config files, in the order protected, local,
 * default.
 *
 * Note: no escaping or sanity checking is done here. Never pass user input
 * to this function!
 *
 * @author Anika Henke <anika@selfthinker.org>
 * @author Andreas Gohr <andi@splitbrain.org>
 *
 * @param string $file
 */
function tpl_includeFile($file) {
