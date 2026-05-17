You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: dokuwiki-C0005
- Project: dokuwiki
- File: install.php
- Lines: 60-146
- Candidate type: form_handling
- Oracle IDs: dokuwiki_install_http

Evidence schema:
```json
{
  "candidate_id": "dokuwiki-C0005",
  "subject_id": "dokuwiki",
  "file": "install.php",
  "lines": [
    60,
    146
  ],
  "candidate_type": "form_handling",
  "issues": [
    {
      "type": "Request Handling Mixed With Rendering",
      "evidence": "Detected by pre-treatment heuristic extractor; join with PHPMD/PHPStan logs for final static evidence."
    },
    {
      "type": "Complexity Proxy",
      "metric": "branch_keyword_count_plus_one",
      "value": 21
    }
  ],
  "dependencies": {
    "request_parameters": [
      "d"
    ],
    "session_keys": [],
    "database_tables": []
  },
  "web_contracts": {
    "dom_selectors": [
      ".cl"
    ],
    "forms": []
  },
  "protected_constraints": {
    "must_preserve_request_parameters": [
      "d"
    ],
    "must_preserve_session_keys": [],
    "must_preserve_database_tables": [],
    "must_preserve_dom_selectors": [
      ".cl"
    ],
    "must_preserve_forms": []
  },
  "allowed_transformations": [
    "Extract Validation Helper",
    "Extract Method",
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
        function acltoggle(){
            var cb = document.getElementById('acl');
            var fs = document.getElementById('acldep');
            if(!cb || !fs) return;
            if(cb.checked){
                fs.style.display = '';
            }else{
                fs.style.display = 'none';
            }
        }
        window.onload = function(){
            acltoggle();
            var cb = document.getElementById('acl');
            if(cb) cb.onchange = acltoggle;
        };
    </script>
</head>
<body style="">
    <h1 style="float:left">
        <img src="lib/exe/fetch.php?media=wiki:dokuwiki-128.png"
             style="vertical-align: middle;" alt="" height="64" width="64" />
        <?php echo $lang['i_installer']?>
    </h1>
    <div style="float:right; margin: 1em;">
        <?php langsel()?>
    </div>
    <br class="cl" />

    <div style="float: right; width: 34%;">
        <?php
            if(file_exists(DOKU_INC.'inc/lang/'.$LC.'/install.html')){
                include(DOKU_INC.'inc/lang/'.$LC.'/install.html');
            }else{
                print "<div lang=\"en\" dir=\"ltr\">\n";
                include(DOKU_INC.'inc/lang/en/install.html');
                print "</div>\n";
            }
        ?>
        <a style="background: transparent url(data/dont-panic-if-you-see-this-in-your-logs-it-means-your-directory-permissions-are-correct.png) left top no-repeat;
                  display: block; width:380px; height:73px; border:none; clear:both;"
           target="_blank"
           href="http://www.dokuwiki.org/security#web_access_security"></a>
    </div>

    <div style="float: left; width: 58%;">
        <?php
            try {
                if(! (check_functions() && check_permissions()) ){
                    echo '<p>'.$lang['i_problems'].'</p>';
                    print_errors();
                    print_retry();
                }elseif(!check_configs()){
                    echo '<p>'.$lang['i_modified'].'</p>';
                    print_errors();
                }elseif(check_data($_REQUEST['d'])){
                    // check_data has sanitized all input parameters
                    if(!store_data($_REQUEST['d'])){
                        echo '<p>'.$lang['i_failure'].'</p>';
                        print_errors();
                    }else{
                        echo '<p>'.$lang['i_success'].'</p>';
                    }
                }else{
                    print_errors();
                    print_form($_REQUEST['d']);
                }
            } catch (Exception $e) {
                echo 'Caught exception: ',  $e->getMessage(), "\n";
            }
        ?>
    </div>


<div style="clear: both">
  <a href="http://dokuwiki.org/"><img src="lib/tpl/dokuwiki/images/button-dw.png" alt="driven by DokuWiki" /></a>
  <a href="http://php.net"><img src="lib/tpl/dokuwiki/images/button-php.gif" alt="powered by PHP" /></a>
</div>
</body>
</html>
<?php

/**
 * Print the input form
 *
 * @param array $d submitted entry 'd' of request data
 */
function print_form($d){
```
