You are assisting with bounded reengineering of a legacy PHP-based monolithic web application.

Task:
Improve maintainability of the selected PHP code region while preserving observable behavior.

Candidate:
- Candidate ID: kanboard-C0119
- Project: kanboard
- File: app/Template/dashboard/projects.php
- Lines: 1-27
- Candidate type: mixed_php_html

Rules:
- Return a unified diff only.
- Do not change public routes, request parameters, session keys, database table names, DOM selectors, or form field names.
- Do not migrate framework, architecture, database schema, or application structure.
- Keep the change local and bounded.

Code region:
```php
<div class="page-header">
    <h2><?= $this->url->link(t('My projects'), 'DashboardController', 'projects', array('user_id' => $user['id'])) ?> (<?= $paginator->getTotal() ?>)</h2>
</div>
<?php if ($paginator->isEmpty()): ?>
    <p class="alert"><?= t('Your are not member of any project.') ?></p>
<?php else: ?>
    <div class="table-list">
        <?= $this->render('project_list/header', array('paginator' => $paginator)) ?>
        <?php foreach ($paginator->getCollection() as $project): ?>
            <div class="table-list-row table-border-left">
                <?= $this->render('project_list/project_title', array(
                    'project' => $project,
                )) ?>

                <?= $this->render('project_list/project_details', array(
                    'project' => $project,
                )) ?>

                <?= $this->render('project_list/project_icons', array(
                    'project' => $project,
                )) ?>
            </div>
        <?php endforeach ?>
    </div>

    <?= $paginator ?>
<?php endif ?>
```
