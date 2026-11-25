<?php
// CLI only: php tools/set-admin-password.php <username>
// Prompts for a password and writes private/config.php with a bcrypt/argon hash. The password is never stored.
if (PHP_SAPI !== 'cli') { http_response_code(404); exit; }
$user = $argv[1] ?? 'lccadmin';
fwrite(STDOUT, "New admin password (min 12 chars): ");
if (DIRECTORY_SEPARATOR === '/') { system('stty -echo'); }
$pw = trim((string)fgets(STDIN));
if (DIRECTORY_SEPARATOR === '/') { system('stty echo'); }
fwrite(STDOUT, "\n");
if (strlen($pw) < 12) { fwrite(STDERR, "Password too short.\n"); exit(1); }
$algo = defined('PASSWORD_ARGON2ID') ? PASSWORD_ARGON2ID : PASSWORD_DEFAULT;
$cfgFile = dirname(__DIR__) . '/private/config.php';
$cfg = is_file($cfgFile) ? (require $cfgFile) : (require dirname(__DIR__) . '/private/config.sample.php');
$cfg['admin_user'] = $user;
$cfg['admin_hash'] = password_hash($pw, $algo);
file_put_contents($cfgFile, "<?php\nreturn " . var_export($cfg, true) . ";\n", LOCK_EX);
chmod($cfgFile, 0600);
fwrite(STDOUT, "Saved admin credentials for '$user' to private/config.php\n");
