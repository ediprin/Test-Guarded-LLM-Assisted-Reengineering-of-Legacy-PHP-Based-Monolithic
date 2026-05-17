You are assisting with bounded reengineering of a legacy PHP-based monolithic web application.

Task:
Improve maintainability of the selected PHP code region while preserving observable behavior.

Candidate:
- Candidate ID: kanboard-C0120
- Project: kanboard
- File: app/Template/dashboard/subtasks.php
- Lines: 1-49
- Candidate type: mixed_php_html

Rules:
- Return a unified diff only.
- Do not change public routes, request parameters, session keys, database table names, DOM selectors, or form field names.
- Do not migrate framework, architecture, database schema, or application structure.
- Keep the change local and bounded.

Code region:
```php
<div class="page-header">
    <h2><?= $this->url->link(t('My subtasks'), 'DashboardController', 'subtasks', array('user_id' => $user['id'])) ?> (<?= $nb_subtasks ?>)</h2>
</div>
<?php if ($nb_subtasks == 0): ?>
    <p class="alert"><?= t('There is nothing assigned to you.') ?></p>
<?php else: ?>
    <div class="table-list">
        <div class="table-list-header">
            <div class="table-list-header-count">
                <?php if ($nb_subtasks > 1): ?>
                    <?= t('%d subtasks', $nb_subtasks) ?>
                <?php else: ?>
                    <?= t('%d subtask', $nb_subtasks) ?>
                <?php endif ?>
            </div>
            <div class="table-list-header-menu">
                <div class="dropdown">
                    <a href="#" class="dropdown-menu dropdown-menu-link-icon"><strong><?= t('Sort') ?> <i class="fa fa-caret-down"></i></strong></a>
                    <ul>
                        <li>
                            <?= $paginator->order(t('Task ID'), \Kanboard\Model\TaskModel::TABLE.'.id') ?>
                        </li>
                        <li>
                            <?= $paginator->order(t('Title'), \Kanboard\Model\TaskModel::TABLE.'.title') ?>
                        </li>
                        <li>
                            <?= $paginator->order(t('Priority'), \Kanboard\Model\TaskModel::TABLE.'.priority') ?>
                        </li>
                    </ul>
                </div>
            </div>
        </div>

        <?php foreach ($paginator->getCollection() as $task): ?>
            <div class="table-list-row color-<?= $task['color_id'] ?>">
                <?= $this->render('task_list/task_title', array(
                    'task' => $task,
                )) ?>

                <?= $this->render('task_list/task_subtasks', array(
                    'task' => $task,
                    'user_id' => $user['id'],
                )) ?>
            </div>
        <?php endforeach ?>
    </div>

    <?= $paginator ?>
<?php endif ?>
```
