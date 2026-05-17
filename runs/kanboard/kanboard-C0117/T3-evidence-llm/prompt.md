You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: kanboard-C0117
- Project: kanboard
- File: app/Template/dashboard/layout.php
- Lines: 1-29
- Candidate type: mixed_php_html
- Oracle IDs: kanboard_dashboard_auth_http

Evidence schema:
```json
{
  "candidate_id": "kanboard-C0117",
  "subject_id": "kanboard",
  "file": "app/Template/dashboard/layout.php",
  "lines": [
    1,
    29
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
      "value": 25
    }
  ],
  "dependencies": {
    "request_parameters": [],
    "session_keys": [],
    "database_tables": []
  },
  "web_contracts": {
    "dom_selectors": [
      "#dashboard",
      "#main",
      ".page-header",
      ".sidebar-container",
      ".sidebar-content"
    ],
    "forms": []
  },
  "protected_constraints": {
    "must_preserve_request_parameters": [],
    "must_preserve_session_keys": [],
    "must_preserve_database_tables": [],
    "must_preserve_dom_selectors": [
      "#dashboard",
      "#main",
      ".page-header",
      ".sidebar-container",
      ".sidebar-content"
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
<section id="main">
    <div class="page-header">
        <ul>
            <?php if ($this->user->hasAccess('ProjectCreationController', 'create')): ?>
                <li>
                    <?= $this->modal->medium('plus', t('New project'), 'ProjectCreationController', 'create') ?>
                </li>
            <?php endif ?>
            <?php if ($this->app->config('disable_private_project', 0) == 0): ?>
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
```
