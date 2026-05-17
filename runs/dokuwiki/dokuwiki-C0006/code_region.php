function print_form($d){
    global $lang;
    global $LC;

    include(DOKU_CONF.'license.php');

    if(!is_array($d)) $d = array();
    $d = array_map('hsc',$d);

    if(!isset($d['acl'])) $d['acl']=1;
    if(!isset($d['pop'])) $d['pop']=1;

    ?>
    <form action="" method="post">
    <input type="hidden" name="l" value="<?php echo $LC ?>" />
    <fieldset>
        <label for="title"><?php echo $lang['i_wikiname']?>
        <input type="text" name="d[title]" id="title" value="<?php echo $d['title'] ?>" style="width: 20em;" />
        </label>

        <fieldset style="margin-top: 1em;">
            <label for="acl">
            <input type="checkbox" name="d[acl]" id="acl" <?php echo(($d['acl'] ? ' checked="checked"' : ''));?> />
            <?php echo $lang['i_enableacl']?></label>

            <fieldset id="acldep">
                <label for="superuser"><?php echo $lang['i_superuser']?></label>
                <input class="text" type="text" name="d[superuser]" id="superuser" value="<?php echo $d['superuser'] ?>" />

                <label for="fullname"><?php echo $lang['fullname']?></label>
                <input class="text" type="text" name="d[fullname]" id="fullname" value="<?php echo $d['fullname'] ?>" />

                <label for="email"><?php echo $lang['email']?></label>
                <input class="text" type="text" name="d[email]" id="email" value="<?php echo $d['email'] ?>" />

                <label for="password"><?php echo $lang['pass']?></label>
                <input class="text" type="password" name="d[password]" id="password" />

                <label for="confirm"><?php echo $lang['passchk']?></label>
                <input class="text" type="password" name="d[confirm]" id="confirm" />

                <label for="policy"><?php echo $lang['i_policy']?></label>
                <select class="text" name="d[policy]" id="policy">
                    <option value="0" <?php echo ($d['policy'] == 0)?'selected="selected"':'' ?>><?php echo $lang['i_pol0']?></option>
                    <option value="1" <?php echo ($d['policy'] == 1)?'selected="selected"':'' ?>><?php echo $lang['i_pol1']?></option>
                    <option value="2" <?php echo ($d['policy'] == 2)?'selected="selected"':'' ?>><?php echo $lang['i_pol2']?></option>
                </select>

                <label for="allowreg">
                    <input type="checkbox" name="d[allowreg]" id="allowreg" <?php echo(($d['allowreg'] ? ' checked="checked"' : ''));?> />
                    <?php echo $lang['i_allowreg']?>
                </label>
            </fieldset>
        </fieldset>

        <fieldset>
            <p><?php echo $lang['i_license']?></p>
            <?php
            array_push($license,array('name' => $lang['i_license_none'], 'url'=>''));
            if(empty($d['license'])) $d['license'] = 'cc-by-sa';
            foreach($license as $key => $lic){
                echo '<label for="lic_'.$key.'">';
                echo '<input type="radio" name="d[license]" value="'.hsc($key).'" id="lic_'.$key.'"'.
                     (($d['license'] === $key)?' checked="checked"':'').'>';
                echo hsc($lic['name']);
                if($lic['url']) echo ' <a href="'.$lic['url'].'" target="_blank"><sup>[?]</sup></a>';
                echo '</label>';
            }
            ?>
        </fieldset>

        <fieldset>
            <p><?php echo $lang['i_pop_field']?></p>
            <label for="pop">
                <input type="checkbox" name="d[pop]" id="pop" <?php echo(($d['pop'] ? ' checked="checked"' : ''));?> />
                <?php echo $lang['i_pop_label']?> <a href="http://www.dokuwiki.org/popularity" target="_blank"><sup>[?]</sup></a>
            </label>
        </fieldset>

    </fieldset>
    <fieldset id="process">
        <button type="submit" name="submit"><?php echo $lang['btn_save']?></button>
    </fieldset>
    </form>
    <?php
}

function print_retry() {
