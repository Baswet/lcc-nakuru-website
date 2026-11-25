<?php
declare(strict_types=1);
require dirname(__DIR__) . '/private/bootstrap.php';
lcc_headers();
lcc_json(200, ['token' => lcc_csrf_token()]);
