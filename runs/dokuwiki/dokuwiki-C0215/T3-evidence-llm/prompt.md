You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0215
- Project: dokuwiki
- File: inc/template.php
- Lines: 1518-1561
- Candidate type: long_method_or_region
- Oracle IDs: dokuwiki_home_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0215",
  "subject_id": "dokuwiki",
  "file": "inc/template.php",
  "lines": [
    1518,
    1561
  ],
  "candidate_type": "long_method_or_region",
  "issues": [
    {
      "type": "Long or Complex Region",
      "evidence": "Detected by pre-treatment heuristic extractor; join with PHPMD/PHPStan logs for final static evidence."
    },
    {
      "type": "Complexity Proxy",
      "metric": "branch_keyword_count_plus_one",
      "value": 14
    }
  ],
  "dependencies": {
    "request_parameters": [],
    "session_keys": [],
    "database_tables": []
  },
  "web_contracts": {
    "dom_selectors": [
      ".license",
      ".urlextern"
    ],
    "forms": []
  },
  "protected_constraints": {
    "must_preserve_request_parameters": [],
    "must_preserve_session_keys": [],
    "must_preserve_database_tables": [],
    "must_preserve_dom_selectors": [
      ".license",
      ".urlextern"
    ],
    "must_preserve_forms": []
  },
  "allowed_transformations": [
    "Extract Method"
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
