function html_softbreak_callback($match){
    // if match is an html tag, return it intact
    if ($match[0]{0} == '<') return $match[0];

    // its a long string without a breaking character,
    // make certain characters into breaking characters by inserting a
    // breaking character (zero length space, U+200B / #8203) in front them.
    $regex = <<< REGEX
(?(?=                                 # start a conditional expression with a positive look ahead ...
&\#?\\w{1,6};)                        # ... for html entities - we don't want to split them (ok to catch some invalid combinations)
&\#?\\w{1,6};                         # yes pattern - a quicker match for the html entity, since we know we have one
|
[?/,&\#;:]                            # no pattern - any other group of 'special' characters to insert a breaking character after
)+                                    # end conditional expression
REGEX;

    return preg_replace('<'.$regex.'>xu','\0&#8203;',$match[0]);
}

/**
 * show warning on conflict detection
 *
 * @author Andreas Gohr <andi@splitbrain.org>
 *
 * @param string $text
 * @param string $summary
 */
function html_conflict($text,$summary){
