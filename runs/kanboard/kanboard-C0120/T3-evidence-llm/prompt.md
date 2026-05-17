You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: kanboard-C0120
- Project: kanboard
- File: app/Template/dashboard/subtasks.php
- Lines: 1-49
- Candidate type: mixed_php_html
- Oracle IDs: kanboard_dashboard_auth_http

Evidence schema:
```json
{
  "candidate_id": "kanboard-C0120",
  "subject_id": "kanboard",
  "file": "app/Template/dashboard/subtasks.php",
  "lines": [
    1,
    49
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
      "value": 46
    }
  ],
  "dependencies": {
    "request_parameters": [],
    "session_keys": [],
    "database_tables": []
  },
  "web_contracts": {
    "dom_selectors": [
      ".$task[",
      ".alert",
      ".color-<?=",
      ".dropdown",
      ".dropdown-menu",
      ".dropdown-menu-link-icon",
      ".fa",
      ".fa-caret-down",
      ".page-header",
      ".table-list",
      ".table-list-header",
      ".table-list-header-count",
      ".table-list-header-menu",
      ".table-list-row"
    ],
    "forms": []
  },
  "protected_constraints": {
    "must_preserve_request_parameters": [],
    "must_preserve_session_keys": [],
    "must_preserve_database_tables": [],
    "must_preserve_dom_selectors": [
      ".$task[",
      ".alert",
      ".color-<?=",
      ".dropdown",
      ".dropdown-menu",
      ".dropdown-menu-link-icon",
      ".fa",
      ".fa-caret-down",
      ".page-header",
      ".table-list",
      ".table-list-header",
      ".table-list-header-count",
      ".table-list-header-menu",
      ".table-list-row"
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
