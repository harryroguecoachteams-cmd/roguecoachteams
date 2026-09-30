<?php
/**
 * Plugin Name: RCT static pages
 * Description: Serves prebuilt HTML from /rct-v2/pages/ for any page or post that carries the _rct_static meta.
 *              The WordPress post keeps the slug, so URLs, the sitemap and menus are untouched.
 *              To switch a page back: set the new post to draft and publish the old one (see rct-migrate revert).
 */
if (!defined('ABSPATH')) { exit; }

add_action('template_redirect', function () {
    if (!is_singular()) { return; }
    $id = get_queried_object_id();
    if (!$id) { return; }
    $file = get_post_meta($id, '_rct_static', true);
    if (!$file || !preg_match('/^[a-z0-9-]+\.html$/', $file)) { return; }
    $path = ABSPATH . 'rct-v2/pages/' . $file;
    if (!is_readable($path)) { return; }
    status_header(200);
    nocache_headers();
    header('Content-Type: text/html; charset=UTF-8');
    header('X-RCT-Static: ' . $file);
    readfile($path);
    exit;
}, 0);
