<?php
declare(strict_types=1);
// Shared helpers for api/ and admin/. PHP 7.4 – 8.4 compatible.

define('LCC_ROOT', dirname(__DIR__));
define('LCC_PRIVATE', __DIR__);
define('LCC_CONTENT', LCC_ROOT . '/data/content.json');

function lcc_config(): array {
    $f = LCC_PRIVATE . '/config.php';
    if (!is_file($f)) { return []; }
    $c = require $f;
    return is_array($c) ? $c : [];
}

function lcc_session(): void {
    if (session_status() === PHP_SESSION_ACTIVE) { return; }
    $secure = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off');
    session_name('lcc_sid');
    session_set_cookie_params(['lifetime' => 0, 'path' => '/', 'secure' => $secure, 'httponly' => true, 'samesite' => 'Strict']);
    ini_set('session.use_strict_mode', '1');
    session_start();
}

function lcc_headers(): void {
    header('X-Content-Type-Options: nosniff');
    header('X-Frame-Options: DENY');
    header('Referrer-Policy: same-origin');
    header("Content-Security-Policy: default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; form-action 'self'");
}

function lcc_csrf_token(): string {
    lcc_session();
    if (empty($_SESSION['csrf'])) { $_SESSION['csrf'] = bin2hex(random_bytes(32)); }
    return $_SESSION['csrf'];
}

function lcc_csrf_ok(?string $t): bool {
    lcc_session();
    return is_string($t) && !empty($_SESSION['csrf']) && hash_equals($_SESSION['csrf'], $t);
}

function lcc_json(int $code, array $data): void {
    http_response_code($code);
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');
    echo json_encode($data);
    exit;
}

function lcc_clean(string $s, int $max): string {
    $s = trim(str_replace("\0", '', $s));
    $s = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', $s) ?? '';
    return function_exists('mb_substr') ? mb_substr($s, 0, $max) : substr($s, 0, $max);
}

function lcc_e($s): string { return htmlspecialchars((string)$s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }

function lcc_read_content(): array {
    $j = json_decode((string)@file_get_contents(LCC_CONTENT), true);
    return is_array($j) ? $j : [];
}

/** Atomic write with a timestamped backup of the previous version. */
function lcc_write_content(array $c): bool {
    $dir = LCC_PRIVATE . '/backups';
    if (!is_dir($dir)) { mkdir($dir, 0700, true); }
    if (is_file(LCC_CONTENT)) { copy(LCC_CONTENT, $dir . '/content-' . date('Ymd-His') . '.json'); }
    $json = json_encode($c, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    if ($json === false) { return false; }
    $tmp = LCC_CONTENT . '.tmp';
    return file_put_contents($tmp, $json, LOCK_EX) !== false && rename($tmp, LCC_CONTENT);
}

function lcc_rate_ok(string $bucket, int $max): bool {
    $ip = hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? 'x') . $bucket);
    $f = LCC_PRIVATE . '/rate.json';
    $fh = fopen($f, 'c+'); if (!$fh) { return true; }
    flock($fh, LOCK_EX);
    $d = json_decode((string)stream_get_contents($fh), true) ?: [];
    $now = time();
    foreach ($d as $k => $ts) { $d[$k] = array_values(array_filter((array)$ts, function ($t) use ($now) { return $t > $now - 3600; })); if (!$d[$k]) unset($d[$k]); }
    $ok = count($d[$ip] ?? []) < $max;
    if ($ok) { $d[$ip][] = $now; }
    ftruncate($fh, 0); rewind($fh); fwrite($fh, json_encode($d)); flock($fh, LOCK_UN); fclose($fh);
    return $ok;
}
