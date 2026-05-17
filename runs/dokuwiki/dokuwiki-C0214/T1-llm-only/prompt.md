You are assisting with bounded reengineering of a legacy PHP-based monolithic web application.

Task:
Improve maintainability of the selected PHP code region while preserving observable behavior.

Candidate:
- Candidate ID: dokuwiki-C0214
- Project: dokuwiki
- File: inc/template.php
- Lines: 1420-1484
- Candidate type: long_method_or_region

Rules:
- Return a unified diff only.
- Do not change public routes, request parameters, session keys, database table names, DOM selectors, or form field names.
- Do not migrate framework, architecture, database schema, or application structure.
- Keep the change local and bounded.

Code region:
```php
function tpl_mediaFileDetails($image, $rev) {
    global $conf, $DEL, $lang;
    /** @var Input $INPUT */
    global $INPUT;

    $removed = (!file_exists(mediaFN($image)) && file_exists(mediaMetaFN($image, '.changes')) && $conf['mediarevisions']);
    if(!$image || (!file_exists(mediaFN($image)) && !$removed) || $DEL) return;
    if($rev && !file_exists(mediaFN($image, $rev))) $rev = false;
    $ns = getNS($image);
    $do = $INPUT->str('mediado');

    $opened_tab = $INPUT->str('tab_details');

    $tab_array = array('view');
    list(, $mime) = mimetype($image);
    if($mime == 'image/jpeg') {
        $tab_array[] = 'edit';
    }
    if($conf['mediarevisions']) {
        $tab_array[] = 'history';
    }

    if(!$opened_tab || !in_array($opened_tab, $tab_array)) $opened_tab = 'view';
    if($INPUT->bool('edit')) $opened_tab = 'edit';
    if($do == 'restore') $opened_tab = 'view';

    media_tabs_details($image, $opened_tab);

    echo '<div class="panelHeader"><h3>';
    list($ext) = mimetype($image, false);
    $class    = preg_replace('/[^_\-a-z0-9]+/i', '_', $ext);
    $class    = 'select mediafile mf_'.$class;
    $attributes = $rev ? ['rev' => $rev] : [];
    $tabTitle = '<strong><a href="'.ml($image, $attributes).'" class="'.$class.'" title="'.$lang['mediaview'].'">'.$image.'</a>'.'</strong>';
    if($opened_tab === 'view' && $rev) {
        printf($lang['media_viewold'], $tabTitle, dformat($rev));
    } else {
        printf($lang['media_'.$opened_tab], $tabTitle);
    }

    echo '</h3></div>'.NL;

    echo '<div class="panelContent">'.NL;

    if($opened_tab == 'view') {
        media_tab_view($image, $ns, null, $rev);

    } elseif($opened_tab == 'edit' && !$removed) {
        media_tab_edit($image, $ns);

    } elseif($opened_tab == 'history' && $conf['mediarevisions']) {
        media_tab_history($image, $ns);
    }

    echo '</div>'.NL;
}

/**
 * prints the namespace tree in the mediamanager popup
 *
 * Only allowed in mediamanager.php
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 */
function tpl_mediaTree() {
```
