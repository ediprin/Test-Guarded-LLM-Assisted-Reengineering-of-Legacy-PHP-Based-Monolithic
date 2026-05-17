function check_functions(){
    global $error;
    global $lang;
    $ok = true;

    if(version_compare(phpversion(),'5.6.0','<')){
        $error[] = sprintf($lang['i_phpver'],phpversion(),'5.6.0');
        $ok = false;
    }

    if(ini_get('mbstring.func_overload') != 0){
        $error[] = $lang['i_mbfuncoverload'];
        $ok = false;
    }

    $funcs = explode(' ','addslashes call_user_func chmod copy fgets '.
                         'file file_exists fseek flush filesize ftell fopen '.
                         'glob header ignore_user_abort ini_get mail mkdir '.
                         'ob_start opendir parse_ini_file readfile realpath '.
                         'rename rmdir serialize session_start unlink usleep '.
                         'preg_replace file_get_contents htmlspecialchars_decode '.
                         'spl_autoload_register stream_select fsockopen pack');

    if (!function_exists('mb_substr')) {
        $funcs[] = 'utf8_encode';
        $funcs[] = 'utf8_decode';
    }

    foreach($funcs as $func){
        if(!function_exists($func)){
            $error[] = sprintf($lang['i_funcna'],$func);
            $ok = false;
        }
    }
    return $ok;
}

/**
 * Print language selection
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 */
function langsel(){
