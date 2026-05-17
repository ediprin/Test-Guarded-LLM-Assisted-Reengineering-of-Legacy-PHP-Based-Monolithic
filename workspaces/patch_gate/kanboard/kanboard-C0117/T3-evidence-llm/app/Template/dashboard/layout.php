<?php
$can_create_project = $this->user->hasAccess('ProjectCreationController', 'create');
$show_private_project = $this->app->config('disable_private_project', 0) == 0;
?>
<section id="main">
    <div class="page-header">
        <ul>
            <?php if ($can_create_project): ?>
                <li>
                    <?= $this->modal->medium('plus', t('New project'), 'ProjectCreationController', 'create') ?>
                </li>
            <?php endif ?>
            <?php if ($show_private_project): ?>
                <li>
                    <?= $this->modal->medium('lock', t('New private project'), 'ProjectCreationController', 'createPrivate') ?>
                </li>
            <?php endif ?>
            <li>
                <?= $this->url->icon('folder', t('Project management'), 'ProjectListController', 'show') ?>
            </li>
            <li>
                <?= $this->modal->medium('dashboard', t('My activity stream'), 'ActivityController', 'user') ?>
            </li>
            <?= $this->hook->render('template:dashboard:page-header:menu', array('user' => $user)) ?>
        </ul>
    </div>
    <section class="sidebar-container" id="dashboard">
        <?= $this->render($sidebar_template, array('user' => $user)) ?>
        <div class="sidebar-content">
            <?= $content_for_sublayout ?>
        </div>
    </section>
</section>
