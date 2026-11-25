<?php
// Copy to private/config.php (or run: php tools/set-admin-password.php <username>).
// Never commit config.php. Keep private/ outside the web root where the host allows.
return [
    'admin_user'     => 'lccadmin',
    'admin_hash'     => '',            // password_hash() output, created by tools/set-admin-password.php
    'notify_email'   => '',            // optional: church office address to notify of new submissions (no message content is emailed)
    'max_per_hour'   => 5,             // form submissions allowed per IP per hour
];
