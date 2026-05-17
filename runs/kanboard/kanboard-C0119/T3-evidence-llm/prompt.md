You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: kanboard-C0119
- Project: kanboard
- File: app/Template/dashboard/projects.php
- Lines: 1-27
- Candidate type: mixed_php_html
- Oracle IDs: kanboard_dashboard_auth_http

Evidence schema:
```json
{
  "candidate_id": "kanboard-C0119",
  "subject_id": "kanboard",
  "file": "app/Template/dashboard/projects.php",
  "lines": [
    1,
    27
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
      "value": 29
    }
  ],
  "dependencies": {
    "request_parameters": [],
    "session_keys": [],
    "database_tables": []
  },
  "web_contracts": {
    "dom_selectors": [
      ".alert",
      ".page-header",
      ".table-border-left",
      ".table-list",
      ".table-list-row"
    ],
    "forms": []
  },
  "protected_constraints": {
    "must_preserve_request_parameters": [],
    "must_preserve_session_keys": [],
    "must_preserve_database_tables": [],
    "must_preserve_dom_selectors": [
      ".alert",
      ".page-header",
      ".table-border-left",
      ".table-list",
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
