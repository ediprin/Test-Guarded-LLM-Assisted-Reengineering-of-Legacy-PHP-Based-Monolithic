You are assisting with bounded reengineering of a legacy PHP-based monolithic web application.

Task:
Improve maintainability of the selected PHP code region while preserving observable behavior.

Candidate:
- Candidate ID: kanboard-C0121
- Project: kanboard
- File: app/Template/dashboard/tasks.php
- Lines: 1-41
- Candidate type: mixed_php_html

Rules:
- Return a unified diff only.
- Do not change public routes, request parameters, session keys, database table names, DOM selectors, or form field names.
- Do not migrate framework, architecture, database schema, or application structure.
- Keep the change local and bounded.

Code region:
```php
<div class="page-header">
    <h2><?= $this->url->link(t('My tasks'), 'DashboardController', 'tasks', array('user_id' => $user['id'])) ?> (<?= $paginator->getTotal() ?>)</h2>
</div>
<?php if ($paginator->isEmpty()): ?>
    <p class="alert"><?= t('There is nothing assigned to you.') ?></p>
<?php else: ?>
    <div class="table-list">
        <?= $this->render('task_list/header', array(
            'paginator' => $paginator,
        )) ?>

        <?php foreach ($paginator->getCollection() as $task): ?>
            <div class="table-list-row color-<?= $task['color_id'] ?>">
                <?= $this->render('task_list/task_title', array(
                    'task' => $task,
                    'redirect' => 'dashboard-tasks',
                )) ?>

                <?= $this->render('task_list/task_details', array(
                    'task' => $task,
                )) ?>

                <?= $this->render('task_list/task_avatars', array(
                    'task' => $task,
                )) ?>

                <?= $this->render('task_list/task_icons', array(
                    'task' => $task,
                )) ?>

                <?= $this->render('task_list/task_subtasks', array(
                    'task' => $task,
                )) ?>

                <?= $this->hook->render('template:dashboard:task:footer', array('task' => $task)) ?>
            </div>
        <?php endforeach ?>
    </div>

    <?= $paginator ?>
<?php endif ?>
```
