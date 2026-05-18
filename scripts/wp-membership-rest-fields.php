<?php
/**
 * Plugin Name: AXIS REST API
 * Description: Membership plans + trainee bookings for the AXIS website.
 * Version: 1.2.1
 */

if (!defined('ABSPATH')) {
    exit;
}

function axis_membership_get_field($post_id, $field)
{
    if (function_exists('get_field')) {
        $acf_value = get_field($field, $post_id);
        if ($acf_value !== null && $acf_value !== false && $acf_value !== '') {
            return $acf_value;
        }
    }

    $meta_value = get_post_meta($post_id, $field, true);
    if ($meta_value !== '' && $meta_value !== null) {
        return $meta_value;
    }

    return null;
}

function axis_membership_normalize_features($value)
{
    if (is_array($value)) {
        return array_values(array_filter(array_map('strval', $value)));
    }

    if (is_string($value) && $value !== '') {
        $decoded = json_decode($value, true);
        if (is_array($decoded)) {
            return axis_membership_normalize_features($decoded);
        }

        return array_values(array_filter(array_map('trim', preg_split('/\r\n|\r|\n/', $value))));
    }

    return array();
}

function axis_membership_build_plan($post)
{
    $post_id = (int) $post->ID;

    return array(
        'id' => $post_id,
        'status' => $post->post_status,
        'category' => (string) (axis_membership_get_field($post_id, 'category') ?: ''),
        'time' => (string) (axis_membership_get_field($post_id, 'time') ?: ''),
        'price' => (string) (axis_membership_get_field($post_id, 'price') ?: ''),
        'duration' => (string) (axis_membership_get_field($post_id, 'duration') ?: ''),
        'features' => axis_membership_normalize_features(axis_membership_get_field($post_id, 'features')),
    );
}

function axis_membership_get_plans()
{
    $posts = get_posts(array(
        'post_type' => 'membership',
        'post_status' => 'publish',
        'numberposts' => 100,
        'orderby' => 'date',
        'order' => 'DESC',
    ));

    $plans = array();
    foreach ($posts as $post) {
        $plans[] = axis_membership_build_plan($post);
    }

    return $plans;
}

add_action('rest_api_init', function () {
    $fields = array('category', 'time', 'price', 'duration', 'features');

    foreach ($fields as $field) {
        register_rest_field(
            'membership',
            $field,
            array(
                'get_callback' => function ($post) use ($field) {
                    return axis_membership_get_field((int) $post['id'], $field);
                },
                'schema' => array(
                    'type' => 'string',
                    'context' => array('view', 'edit'),
                ),
            )
        );
    }

    register_rest_route('axis/v1', '/memberships', array(
        'methods' => 'GET',
        'callback' => function () {
            return axis_membership_get_plans();
        },
        'permission_callback' => '__return_true',
    ));

    register_rest_route('axis/v1', '/trainee', array(
        'methods' => 'POST',
        'callback' => 'axis_create_trainee_booking',
        'permission_callback' => '__return_true',
        'args' => array(
            'username' => array('required' => true, 'type' => 'string'),
            'email' => array('required' => true, 'type' => 'string'),
            'phone' => array('required' => true, 'type' => 'string'),
            'gender' => array('required' => true, 'type' => 'string'),
            'date_of_birth' => array('required' => true, 'type' => 'string'),
            'package' => array('required' => true, 'type' => 'integer'),
        ),
    ));
});

function axis_trainee_set_field($post_id, $field, $value)
{
    if (function_exists('update_field')) {
        update_field($field, $value, $post_id);
    }

    update_post_meta($post_id, $field, $value);

    if (function_exists('pods')) {
        $pod = pods('trainee', $post_id);
        if ($pod && $pod->exists()) {
            $pod->save($field, $value);
        }
    }
}

function axis_create_trainee_booking(WP_REST_Request $request)
{
    $username = sanitize_text_field($request->get_param('username'));
    $email = sanitize_email($request->get_param('email'));
    $phone = sanitize_text_field($request->get_param('phone'));
    $gender = sanitize_text_field($request->get_param('gender'));
    $date_of_birth = sanitize_text_field($request->get_param('date_of_birth'));
    $package_id = absint($request->get_param('package'));

    if ($username === '' || $email === '' || $phone === '' || $gender === '' || $date_of_birth === '') {
        return new WP_Error('missing_fields', 'Please fill in all required fields.', array('status' => 400));
    }

    if (!is_email($email)) {
        return new WP_Error('invalid_email', 'Please enter a valid email address.', array('status' => 400));
    }

    if (!$package_id || get_post_type($package_id) !== 'membership') {
        return new WP_Error('invalid_package', 'Please select a valid membership plan.', array('status' => 400));
    }

    $post_id = wp_insert_post(array(
        'post_type' => 'trainee',
        'post_status' => 'publish',
        'post_title' => $username,
    ), true);

    if (is_wp_error($post_id)) {
        return new WP_Error('create_failed', 'Could not save your booking. Please try again.', array('status' => 500));
    }

    axis_trainee_set_field($post_id, 'username', $username);
    axis_trainee_set_field($post_id, 'email', $email);
    axis_trainee_set_field($post_id, 'phone', $phone);
    axis_trainee_set_field($post_id, 'gender', $gender);
    axis_trainee_set_field($post_id, 'date_of_birth', $date_of_birth);
    axis_trainee_set_field($post_id, 'package', $package_id);

    return rest_ensure_response(array(
        'success' => true,
        'id' => $post_id,
        'message' => 'Booking received successfully.',
    ));
}

add_filter('rest_pre_dispatch', function ($result, $server, $request) {
    if ($request->get_method() === 'OPTIONS' && strpos($request->get_route(), '/axis/v1/') === 0) {
        return new WP_REST_Response(null, 204);
    }

    return $result;
}, 10, 3);

add_filter('rest_pre_serve_request', function ($served, $result, $request) {
    if (strpos($request->get_route(), '/axis/v1/') !== 0) {
        return $served;
    }

    header('Access-Control-Allow-Origin: *');
    header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type, Accept');

    return $served;
}, 10, 4);
