You are assisting with bounded reengineering of a legacy PHP-based monolithic web application.

Task:
Improve maintainability of the selected PHP code region while preserving observable behavior.

Candidate:
- Candidate ID: dokuwiki-C0208
- Project: dokuwiki
- File: inc/template.php
- Lines: 721-769
- Candidate type: long_method_or_region

Rules:
- Return a unified diff only.
- Do not change public routes, request parameters, session keys, database table names, DOM selectors, or form field names.
- Do not migrate framework, architecture, database schema, or application structure.
- Keep the change local and bounded.

Code region:
```php
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
```
