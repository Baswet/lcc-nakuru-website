<?php
declare(strict_types=1);
// Receives contact and prayer forms. Submissions are stored in private/submissions (never public).
require dirname(__DIR__) . '/private/bootstrap.php';
lcc_headers();
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') { lcc_json(405, ['error' => 'Method not allowed.']); }
if (!lcc_csrf_ok($_POST['csrf'] ?? null)) { lcc_json(403, ['error' => 'Your session expired. Please refresh the page and try again.']); }
if (!empty($_POST['website'])) { lcc_json(200, ['ok' => true]); } // honeypot: silently accept bots
$cfg = lcc_config();
if (!lcc_rate_ok('submit', (int)($cfg['max_per_hour'] ?? 5))) { lcc_json(429, ['error' => 'Too many messages from this connection. Please try again later or call 0722 864 864.']); }

$type = ($_POST['type'] ?? '') === 'prayer' ? 'prayer' : 'contact';
$name = lcc_clean((string)($_POST['name'] ?? ''), 100);
$reply = lcc_clean((string)($_POST['reply'] ?? ''), 120);
$msg = lcc_clean((string)($_POST['message'] ?? ''), 3000);
if ($msg === '') { lcc_json(422, ['error' => 'Please write a message.']); }
if ($type === 'contact' && ($name === '' || $reply === '')) { lcc_json(422, ['error' => 'Please give your name and an email or phone number.']); }
if ($type === 'prayer' && empty($_POST['consent'])) { lcc_json(422, ['error' => 'Please tick the consent box.']); }

$rec = ['id' => bin2hex(random_bytes(8)), 'type' => $type, 'received' => date('c'), 'name' => $name, 'reply' => $reply, 'message' => $msg, 'read' => false];
$dir = LCC_PRIVATE . '/submissions';
if (!is_dir($dir)) { mkdir($dir, 0700, true); }
if (file_put_contents($dir . '/' . date('Ymd-His') . '-' . $rec['id'] . '.json', json_encode($rec, JSON_UNESCAPED_UNICODE), LOCK_EX) === false) {
    lcc_json(500, ['error' => 'We could not save your message. Please call 0722 864 864.']);
}
if (!empty($cfg['notify_email']) && filter_var($cfg['notify_email'], FILTER_VALIDATE_EMAIL)) {
    // Notification only: no names or message content leave the server by email.
    @mail($cfg['notify_email'], 'New ' . $type . ' submission on the LCC website', "A new $type submission is waiting in the website admin.");
}
lcc_json(200, ['ok' => true]);
