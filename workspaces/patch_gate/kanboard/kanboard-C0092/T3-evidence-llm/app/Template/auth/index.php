<?php
$show_login_error = isset($errors['login']);
$show_login_form = ! HIDE_LOGIN_FORM;
$show_captcha = isset($captcha) && $captcha;
$show_remember_me = REMEMBER_ME_AUTH;
$show_password_reset = $this->app->config('password_reset') == 1;
?>
<div class="form-login">

    <?= $this->hook->render('template:auth:login-form:before') ?>

    <?php if ($show_login_error): ?>
        <p class="alert alert-error"><?= $this->text->e($errors['login']) ?></p>
    <?php endif ?>

    <?php if ($show_login_form): ?>
    <form method="post" action="<?= $this->url->href('AuthController', 'check') ?>">

        <?= $this->form->csrf() ?>

        <?= $this->form->label(t('Username'), 'username') ?>
        <?= $this->form->text('username', $values, $errors, array('autofocus', 'required')) ?>

        <?= $this->form->label(t('Password'), 'password') ?>
        <?= $this->form->password('password', $values, $errors, array('required')) ?>

        <?php if ($show_captcha): ?>
            <?= $this->form->label(t('Enter the text below'), 'captcha') ?>
            <img src="<?= $this->url->href('CaptchaController', 'image') ?>" alt="Captcha">
            <?= $this->form->text('captcha', array(), $errors, array('required')) ?>
        <?php endif ?>

        <?php if ($show_remember_me): ?>
            <?= $this->form->checkbox('remember_me', t('Remember Me'), 1, true) ?><br>
        <?php endif ?>

        <div class="form-actions">
            <button type="submit" class="btn btn-blue"><?= t('Sign in') ?></button>
        </div>
        <?php if ($show_password_reset): ?>
            <div class="reset-password">
                <?= $this->url->link(t('Forgot password?'), 'PasswordResetController', 'create') ?>
            </div>
        <?php endif ?>
    </form>
    <?php endif ?>

    <?= $this->hook->render('template:auth:login-form:after') ?>
</div>
