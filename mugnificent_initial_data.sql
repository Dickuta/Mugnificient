-- Mugnificent E-Commerce Platform - Database Initialization Script
-- Created for University of Suffolk mugs store

BEGIN;

-- PERMISSIONS TABLE DATA
INSERT INTO permissions (id, name, description, created_at, updated_at) VALUES (1, 'view_products', 'View products', '2026-03-26 13:50:22.612312', '2026-03-26 13:50:22.612315');
INSERT INTO permissions (id, name, description, created_at, updated_at) VALUES (2, 'create_products', 'Create products', '2026-03-26 13:50:22.612315', '2026-03-26 13:50:22.612316');
INSERT INTO permissions (id, name, description, created_at, updated_at) VALUES (3, 'edit_products', 'Edit products', '2026-03-26 13:50:22.612316', '2026-03-26 13:50:22.612319');
INSERT INTO permissions (id, name, description, created_at, updated_at) VALUES (4, 'delete_products', 'Delete products', '2026-03-26 13:50:22.612319', '2026-03-26 13:50:22.612320');
INSERT INTO permissions (id, name, description, created_at, updated_at) VALUES (5, 'view_orders', 'View orders', '2026-03-26 13:50:22.612321', '2026-03-26 13:50:22.612321');
INSERT INTO permissions (id, name, description, created_at, updated_at) VALUES (6, 'create_orders', 'Create orders', '2026-03-26 13:50:22.612321', '2026-03-26 13:50:22.612347');
INSERT INTO permissions (id, name, description, created_at, updated_at) VALUES (7, 'edit_orders', 'Edit orders', '2026-03-26 13:50:22.612349', '2026-03-26 13:50:22.612349');
INSERT INTO permissions (id, name, description, created_at, updated_at) VALUES (8, 'delete_orders', 'Delete orders', '2026-03-26 13:50:22.612350', '2026-03-26 13:50:22.612350');
INSERT INTO permissions (id, name, description, created_at, updated_at) VALUES (9, 'view_users', 'View users', '2026-03-26 13:50:22.612350', '2026-03-26 13:50:22.612351');
INSERT INTO permissions (id, name, description, created_at, updated_at) VALUES (10, 'create_users', 'Create users', '2026-03-26 13:50:22.612351', '2026-03-26 13:50:22.612352');
INSERT INTO permissions (id, name, description, created_at, updated_at) VALUES (11, 'edit_users', 'Edit users', '2026-03-26 13:50:22.612352', '2026-03-26 13:50:22.612352');
INSERT INTO permissions (id, name, description, created_at, updated_at) VALUES (12, 'delete_users', 'Delete users', '2026-03-26 13:50:22.612353', '2026-03-26 13:50:22.612353');
INSERT INTO permissions (id, name, description, created_at, updated_at) VALUES (13, 'view_inventory', 'View inventory', '2026-03-26 13:50:22.612353', '2026-03-26 13:50:22.612354');
INSERT INTO permissions (id, name, description, created_at, updated_at) VALUES (14, 'manage_inventory', 'Manage inventory', '2026-03-26 13:50:22.612354', '2026-03-26 13:50:22.612354');
INSERT INTO permissions (id, name, description, created_at, updated_at) VALUES (15, 'view_stock_alerts', 'View stock alerts', '2026-03-26 13:50:22.612355', '2026-03-26 13:50:22.612355');
INSERT INTO permissions (id, name, description, created_at, updated_at) VALUES (16, 'manage_suppliers', 'Manage suppliers', '2026-03-26 13:50:22.612355', '2026-03-26 13:50:22.612356');
INSERT INTO permissions (id, name, description, created_at, updated_at) VALUES (17, 'view_reports', 'View reports', '2026-03-26 13:50:22.612356', '2026-03-26 13:50:22.612356');
INSERT INTO permissions (id, name, description, created_at, updated_at) VALUES (18, 'view_analytics', 'View analytics', '2026-03-26 13:50:22.612357', '2026-03-26 13:50:22.612357');
INSERT INTO permissions (id, name, description, created_at, updated_at) VALUES (19, 'manage_roles', 'Manage roles', '2026-03-26 13:50:22.612357', '2026-03-26 13:50:22.612358');
INSERT INTO permissions (id, name, description, created_at, updated_at) VALUES (20, 'manage_permissions', 'Manage permissions', '2026-03-26 13:50:22.612358', '2026-03-26 13:50:22.612358');
INSERT INTO permissions (id, name, description, created_at, updated_at) VALUES (21, 'view_categories', 'View categories', '2026-03-26 13:50:22.612359', '2026-03-26 13:50:22.612359');
INSERT INTO permissions (id, name, description, created_at, updated_at) VALUES (22, 'manage_categories', 'Manage categories', '2026-03-26 13:50:22.612359', '2026-03-26 13:50:22.612360');

-- ROLES TABLE DATA
INSERT INTO roles (id, name, description, is_default, created_at, updated_at) VALUES (1, 'admin', 'Administrator with all permissions', FALSE, '2026-03-26 13:50:22.653047', '2026-03-26 13:50:22.653049');
INSERT INTO roles (id, name, description, is_default, created_at, updated_at) VALUES (2, 'manager', 'Store manager', FALSE, '2026-03-26 13:51:42.228289', '2026-03-26 13:51:42.228291');
INSERT INTO roles (id, name, description, is_default, created_at, updated_at) VALUES (3, 'staff', 'Store staff', FALSE, '2026-03-26 13:51:42.228292', '2026-03-26 13:51:42.228292');
INSERT INTO roles (id, name, description, is_default, created_at, updated_at) VALUES (4, 'customer', 'Customer role', TRUE, '2026-03-26 13:51:42.231527', '2026-03-26 13:51:42.231530');

-- USERS TABLE DATA
INSERT INTO users (id, username, email, hashed_password, first_name, last_name, phone, address, city, state, zip_code, country, is_active, is_staff, is_superuser, created_at, updated_at, role_id) VALUES (1, 'admin', 'admin@university-of-suffolk.ac.uk', 'b.T5o1Q0J8qgJ4E.w2qQ2O6qQqQ.q2y1y5m2o5z5z5z5z5z5z5z5z', 'System', 'Administrator', NULL, NULL, NULL, NULL, NULL, NULL, TRUE, TRUE, NULL, '2026-03-26 13:51:17.197288', '2026-03-26 13:51:17.197288', 1);

-- CATEGORIES TABLE DATA
INSERT INTO categories (id, name, slug, description, image, is_active, created_at, updated_at) VALUES (2, 'Mugs', 'mugs', 'University Mugs', '', TRUE, '2026-03-26 13:52:19.687173', '2026-03-26 13:52:19.687176');

-- PRODUCTS TABLE DATA
INSERT INTO products (id, name, slug, description, price, compare_price, stock, sku, is_featured, is_active, weight, image, created_at, updated_at, category_id) VALUES (2, 'Official University Mug - Black', 'official-university-mug---black', 'Official University of Suffolk branded mug', 12.99, 0.00, 50, 'UOS-MUG-BLK-001', FALSE, TRUE, 0.00, '', '2026-03-26 13:52:53.650954', '2026-03-26 13:52:53.650957', 2);
INSERT INTO products (id, name, slug, description, price, compare_price, stock, sku, is_featured, is_active, weight, image, created_at, updated_at, category_id) VALUES (3, 'Official University Mug - White', 'official-university-mug---white', 'Official University of Suffolk branded mug', 12.99, 0.00, 35, 'UOS-MUG-WHT-001', FALSE, TRUE, 0.00, '', '2026-03-26 13:52:53.655699', '2026-03-26 13:52:53.655704', 2);
INSERT INTO products (id, name, slug, description, price, compare_price, stock, sku, is_featured, is_active, weight, image, created_at, updated_at, category_id) VALUES (4, 'University Logo Ceramic Mug', 'university-logo-ceramic-mug', 'Ceramic mug featuring University of Suffolk logo', 14.99, 0.00, 25, 'UOS-MUG-CRC-001', FALSE, TRUE, 0.00, '', '2026-03-26 13:52:53.663285', '2026-03-26 13:52:53.663290', 2);
INSERT INTO products (id, name, slug, description, price, compare_price, stock, sku, is_featured, is_active, weight, image, created_at, updated_at, category_id) VALUES (5, 'Graduation Commemorative Mug', 'graduation-commemorative-mug', 'Special edition mug for graduates', 19.99, 0.00, 15, 'UOS-MUG-GRD-001', FALSE, TRUE, 0.00, '', '2026-03-26 13:52:53.668768', '2026-03-26 13:52:53.668773', 2);
INSERT INTO products (id, name, slug, description, price, compare_price, stock, sku, is_featured, is_active, weight, image, created_at, updated_at, category_id) VALUES (6, 'Coffee & Study Mug', 'coffee--study-mug', 'Perfect companion for studying at University of Suffolk', 11.99, 0.00, 40, 'UOS-MUG-STU-001', FALSE, TRUE, 0.00, '', '2026-03-26 13:52:53.672532', '2026-03-26 13:52:53.672535', 2);

-- SUPPLIERS TABLE DATA
INSERT INTO suppliers (id, name, contact_name, email, phone, address, city, state, zip_code, country, is_active, notes, created_at, updated_at) VALUES (1, 'University Merchandise Co.', 'Merchandise Manager', 'orders@university-merch.com', '+44 1473 123456', 'University of Suffolk Campus, Ipswich', 'Ipswich', '', '', 'United States', TRUE, 'Official supplier for University of Suffolk merchandise', '2026-03-26 13:53:14.787695', '2026-03-26 13:53:14.787697');

-- STOCK_ITEMS TABLE DATA
INSERT INTO stock_items (id, product_id, current_quantity, reserved_quantity, available_quantity, min_stock_level, max_stock_level, unit_cost, last_updated, last_count_date, notes) VALUES (1, 2, 50, 0, 50, 10, 100, 5.20, '2026-03-26 13:52:53.658276', NULL, '');
INSERT INTO stock_items (id, product_id, current_quantity, reserved_quantity, available_quantity, min_stock_level, max_stock_level, unit_cost, last_updated, last_count_date, notes) VALUES (2, 3, 35, 0, 35, 10, 100, 5.20, '2026-03-26 13:52:53.664981', NULL, '');
INSERT INTO stock_items (id, product_id, current_quantity, reserved_quantity, available_quantity, min_stock_level, max_stock_level, unit_cost, last_updated, last_count_date, notes) VALUES (3, 4, 25, 0, 25, 10, 100, 6.00, '2026-03-26 13:52:53.669726', NULL, '');
INSERT INTO stock_items (id, product_id, current_quantity, reserved_quantity, available_quantity, min_stock_level, max_stock_level, unit_cost, last_updated, last_count_date, notes) VALUES (4, 5, 15, 0, 15, 10, 100, 8.00, '2026-03-26 13:52:53.673383', NULL, '');
INSERT INTO stock_items (id, product_id, current_quantity, reserved_quantity, available_quantity, min_stock_level, max_stock_level, unit_cost, last_updated, last_count_date, notes) VALUES (5, 6, 40, 0, 40, 10, 100, 4.80, '2026-03-26 13:52:53.674774', NULL, '');

COMMIT;

-- End of Mugnificent Database Initialization Script