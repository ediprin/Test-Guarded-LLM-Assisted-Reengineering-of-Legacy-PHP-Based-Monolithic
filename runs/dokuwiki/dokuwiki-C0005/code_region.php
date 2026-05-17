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
