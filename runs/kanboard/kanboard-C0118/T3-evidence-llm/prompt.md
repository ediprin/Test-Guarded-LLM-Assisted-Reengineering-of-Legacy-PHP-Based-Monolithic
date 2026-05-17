You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: kanboard-C0118
- Project: kanboard
- File: app/Template/dashboard/overview.php
- Lines: 1-96
- Candidate type: mixed_php_html
- Oracle IDs: kanboard_dashboard_auth_http

Evidence schema:
```json
{
  "candidate_id": "kanboard-C0118",
  "subject_id": "kanboard",
  "file": "app/Template/dashboard/overview.php",
  "lines": [
    1,
    96
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
      "value": 107
    }
  ],
  "dependencies": {
    "request_parameters": [],
    "session_keys": [],
    "database_tables": []
  },
  "web_contracts": {
    "dom_selectors": [
      "#project-tasks-<?= $result[",
      ".$project[",
      ".$task[",
      ".<?=",
      ".alert",
      ".color-<?=",
      ".fa",
      ".fa-fw",
      ".fa-lock",
      ".filter-box",
      ".input-addon",
      ".input-addon-item",
      ".margin-bottom",
      ".page-header",
      ".search",
      ".table-border-left",
      ".table-list",
      ".table-list-details",
      ".table-list-row",
      ".table-list-title"
    ],
    "forms": [
      "<?= $this->url->dir() ?>"
    ]
  },
  "protected_constraints": {
    "must_preserve_request_parameters": [],
    "must_preserve_session_keys": [],
    "must_preserve_database_tables": [],
    "must_preserve_dom_selectors": [
      "#project-tasks-<?= $result[",
      ".$project[",
      ".$task[",
      ".<?=",
      ".alert",
      ".color-<?=",
      ".fa",
      ".fa-fw",
      ".fa-lock",
      ".filter-box",
      ".input-addon",
      ".input-addon-item",
      ".margin-bottom",
      ".page-header",
      ".search",
      ".table-border-left",
      ".table-list",
      ".table-list-details",
      ".table-list-row",
      ".table-list-title"
    ],
    "must_preserve_forms": [
      "<?= $this->url->dir() ?>"
    ]
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
<div class="filter-box margin-bottom">
    <form method="get" action="<?= $this->url->dir() ?>" class="search">
        <?= $this->form->hidden('controller', array('controller' => 'SearchController')) ?>
        <?= $this->form->hidden('action', array('action' => 'index')) ?>

        <div class="input-addon">
            <?= $this->form->text('search', array(), array(), array('placeholder="'.t('Search').'"'), 'input-addon-field') ?>
            <div class="input-addon-item">
                <?= $this->render('app/filters_helper') ?>
            </div>
        </div>
    </form>
</div>

<?php if (! $project_paginator->isEmpty()): ?>
    <div class="table-list">
        <?= $this->render('project_list/header', array('paginator' => $project_paginator)) ?>
        <?php foreach ($project_paginator->getCollection() as $project): ?>
            <div class="table-list-row table-border-left">
                <div>
                    <?php if ($this->user->hasProjectAccess('ProjectViewController', 'show', $project['id'])): ?>
                        <?= $this->render('project/dropdown', array('project' => $project)) ?>
                    <?php else: ?>
                        <strong><?= '#'.$project['id'] ?></strong>
                    <?php endif ?>

                    <span class="table-list-title <?= $project['is_active'] == 0 ? 'status-closed' : '' ?>">
                        <?= $this->url->link($this->text->e($project['name']), 'BoardViewController', 'show', array('project_id' => $project['id'])) ?>
                    </span>

                    <?php if ($project['is_private']): ?>
                        <i class="fa fa-lock fa-fw" title="<?= t('Private project') ?>"></i>
                    <?php endif ?>
                </div>
                <div class="table-list-details">
                    <?php foreach ($project['columns'] as $column): ?>
                        <strong title="<?= t('Task count') ?>"><?= $column['nb_open_tasks'] ?></strong>
                        <small><?= $this->text->e($column['title']) ?></small>
                    <?php endforeach ?>
                </div>
            </div>
        <?php endforeach ?>
    </div>

    <?= $project_paginator ?>
<?php endif ?>

<?php if (empty($overview_paginator)): ?>
    <p class="alert"><?= t('There is nothing assigned to you.') ?></p>
<?php else: ?>
    <?php foreach ($overview_paginator as $result): ?>
        <?php if (! $result['paginator']->isEmpty()): ?>
            <div class="page-header">
                <h2 id="project-tasks-<?= $result['project_id'] ?>"><?= $this->url->link($this->text->e($result['project_name']), 'BoardViewController', 'show', array('project_id' => $result['project_id'])) ?></h2>
            </div>

            <div class="table-list">
                <?= $this->render('task_list/header', array(
                    'paginator' => $result['paginator'],
                )) ?>

                <?php foreach ($result['paginator']->getCollection() as $task): ?>
                    <div class="table-list-row color-<?= $task['color_id'] ?>">
                        <?= $this->render('task_list/task_title', array(
                            'task' => $task,
                            'redirect' => 'dashboard',
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
                            'task'    => $task,
                            'user_id' => $user['id'],
                        )) ?>

                        <?= $this->hook->render('template:dashboard:task:footer', array('task' => $task)) ?>
                    </div>
                <?php endforeach ?>
            </div>

            <?= $result['paginator'] ?>
        <?php endif ?>
    <?php endforeach ?>
<?php endif ?>

<?= $this->hook->render('template:dashboard:show', array('user' => $user)) ?>
```
