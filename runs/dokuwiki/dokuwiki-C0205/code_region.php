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
