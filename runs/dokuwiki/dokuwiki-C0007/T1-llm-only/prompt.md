You are assisting with bounded reengineering of a legacy PHP-based monolithic web application.

Task:
Improve maintainability of the selected PHP code region while preserving observable behavior.

Candidate:
- Candidate ID: dokuwiki-C0007
- Project: dokuwiki
- File: install.php
- Lines: 233-254
- Candidate type: mixed_php_html

Rules:
- Return a unified diff only.
- Do not change public routes, request parameters, session keys, database table names, DOM selectors, or form field names.
- Do not migrate framework, architecture, database schema, or application structure.
- Keep the change local and bounded.

Code region:
```php
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
```
