function print_retry() {
    global $lang;
    global $LC;
    ?>
    <form action="" method="get">
      <fieldset>
        <input type="hidden" name="l" value="<?php echo $LC ?>" />
        <button type="submit"><?php echo $lang['i_retry'];?></button>
      </fieldset>
    </form>
    <?php
}

/**
 * Check validity of data
 *
 * @author Andreas Gohr
 *
 * @param array $d
 * @return bool ok?
 */
function check_data(&$d){
