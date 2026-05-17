You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0006
- Project: dokuwiki
- File: install.php
- Lines: 146-233
- Candidate type: mixed_php_html
- Oracle IDs: dokuwiki_install_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0006",
  "subject_id": "dokuwiki",
  "file": "install.php",
  "lines": [
    146,
    233
  ],
  "candidate_type": "mixed_php_html",
  "issues": [
    {
      "type": "Mixed PHP/HTML",
      "evidence": "Detected by pre-treatment heuristic extractor; join with PHPMD/PHPStan logs for final static evidence."
    },
    {
      "type": "Complexity Proxy",
      "metric": "branch_keyword_count_plus_one",
      "value": 85
    }
  ],
  "dependencies": {
    "request_parameters": [],
    "session_keys": [],
    "database_tables": []
  },
  "web_contracts": {
    "dom_selectors": [
      "#acl",
      "#acldep",
      "#allowreg",
      "#confirm",
      "#email",
      "#fullname",
      "#lic_",
      "#password",
      "#policy",
      "#pop",
      "#process",
      "#superuser",
      "#title",
      ".text"
    ],
    "forms": []
  },
  "protected_constraints": {
    "must_preserve_request_parameters": [],
    "must_preserve_session_keys": [],
    "must_preserve_database_tables": [],
    "must_preserve_dom_selectors": [
      "#acl",
      "#acldep",
      "#allowreg",
      "#confirm",
      "#email",
      "#fullname",
      "#lic_",
      "#password",
      "#policy",
      "#pop",
      "#process",
      "#superuser",
      "#title",
      ".text"
    ],
    "must_preserve_forms": []
  },
  "allowed_transformations": [
    "Separate PHP Logic from Markup",
    "Extract View Helper"
  ],
  "test_support": {
    "existing_tests": null,
    "characterization_tests": null,
    "oracle_status": "pending"
  }
}
```

Constraints:
- Preserve all request parameters, session keys, database tables, forms, DOM selectors, and route behavior listed in the evidence.
- Use only allowed transformations from the evidence.
- Do not introduce new dependencies.
- Do not perform framework migration, database migration, or rewrite.
- Return a unified diff only.

Code region:
```php
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
```
