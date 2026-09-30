<?php
/** One-off (key guarded, deleted after use): publish /offer/ and archive the remaining old WP pages as drafts titled "OLD - ...". */
header('Content-Type: text/plain; charset=UTF-8');
define('RCT_KEY', '__KEY__');
if (!isset($_GET['key']) || !hash_equals(RCT_KEY, (string)$_GET['key'])) { http_response_code(404); exit('not found'); }
define('WP_USE_THEMES', false);
require __DIR__ . '/wp-load.php';
$dir = dirname(ABSPATH) . '/rct-backup'; if (!is_dir($dir)) { mkdir($dir, 0700, true); }
$log = ['time' => date('c'), 'archived' => []];

// 1. /offer/
$ex = get_page_by_path('offer');
if ($ex) { echo "offer already exists id {$ex->ID}\n"; $nid = $ex->ID; }
else {
    $nid = wp_insert_post(['post_type' => 'page', 'post_status' => 'publish', 'post_title' => 'The 90-Day Sprint', 'post_name' => 'offer', 'post_content' => '', 'comment_status' => 'closed'], true);
    if (is_wp_error($nid)) { exit('ERROR ' . $nid->get_error_message()); }
}
$p = get_post($nid);
update_post_meta($nid, '_rct_static', 'offer.html');
update_post_meta($nid, 'rank_math_robots', ['noindex', 'nofollow']);
echo "offer: id $nid slug {$p->post_name} -> " . get_permalink($nid) . "\n";
$log['offer_id'] = $nid;

// 2. archive the remaining old pages
foreach ([2188, 2172, 2135, 2062, 1994, 1966, 1900, 1877, 1851, 1843, 1772, 1765, 985, 646] as $id) {
    $o = get_post($id);
    if (!$o || $o->post_status !== 'publish') { echo "skip $id\n"; continue; }
    $log['archived'][] = ['id' => $id, 'slug' => $o->post_name, 'title' => $o->post_title, 'status' => $o->post_status];
    wp_update_post(['ID' => $id, 'post_status' => 'draft', 'post_title' => 'OLD - ' . $o->post_title]);
    echo "archived $id /{$o->post_name}/ as draft 'OLD - {$o->post_title}'\n";
}
file_put_contents($dir . '/state2.json', json_encode($log, JSON_PRETTY_PRINT));
do_action('litespeed_purge_all');
if (function_exists('speedycache_delete_cache')) { @speedycache_delete_cache(); }
do_action('swcfpc_purge_cache');
wp_cache_flush(); flush_rewrite_rules(false);
echo "done\n";
