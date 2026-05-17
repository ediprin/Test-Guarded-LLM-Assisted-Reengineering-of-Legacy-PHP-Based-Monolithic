You are assisting with bounded reengineering of a legacy PHP-based monolithic web application.

Task:
Improve maintainability of the selected PHP code region while preserving observable behavior.

Candidate:
- Candidate ID: dokuwiki-C0205
- Project: dokuwiki
- File: inc/template.php
- Lines: 379-418
- Candidate type: long_method_or_region

Rules:
- Return a unified diff only.
- Do not change public routes, request parameters, session keys, database table names, DOM selectors, or form field names.
- Do not migrate framework, architecture, database schema, or application structure.
- Keep the change local and bounded.

Code region:
```php
function _tpl_metaheaders_action($data) {
    foreach($data as $tag => $inst) {
        if($tag == 'script') {
            echo "<!--[if gte IE 9]><!-->\n"; // no scripts for old IE
        }
        foreach($inst as $attr) {
            if ( empty($attr) ) { continue; }
            echo '<', $tag, ' ', buildAttributes($attr);
            if(isset($attr['_data']) || $tag == 'script') {
                if($tag == 'script' && $attr['_data'])
                    $attr['_data'] = "/*<![CDATA[*/".
                        $attr['_data'].
                        "\n/*!]]>*/";

                echo '>', $attr['_data'], '</', $tag, '>';
            } else {
                echo '/>';
            }
            echo "\n";
        }
        if($tag == 'script') {
            echo "<!--<![endif]-->\n";
        }
    }
}

/**
 * Print a link
 *
 * Just builds a link.
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 *
 * @param string $url
 * @param string $name
 * @param string $more
 * @param bool $return if true return the link html, otherwise print
 * @return bool|string html of the link, or true if printed
 */
function tpl_link($url, $name, $more = '', $return = false) {
```
