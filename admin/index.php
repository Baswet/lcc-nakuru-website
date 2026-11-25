<?php
declare(strict_types=1);
/**
 * LCC website admin (PHP hosting only; not active on GitHub Pages).
 * Edits data/content.json; reads private form submissions; uploads images.
 * Security: hashed password (tools/set-admin-password.php), session hardening, CSRF on every POST,
 * login throttling, idle timeout, output escaping, validated uploads, content backups before each save.
 */
require dirname(__DIR__) . '/private/bootstrap.php';
lcc_headers();
header('Cache-Control: no-store');
header('X-Robots-Tag: noindex, nofollow');
lcc_session();
$cfg = lcc_config();
$flash = '';
$act = (string)($_POST['action'] ?? '');

if (empty($cfg['admin_hash'])) {
    page('Setup needed', '<p>No admin account exists yet. On the server, run <code>php tools/set-admin-password.php yourname</code>, then reload this page.</p>');
}

if (!empty($_SESSION['admin']) && (time() - ($_SESSION['seen'] ?? 0)) > 1800) { $_SESSION = []; session_regenerate_id(true); $flash = 'Signed out after 30 minutes of inactivity.'; }

if ($act !== '' && !lcc_csrf_ok($_POST['csrf'] ?? null)) { http_response_code(403); page('Expired', '<p>Your form expired. <a href="./">Reload</a> and try again.</p>'); }

// ---------- login / logout
if ($act === 'login') {
    if (!lcc_rate_ok('login', 8)) { $flash = 'Too many attempts. Wait an hour and try again.'; }
    elseif (hash_equals((string)$cfg['admin_user'], (string)($_POST['user'] ?? '')) && password_verify((string)($_POST['pass'] ?? ''), (string)$cfg['admin_hash'])) {
        session_regenerate_id(true);
        $_SESSION['admin'] = true; $_SESSION['seen'] = time(); unset($_SESSION['csrf']);
        header('Location: ./'); exit;
    } else { usleep(400000); $flash = 'Incorrect username or password.'; }
}
if ($act === 'logout') { $_SESSION = []; session_regenerate_id(true); header('Location: ./'); exit; }

if (empty($_SESSION['admin'])) {
    page('Sign in', ($flash ? '<p class="err">' . lcc_e($flash) . '</p>' : '') . '<form method="post" class="box"><input type="hidden" name="action" value="login"><input type="hidden" name="csrf" value="' . lcc_e(lcc_csrf_token()) . '">
    <label>Username<input name="user" autocomplete="username" required></label><label>Password<input name="pass" type="password" autocomplete="current-password" required></label><button>Sign in</button></form>');
}
$_SESSION['seen'] = time();

// ---------- actions
$c = lcc_read_content();
$save = false;
$s = function (string $k, int $max = 500): string { return lcc_clean((string)($_POST[$k] ?? ''), $max); };
$ytId = function (string $in): string {
    if (preg_match('~(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})~', $in, $m)) { return $m[1]; }
    return preg_match('~^[A-Za-z0-9_-]{11}$~', $in) ? $in : '';
};
switch ($act) {
    case 'notice':
        $c['notice'] = ['show' => !empty($_POST['show']), 'text' => $s('text', 160), 'link' => $s('link', 200)]; $save = true; break;
    case 'services':
        $items = [];
        foreach ((array)($_POST['name'] ?? []) as $i => $n) {
            $n = lcc_clean((string)$n, 80); if ($n === '') continue;
            $w = lcc_clean((string)($_POST['watch'][$i] ?? ''), 200);
            $items[] = ['name' => $n, 'day' => lcc_clean((string)($_POST['day'][$i] ?? ''), 60), 'time' => lcc_clean((string)($_POST['time'][$i] ?? ''), 60), 'detail' => lcc_clean((string)($_POST['detail'][$i] ?? ''), 200),
                'status' => (($_POST['status'][$i] ?? '') === 'confirmed') ? 'confirmed' : 'reported', 'watch' => preg_match('~^https://~', $w) ? $w : '', 'source' => lcc_clean((string)($_POST['source'][$i] ?? ''), 200)];
        }
        $c['services']['items'] = $items; $c['services']['verified'] = !empty($_POST['verified']); $c['services']['times_note'] = $s('note', 300); $save = true; break;
    case 'giving':
        $pb = preg_replace('/\D/', '', $s('paybill', 10));
        $c['giving'] = ['verified' => !empty($_POST['verified']) && $pb !== '', 'mpesa_paybill' => $pb, 'mpesa_account' => $s('account', 60), 'note' => $s('note', 400)]; $save = true; break;
    case 'video_add':
        $id = $ytId($s('yt', 200));
        $cat = in_array($_POST['category'] ?? '', ['sermon', 'worship', 'conference', 'story'], true) ? $_POST['category'] : 'sermon';
        if ($id === '' || $s('title') === '') { $flash = 'Enter a valid YouTube link or ID and a title.'; break; }
        $c['videos'] = array_values(array_filter($c['videos'] ?? [], function ($v) use ($id) { return $v['id'] !== $id; }));
        array_unshift($c['videos'], ['id' => $id, 'title' => $s('title', 140), 'full_title' => $s('title', 140), 'speaker' => $s('speaker', 80), 'category' => $cat, 'published' => date('j M Y')]);
        $save = true; break;
    case 'video_del':
        $id = $s('id', 11); $c['videos'] = array_values(array_filter($c['videos'] ?? [], function ($v) use ($id) { return $v['id'] !== $id; })); $save = true; break;
    case 'event_add':
        $st = $s('start', 10); $en = $s('end', 10) ?: $st;
        if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $st) || !preg_match('/^\d{4}-\d{2}-\d{2}$/', $en) || $s('title') === '') { $flash = 'Title and valid dates are required.'; break; }
        $ext = $s('external', 300); if ($ext !== '' && !preg_match('~^https://~', $ext)) { $flash = 'Registration links must start with https://'; break; }
        $c['events'][] = ['slug' => substr(preg_replace('/[^a-z0-9]+/', '-', strtolower($s('title'))), 0, 60), 'title' => $s('title', 140), 'start' => $st, 'end' => $en, 'place' => $s('place', 160), 'summary' => $s('summary', 600), 'url' => 'events.html', 'external' => $ext];
        $save = true; break;
    case 'event_del':
        $k = (int)($_POST['i'] ?? -1); if (isset($c['events'][$k])) { array_splice($c['events'], $k, 1); $save = true; } break;
    case 'news_add':
        if ($s('title') === '') { $flash = 'Title is required.'; break; }
        array_unshift($c['news'], ['slug' => substr(preg_replace('/[^a-z0-9]+/', '-', strtolower($s('title'))), 0, 60), 'date' => $s('date', 20) ?: date('Y-m'), 'title' => $s('title', 140), 'summary' => $s('summary', 800), 'video' => $ytId($s('yt', 200))]);
        $save = true; break;
    case 'news_del':
        $k = (int)($_POST['i'] ?? -1); if (isset($c['news'][$k])) { array_splice($c['news'], $k, 1); $save = true; } break;
    case 'photos':
        foreach (($c['photos'] ?? []) as $k => $ph) {
            $src = basename((string)($_POST['src'][$k] ?? ''));
            $ok = $src !== '' && is_file(LCC_ROOT . '/assets/uploads/' . $src);
            $c['photos'][$k]['src'] = $ok ? 'assets/uploads/' . $src : '';
            $c['photos'][$k]['approved'] = $ok && !empty($_POST['approved'][$k]);
            $c['photos'][$k]['desc'] = lcc_clean((string)($_POST['desc'][$k] ?? $ph['desc']), 160);
        }
        $save = true; break;
    case 'contact':
        foreach (['phone' => 30, 'email' => 120, 'street' => 120, 'postal' => 120] as $k => $max) { $c['contact'][$k] = $s($k, $max); }
        $c['contact']['phone_intl'] = '+254' . substr(preg_replace('/\D/', '', $c['contact']['phone']), -9);
        $save = true; break;
    case 'ministry':
        foreach (($c['ministries'] ?? []) as $k => $m) {
            if (isset($_POST['text'][$k])) { $c['ministries'][$k]['text'] = lcc_clean((string)$_POST['text'][$k], 600); }
        }
        $c['ministries_note'] = $s('mnote', 400); $save = true; break;
    case 'past_add':
        if ($s('title') === '') { $flash = 'Title is required.'; break; }
        array_unshift($c['past_events'], ['title' => $s('title', 140), 'when' => $s('when', 40), 'category' => $s('category', 40) ?: 'Event', 'summary' => $s('summary', 600), 'video' => $ytId($s('yt', 200))]);
        $save = true; break;
    case 'past_del':
        $k = (int)($_POST['i'] ?? -1); if (isset($c['past_events'][$k])) { array_splice($c['past_events'], $k, 1); $save = true; } break;
    case 'sub_del':
        $f = basename($s('f', 80)); $p = LCC_PRIVATE . '/submissions/' . $f;
        if (preg_match('/^[0-9]{8}-[0-9]{6}-[a-f0-9]{16}\.json$/', $f) && is_file($p)) { unlink($p); $flash = 'Submission deleted.'; } break;
    case 'upload':
        $flash = handle_upload(); break;
}
if ($save) { $flash = lcc_write_content($c) ? 'Saved. Run python3 tools/build.py on the server (or ask your web developer) to republish the pages; the notice, giving and sermon library update straight away.' : 'Could not save — check file permissions on data/content.json.'; }

function handle_upload(): string {
    $f = $_FILES['img'] ?? null;
    if (!$f || ($f['error'] ?? 1) !== UPLOAD_ERR_OK) { return 'Upload failed.'; }
    if ($f['size'] > 3 * 1024 * 1024) { return 'Images must be under 3 MB.'; }
    $mime = (new finfo(FILEINFO_MIME_TYPE))->file($f['tmp_name']);
    $ext = ['image/jpeg' => 'jpg', 'image/png' => 'png', 'image/webp' => 'webp'][$mime] ?? null;
    if (!$ext || !@getimagesize($f['tmp_name'])) { return 'Only JPG, PNG or WebP images are allowed.'; }
    $name = date('Ymd') . '-' . bin2hex(random_bytes(6)) . '.' . $ext;
    $dest = LCC_ROOT . '/assets/uploads/' . $name;
    // Re-encode with GD when available to strip metadata and any embedded payloads.
    if (function_exists('imagecreatefromstring')) {
        $im = @imagecreatefromstring((string)file_get_contents($f['tmp_name']));
        if (!$im) { return 'That image could not be read.'; }
        $ok = $ext === 'png' ? imagepng($im, $dest, 7) : ($ext === 'webp' && function_exists('imagewebp') ? imagewebp($im, $dest, 82) : imagejpeg($im, $dest, 84));
        imagedestroy($im);
        if (!$ok) { return 'Could not save the image.'; }
    } elseif (!move_uploaded_file($f['tmp_name'], $dest)) { return 'Could not save the image.'; }
    chmod($dest, 0644);
    return 'Uploaded: assets/uploads/' . $name . ' — only upload photos LCC has permission to use.';
}

// ---------- view
$t = lcc_e(lcc_csrf_token());
$hid = function (string $a) use ($t) { return '<input type="hidden" name="csrf" value="' . $t . '"><input type="hidden" name="action" value="' . $a . '">'; };
ob_start(); ?>
<p class="bar"><?= $flash ? '<span class="ok">' . lcc_e($flash) . '</span>' : 'Signed in.' ?> <form method="post" style="display:inline"><?= $hid('logout') ?><button class="link">Sign out</button></form></p>
<nav class="tabs"><a href="#photos">Photos</a><a href="#contact">Contact</a><a href="#ministries">Ministries</a><a href="#past">Past events</a><a href="#notice">Notice</a><a href="#services">Services</a><a href="#giving">Giving</a><a href="#videos">Videos</a><a href="#events">Events</a><a href="#news">News</a><a href="#subs">Submissions</a><a href="#upload">Images</a></nav>

<section id="photos"><h2>Photo slots</h2><form method="post" class="box"><?= $hid('photos') ?>
<p class="warn">Approve a photo only when the church owns it or has permission. Upload it under “Images” first, then pick it here. Until a slot is approved, the site shows LCC's own YouTube stills.</p>
<?php $ups = array_map('basename', glob(LCC_ROOT . '/assets/uploads/*.{jpg,png,webp}', GLOB_BRACE) ?: []); foreach (($c['photos'] ?? []) as $k => $ph): ?>
<div class="grid"><b><?= lcc_e($ph['slot']) ?></b><input name="desc[<?= (int)$k ?>]" value="<?= lcc_e($ph['desc']) ?>"><select name="src[<?= (int)$k ?>]"><option value="">— YouTube still (default) —</option><?php foreach ($ups as $u): ?><option <?= basename((string)$ph['src']) === $u ? 'selected' : '' ?>><?= lcc_e($u) ?></option><?php endforeach; ?></select><label class="row"><input type="checkbox" name="approved[<?= (int)$k ?>]" <?= !empty($ph['approved']) ? 'checked' : '' ?>> Approved</label></div>
<?php endforeach; ?><button>Save photos</button></form></section>

<section id="contact"><h2>Contact details</h2><form method="post" class="box"><?= $hid('contact') ?>
<?php foreach (['phone' => 'Phone', 'email' => 'Email', 'street' => 'Street', 'postal' => 'Postal address'] as $k => $l): ?><label><?= $l ?><input name="<?= $k ?>" value="<?= lcc_e($c['contact'][$k] ?? '') ?>"></label><?php endforeach; ?><button>Save</button></form></section>

<section id="ministries"><h2>Ministries</h2><form method="post" class="box"><?= $hid('ministry') ?>
<?php foreach (($c['ministries'] ?? []) as $k => $m): ?><label><?= lcc_e($m['name']) ?><textarea name="text[<?= (int)$k ?>]"><?= lcc_e($m['text']) ?></textarea></label><?php endforeach; ?>
<label>Note under ministries<input name="mnote" value="<?= lcc_e($c['ministries_note'] ?? '') ?>"></label><button>Save</button></form></section>

<section id="past"><h2>Past events archive</h2><form method="post" class="box"><?= $hid('past_add') ?>
<div class="grid"><input name="title" placeholder="Title" required><input name="when" placeholder="When, e.g. December 2026"><input name="category" placeholder="Category"><input name="yt" placeholder="YouTube link (optional)"></div>
<label>Summary<textarea name="summary"></textarea></label><button>Add past event</button></form>
<table><?php foreach (($c['past_events'] ?? []) as $i => $ev): ?><tr><td><?= lcc_e($ev['title']) ?></td><td><?= lcc_e($ev['when']) ?></td><td><form method="post"><?= $hid('past_del') ?><input type="hidden" name="i" value="<?= (int)$i ?>"><button class="link">Remove</button></form></td></tr><?php endforeach; ?></table></section>

<section id="notice"><h2>Notice bar</h2><form method="post" class="box"><?= $hid('notice') ?>
<label class="row"><input type="checkbox" name="show" <?= !empty($c['notice']['show']) ? 'checked' : '' ?>> Show notice bar</label>
<label>Text<input name="text" maxlength="160" value="<?= lcc_e($c['notice']['text'] ?? '') ?>"></label>
<label>Link (page or https URL)<input name="link" value="<?= lcc_e($c['notice']['link'] ?? '') ?>"></label><button>Save</button></form></section>

<section id="services"><h2>Service times</h2><form method="post" class="box"><?= $hid('services') ?>
<?php foreach (array_merge($c['services']['items'] ?? [], [['name' => '', 'day' => '', 'time' => '', 'detail' => '']]) as $it): ?>
<div class="grid"><input name="name[]" placeholder="Name" value="<?= lcc_e($it['name']) ?>"><input name="day[]" placeholder="Day" value="<?= lcc_e($it['day']) ?>"><input name="time[]" placeholder="Time" value="<?= lcc_e($it['time']) ?>"><input name="detail[]" placeholder="Detail" value="<?= lcc_e($it['detail']) ?>"><select name="status[]"><option value="confirmed" <?= ($it['status'] ?? '') === 'confirmed' ? 'selected' : '' ?>>Confirmed</option><option value="reported" <?= ($it['status'] ?? '') !== 'confirmed' ? 'selected' : '' ?>>Needs confirmation</option></select><input name="watch[]" placeholder="YouTube link (https)" value="<?= lcc_e($it['watch'] ?? '') ?>"><input name="source[]" placeholder="Source" value="<?= lcc_e($it['source'] ?? '') ?>"></div>
<?php endforeach; ?>
<label>Note shown while times are unconfirmed<input name="note" value="<?= lcc_e($c['services']['times_note'] ?? '') ?>"></label>
<label class="row"><input type="checkbox" name="verified" <?= !empty($c['services']['verified']) ? 'checked' : '' ?>> These times are confirmed by the church office</label><button>Save</button></form></section>

<section id="giving"><h2>Giving</h2><form method="post" class="box"><?= $hid('giving') ?>
<p class="warn">Only publish payment details confirmed directly by the LCC church office. Wrong numbers can cost people money.</p>
<label>M-Pesa Paybill<input name="paybill" inputmode="numeric" value="<?= lcc_e($c['giving']['mpesa_paybill'] ?? '') ?>"></label>
<label>Account name<input name="account" value="<?= lcc_e($c['giving']['mpesa_account'] ?? '') ?>"></label>
<label>Message while not published<input name="note" value="<?= lcc_e($c['giving']['note'] ?? '') ?>"></label>
<label class="row"><input type="checkbox" name="verified" <?= !empty($c['giving']['verified']) ? 'checked' : '' ?>> Confirmed by the church office — publish on the Give page</label><button>Save</button></form></section>

<section id="videos"><h2>Videos (<?= count($c['videos'] ?? []) ?>)</h2><form method="post" class="box"><?= $hid('video_add') ?>
<div class="grid"><input name="yt" placeholder="YouTube link or ID" required><input name="title" placeholder="Title" required><input name="speaker" placeholder="Speaker"><select name="category"><option value="sermon">Message</option><option value="worship">Worship</option><option value="conference">Conference</option><option value="story">Story</option></select></div><button>Add to top</button></form>
<table><?php foreach (($c['videos'] ?? []) as $v): ?><tr><td><?= lcc_e($v['title']) ?></td><td><?= lcc_e($v['category']) ?></td><td><form method="post"><?= $hid('video_del') ?><input type="hidden" name="id" value="<?= lcc_e($v['id']) ?>"><button class="link">Remove</button></form></td></tr><?php endforeach; ?></table></section>

<section id="events"><h2>Events</h2><form method="post" class="box"><?= $hid('event_add') ?>
<div class="grid"><input name="title" placeholder="Title" required><input name="start" type="date" required><input name="end" type="date"><input name="place" placeholder="Place"></div>
<label>Summary<textarea name="summary"></textarea></label><label>Registration link (https, optional)<input name="external" type="url"></label><button>Add event</button></form>
<table><?php foreach (($c['events'] ?? []) as $i => $ev): ?><tr><td><?= lcc_e($ev['title']) ?></td><td><?= lcc_e($ev['start']) ?></td><td><form method="post"><?= $hid('event_del') ?><input type="hidden" name="i" value="<?= (int)$i ?>"><button class="link">Remove</button></form></td></tr><?php endforeach; ?></table></section>

<section id="news"><h2>News</h2><form method="post" class="box"><?= $hid('news_add') ?>
<div class="grid"><input name="title" placeholder="Title" required><input name="date" placeholder="Date, e.g. 2026-12"><input name="yt" placeholder="YouTube link (optional)"></div>
<label>Summary<textarea name="summary"></textarea></label><button>Add story</button></form>
<table><?php foreach (($c['news'] ?? []) as $i => $n): ?><tr><td><?= lcc_e($n['title']) ?></td><td><?= lcc_e($n['date']) ?></td><td><form method="post"><?= $hid('news_del') ?><input type="hidden" name="i" value="<?= (int)$i ?>"><button class="link">Remove</button></form></td></tr><?php endforeach; ?></table></section>

<section id="subs"><h2>Form submissions</h2><p class="warn">Prayer requests are confidential. Do not copy them anywhere public.</p>
<?php $files = glob(LCC_PRIVATE . '/submissions/*.json') ?: []; rsort($files);
if (!$files) echo '<p>No submissions yet.</p>';
foreach (array_slice($files, 0, 100) as $file): $r = json_decode((string)file_get_contents($file), true) ?: []; ?>
<article class="box sub"><b><?= lcc_e(ucfirst($r['type'] ?? '')) ?></b> · <?= lcc_e($r['received'] ?? '') ?> · <?= lcc_e($r['name'] ?: 'Anonymous') ?> · <?= lcc_e($r['reply'] ?? '') ?>
<p><?= nl2br(lcc_e($r['message'] ?? '')) ?></p><form method="post"><?= $hid('sub_del') ?><input type="hidden" name="f" value="<?= lcc_e(basename($file)) ?>"><button class="link">Delete</button></form></article>
<?php endforeach; ?></section>

<section id="upload"><h2>Upload an image</h2><form method="post" enctype="multipart/form-data" class="box"><?= $hid('upload') ?>
<p class="warn">Upload only photos LCC owns or has permission to use. JPG, PNG or WebP, max 3 MB.</p><input type="file" name="img" accept="image/jpeg,image/png,image/webp" required><button>Upload</button></form></section>
<?php page('Dashboard', (string)ob_get_clean());

function page(string $title, string $body): void {
    echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>' . lcc_e($title) . ' · LCC admin</title><style>
body{font:16px/1.5 system-ui,sans-serif;background:#F6F1E8;color:#1E1A16;margin:0;padding:24px;max-width:960px;margin:auto}h1{font-family:Georgia,serif;font-weight:400}h2{font-family:Georgia,serif;font-weight:400;margin-top:40px}
.box{background:#FFFCF6;border:1px solid #DDD0BC;border-radius:8px;padding:18px;display:grid;gap:12px;margin:12px 0}label{display:grid;gap:4px;font-weight:600}.row{display:flex;gap:8px;align-items:center;font-weight:500}
input,textarea,select{font:inherit;padding:10px;border:1px solid #B9AC9A;border-radius:6px;background:#fff}textarea{min-height:90px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px}
button{font:600 15px system-ui;background:#1E1A16;color:#fff;border:0;border-radius:999px;padding:10px 18px;cursor:pointer;justify-self:start}button.link{background:none;color:#A3442A;padding:4px;text-decoration:underline}
table{width:100%;border-collapse:collapse}td{border-top:1px solid #DDD0BC;padding:6px}.tabs a{margin-right:12px;color:#A3442A}.warn{background:#F7E9C8;padding:10px;border-radius:6px;margin:0}.ok{color:#2E4A12}.err{color:#7A1F12}.sub p{white-space:normal;margin:0}
</style></head><body><h1>LCC website admin</h1>' . $body . '</body></html>';
    exit;
}
