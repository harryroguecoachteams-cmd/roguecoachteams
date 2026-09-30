<?php
/**
 * One-off migration. Guarded by a key, deleted after use.
 *   ?key=K&mode=dry     report only
 *   ?key=K&mode=apply   old page -> draft with slug "<slug>-old-v1", new page published with the ORIGINAL slug
 *   ?key=K&mode=revert  undo from the backup file
 * Backup: /home/<user>/rct-backup/state.json (outside the web root).
 */
header('Content-Type: text/plain; charset=UTF-8');
define('RCT_KEY', '__KEY__');
if (!isset($_GET['key']) || !hash_equals(RCT_KEY, (string)$_GET['key'])) { http_response_code(404); exit('not found'); }
define('WP_USE_THEMES', false);
require __DIR__ . '/wp-load.php';

$items = [
    ['id' => 1167, 'file' => 'index.html',                          'front' => true],
    ['id' => 1405, 'file' => 'services.html'],
    ['id' => 1425, 'file' => 'sprint.html'],
    ['id' => 1141, 'file' => 'pricing.html'],
    ['id' => 1561, 'file' => 'about.html'],
    ['id' => 310,  'file' => 'contact.html'],
    ['id' => 316,  'file' => 'insights.html'],
    ['id' => 1821, 'file' => 'coaching-scams.html'],
    ['id' => 1023, 'file' => 'authority-building-for-coaches.html'],
    ['id' => 919,  'file' => 'joint-ventures-for-coaches.html'],
];
// extra brand-new pages (no old page), e.g. offer.html at /offer/ - added only when passed in &extra=1
$mode = $_GET['mode'] ?? 'dry';
$dir  = dirname(ABSPATH) . '/rct-backup';
$state = $dir . '/state.json';
$suffix = '-old-v1';

function out($s) { echo $s . "\n"; }

if ($mode === 'revert') {
    $b = json_decode(file_get_contents($state), true);
    if (!$b) { exit("no backup at $state"); }
    foreach ($b['items'] as $it) {
        if (!empty($it['new_id'])) { wp_update_post(['ID' => $it['new_id'], 'post_status' => 'draft', 'post_name' => $it['slug'] . '-new-v2']); }
        wp_update_post(['ID' => $it['id'], 'post_status' => $it['status'], 'post_name' => $it['slug'], 'post_parent' => $it['parent']]);
        foreach ($it['menu_items'] as $mid) { update_post_meta($mid, '_menu_item_object_id', $it['id']); }
        out("reverted {$it['id']} -> /{$it['slug']}/ status {$it['status']}");
    }
    if (isset($b['page_on_front'])) { update_option('page_on_front', $b['page_on_front']); }
    exit("REVERT DONE");
}

$backup = ['time' => date('c'), 'page_on_front' => (int)get_option('page_on_front'), 'show_on_front' => get_option('show_on_front'), 'items' => []];
$errors = 0; $idmap = [];
foreach ($items as $it) {
    $p = get_post($it['id']);
    if (!$p) { out("MISSING id {$it['id']}"); $errors++; continue; }
    $uri = get_page_uri($p->ID);
    $menu = get_posts(['post_type' => 'nav_menu_item', 'post_status' => 'any', 'numberposts' => -1, 'fields' => 'ids',
                       'meta_query' => [['key' => '_menu_item_object_id', 'value' => $p->ID], ['key' => '_menu_item_type', 'value' => 'post_type']]]);
    out(sprintf("%-4d %-9s %-8s /%s/  parent=%d  menu_items=%d  -> %s%s", $p->ID, $p->post_type, $p->post_status, $p->post_name, $p->post_parent, count($menu), $it['file'], !empty($it['front']) ? '  [FRONT PAGE]' : ''));
    if ($mode !== 'apply') { continue; }
    if ($p->post_status !== 'publish') { out("  skip: not published"); continue; }
    if (file_exists(ABSPATH . 'rct-v2/pages/' . $it['file']) === false) { out("  ABORT: page file missing"); $errors++; continue; }
    $rec = ['id' => $p->ID, 'slug' => $p->post_name, 'status' => $p->post_status, 'type' => $p->post_type, 'parent' => $p->post_parent,
            'title' => $p->post_title, 'menu_items' => $menu, 'file' => $it['file']];
    // 1. free the slug: old page -> draft, renamed
    $r = wp_update_post(['ID' => $p->ID, 'post_status' => 'draft', 'post_name' => $p->post_name . $suffix], true);
    if (is_wp_error($r)) { out("  ERROR draft: " . $r->get_error_message()); $errors++; continue; }
    delete_post_meta($p->ID, '_wp_old_slug');
    // 2. new post with the original slug
    $args = ['post_type' => $p->post_type, 'post_status' => 'publish', 'post_title' => $p->post_title, 'post_name' => $rec['slug'],
             'post_parent' => isset($idmap[$p->post_parent]) ? $idmap[$p->post_parent] : $p->post_parent, 'post_author' => $p->post_author, 'post_content' => '', 'comment_status' => 'closed'];
    if ($p->post_type === 'post') { $args['post_date'] = $p->post_date; $args['post_date_gmt'] = $p->post_date_gmt; }
    $nid = wp_insert_post($args, true);
    if (is_wp_error($nid)) { out("  ERROR insert: " . $nid->get_error_message()); wp_update_post(['ID' => $p->ID, 'post_status' => 'publish', 'post_name' => $rec['slug']]); $errors++; continue; }
    $new = get_post($nid);
    if ($new->post_name !== $rec['slug']) {
        out("  SLUG MISMATCH got {$new->post_name}; rolling back this item");
        wp_delete_post($nid, true); wp_update_post(['ID' => $p->ID, 'post_status' => 'publish', 'post_name' => $rec['slug']]); $errors++; continue;
    }
    update_post_meta($nid, '_rct_static', $it['file']);
    $rec['new_id'] = $nid; $idmap[$p->ID] = $nid;
    foreach ($menu as $mid) { update_post_meta($mid, '_menu_item_object_id', $nid); }
    if (!empty($it['front']) && (int)get_option('page_on_front') === $p->ID) { update_option('page_on_front', $nid); out("  front page -> $nid"); }
    // keep category assignments for posts
    if ($p->post_type === 'post') { wp_set_post_categories($nid, wp_get_post_categories($p->ID)); }
    out("  OK: new id $nid at " . get_permalink($nid));
    $backup['items'][] = $rec;
}
if ($mode === 'apply') {
    if (!is_dir($dir)) { mkdir($dir, 0700, true); }
    // merge with any earlier backup so revert stays complete
    if (file_exists($state)) { $old = json_decode(file_get_contents($state), true); if ($old) { $backup['items'] = array_merge($old['items'], $backup['items']); $backup['page_on_front'] = $old['page_on_front']; } }
    file_put_contents($state, json_encode($backup, JSON_PRETTY_PRINT));
    // Rank Math auto-redirects on slug change would hijack the original URLs: remove any created for our slugs
    global $wpdb;
    $tbl = $wpdb->prefix . 'rank_math_redirections';
    if ($wpdb->get_var("SHOW TABLES LIKE '$tbl'") === $tbl) {
        $n = 0;
        foreach ($backup['items'] as $rec) {
            if (empty($rec['new_id'])) { continue; }
            $n += (int)$wpdb->query($wpdb->prepare("DELETE FROM $tbl WHERE sources LIKE %s OR url_to LIKE %s", '%' . $wpdb->esc_like($rec['slug'] . $suffix) . '%', '%' . $wpdb->esc_like($rec['slug'] . $suffix) . '%'));
        }
        out("rank math redirects removed: $n");
    }
    // purge caches
    do_action('litespeed_purge_all');
    if (function_exists('speedycache_delete_cache')) { @speedycache_delete_cache(); }
    do_action('swcfpc_purge_cache');
    if (function_exists('rocket_clean_domain')) { rocket_clean_domain(); }
    wp_cache_flush();
    flush_rewrite_rules(false);
    out("backup written: $state");
}
out("errors: $errors");
out("done ($mode)");
