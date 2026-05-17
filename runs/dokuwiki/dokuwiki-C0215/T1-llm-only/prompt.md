You are assisting with bounded reengineering of a legacy PHP-based monolithic web application.

Task:
Improve maintainability of the selected PHP code region while preserving observable behavior.

Candidate:
- Candidate ID: dokuwiki-C0215
- Project: dokuwiki
- File: inc/template.php
- Lines: 1518-1561
- Candidate type: long_method_or_region

Rules:
- Return a unified diff only.
- Do not change public routes, request parameters, session keys, database table names, DOM selectors, or form field names.
- Do not migrate framework, architecture, database schema, or application structure.
- Keep the change local and bounded.

Code region:
```php
function tpl_license($img = 'badge', $imgonly = false, $return = false, $wrap = true) {
    global $license;
    global $conf;
    global $lang;
    if(!$conf['license']) return '';
    if(!is_array($license[$conf['license']])) return '';
    $lic    = $license[$conf['license']];
    $target = ($conf['target']['extern']) ? ' target="'.$conf['target']['extern'].'"' : '';

    $out = '';
    if($wrap) $out .= '<div class="license">';
    if($img) {
        $src = license_img($img);
        if($src) {
            $out .= '<a href="'.$lic['url'].'" rel="license"'.$target;
            $out .= '><img src="'.DOKU_BASE.$src.'" alt="'.$lic['name'].'" /></a>';
            if(!$imgonly) $out .= ' ';
        }
    }
    if(!$imgonly) {
        $out .= $lang['license'].' ';
        $out .= '<bdi><a href="'.$lic['url'].'" rel="license" class="urlextern"'.$target;
        $out .= '>'.$lic['name'].'</a></bdi>';
    }
    if($wrap) $out .= '</div>';

    if($return) return $out;
    echo $out;
    return '';
}

/**
 * Includes the rendered HTML of a given page
 *
 * This function is useful to populate sidebars or similar features in a
 * template
 *
 * @param string $pageid The page name you want to include
 * @param bool $print Should the content be printed or returned only
 * @param bool $propagate Search higher namespaces, too?
 * @param bool $useacl Include the page only if the ACLs check out?
 * @return bool|null|string
 */
function tpl_include_page($pageid, $print = true, $propagate = false, $useacl = true) {
```
