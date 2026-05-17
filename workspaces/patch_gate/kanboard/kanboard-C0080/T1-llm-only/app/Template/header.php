<?php
    $title_template_data = array(
        'project' => isset($project) ? $project : null,
        'task' => isset($task) ? $task : null,
        'description' => isset($description) ? $description : null,
        'title' => $title,
    );

    $_title = $this->render('header/title', $title_template_data);

    $top_right_corner_items = array(
        $this->render('header/user_notifications'),
        $this->render('header/creation_dropdown'),
        $this->render('header/user_dropdown'),
    );

    $_top_right_corner = implode('&nbsp;', $top_right_corner_items);
?>

<header>
    <div class="title-container">
        <?= $_title ?>
    </div>
    <div class="board-selector-container">
        <?php if (! empty($board_selector)): ?>
            <?= $this->render('header/board_selector', array('board_selector' => $board_selector)) ?>
        <?php endif ?>
    </div>
    <div class="menus-container">
        <?= $_top_right_corner ?>
    </div>
</header>
