You are assisting with bounded reengineering of a legacy PHP-based monolithic web application.

Task:
Improve maintainability of the selected PHP code region while preserving observable behavior.

Candidate:
- Candidate ID: dokuwiki-C0224
- Project: dokuwiki
- File: lib/exe/css.php
- Lines: 537-576
- Candidate type: long_method_or_region

Rules:
- Return a unified diff only.
- Do not change public routes, request parameters, session keys, database table names, DOM selectors, or form field names.
- Do not migrate framework, architecture, database schema, or application structure.
- Keep the change local and bounded.

Code region:
```php
function css_compress($css){
    //strip comments through a callback
    $css = preg_replace_callback('#(/\*)(.*?)(\*/)#s','css_comment_cb',$css);

    //strip (incorrect but common) one line comments
    $css = preg_replace_callback('/^.*\/\/.*$/m','css_onelinecomment_cb',$css);

    // strip whitespaces
    $css = preg_replace('![\r\n\t ]+!',' ',$css);
    $css = preg_replace('/ ?([;,{}\/]) ?/','\\1',$css);
    $css = preg_replace('/ ?: /',':',$css);

    // number compression
    $css = preg_replace('/([: ])0+(\.\d+?)0*((?:pt|pc|in|mm|cm|em|ex|px)\b|%)(?=[^\{]*[;\}])/', '$1$2$3', $css); // "0.1em" to ".1em", "1.10em" to "1.1em"
    $css = preg_replace('/([: ])\.(0)+((?:pt|pc|in|mm|cm|em|ex|px)\b|%)(?=[^\{]*[;\}])/', '$1$2', $css); // ".0em" to "0"
    $css = preg_replace('/([: ]0)0*(\.0*)?((?:pt|pc|in|mm|cm|em|ex|px)(?=[^\{]*[;\}])\b|%)/', '$1', $css); // "0.0em" to "0"
    $css = preg_replace('/([: ]\d+)(\.0*)((?:pt|pc|in|mm|cm|em|ex|px)(?=[^\{]*[;\}])\b|%)/', '$1$3', $css); // "1.0em" to "1em"
    $css = preg_replace('/([: ])0+(\d+|\d*\.\d+)((?:pt|pc|in|mm|cm|em|ex|px)(?=[^\{]*[;\}])\b|%)/', '$1$2$3', $css); // "001em" to "1em"

    // shorten attributes (1em 1em 1em 1em -> 1em)
    $css = preg_replace('/(?<![\w\-])((?:margin|padding|border|border-(?:width|radius)):)([\w\.]+)( \2)+(?=[;\}]| !)/', '$1$2', $css); // "1em 1em 1em 1em" to "1em"
    $css = preg_replace('/(?<![\w\-])((?:margin|padding|border|border-(?:width)):)([\w\.]+) ([\w\.]+) \2 \3(?=[;\}]| !)/', '$1$2 $3', $css); // "1em 2em 1em 2em" to "1em 2em"

    // shorten colors
    $css = preg_replace("/#([0-9a-fA-F]{1})\\1([0-9a-fA-F]{1})\\2([0-9a-fA-F]{1})\\3(?=[^\{]*[;\}])/", "#\\1\\2\\3", $css);

    return $css;
}

/**
 * Callback for css_compress()
 *
 * Keeps short comments (< 5 chars) to maintain typical browser hacks
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 *
 * @param array $matches
 * @return string
 */
function css_comment_cb($matches){
```
