# User Manual - Mugnificent E-Commerce Platform

## Table of Contents
- [Getting Started](#getting-started)
- [User Authentication](#user-authentication)
- [Product Management](#product-management)
- [Inventory Management](#inventory-management)
- [Forecasting Dashboard](#forecasting-dashboard)
- [Order Management](#order-management)
- [Admin Functions](#admin-functions)
- [RBAC Management](#rbac-management)
- [Delivery Tracking](#delivery-tracking)
- [Troubleshooting](#troubleshooting)

## Getting Started

Welcome to the Mugnificent E-Commerce Platform! This system helps the University of Suffolk manage mug inventory with AI-powered forecasting and automated reordering.

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection
- Valid user account (provided by administrator)

### First Login
1. Navigate to the application URL
2. Click on "Sign In" or navigate to `/auth/login`
3. Enter your username/email and password
4. Click "Sign In"
5. You will be redirected to your dashboard

## User Authentication

### Registering a New Account
1. Click "Sign Up" on the login page
2. Fill in the registration form:
   - Username (3-50 alphanumeric characters)
   - Email address
   - Password (at least 8 characters with complexity)
   - First name and last name
   - Phone number (optional)
3. Click "Register"
4. Check your email for activation link
5. Return to login page and sign in

### Logging In
1. Navigate to the login page
2. Enter your username or email
3. Enter your password
4. Click "Sign In"
5. You will be redirected to your dashboard

### Password Recovery
1. Click "Forgot Password?" on the login page
2. Enter your email address
3. Check your email for reset link
4. Click the link and follow instructions to reset your password

### Profile Management
1. Click on your profile icon/name in the top right
2. Select "Profile" from the dropdown menu
3. Update your personal information
4. Click "Save Changes" to save your updates

## Product Management

### Viewing Products
1. Navigate to "Products" in the main menu
2. Browse all available products
3. Use search to find specific items
4. Filter by category or availability

### Product Details
1. Click on any product name/image
2. View detailed information including:
   - Product name and description
   - Price and comparison price
   - Current stock level
   - Product image

## Inventory Management

### Inventory Dashboard
1. Navigate to "Inventory" > "Dashboard"
2. View overall inventory status including:
   - Total products in system
   - Products needing attention (low stock)
   - Low stock alerts
   - Out of stock items
   - Recent stock movements

### Product Inventory
1. Go to "Inventory" > "Products"
2. View current stock levels for all products
3. Filter by stock thresholds or categories
4. Identify products that need immediate attention

### Inventory Alerts
1. Navigate to "Inventory" > "Alerts"
2. View all current inventory alerts
3. Alerts indicate when stock falls below configured thresholds
4. Each alert shows:
   - Product name
   - Current stock level
   - Threshold value
   - Date created
5. Resolve alerts when appropriate action is taken

### Stock Adjustments
1. Go to "Inventory" > "Stock Management"
2. Locate the product you want to adjust
3. Enter adjustment details:
   - Product ID
   - Quantity change (+ for addition, - for removal)
   - Movement type (e.g., "in", "out", "adjustment")
   - Notes about the adjustment
4. Click "Adjust Stock" to record the change

## Forecasting Dashboard

### Accessing Forecasting
1. Navigate to "Forecasting" in the main menu
2. Landing on the forecasting dashboard
3. View overall forecasting performance metrics

### Dashboard Overview
The dashboard displays:
- **Total Products**: Count of all tracked products
- **Products Needing Attention**: Items that require immediate forecasting consideration
- **Total Forecasts Generated**: Historical count of forecasts
- **Average Accuracy**: Overall forecasting accuracy percentage
- **Product-Specific Forecasts**: Detailed information about each product's forecast

### Product Forecast Detail
1. Click on any product in the dashboard
2. View detailed forecast including:
   - Current stock level
   - Average daily sales
   - Total predicted demand
   - Estimated stock depletion date
   - Recommended order date
   - Detailed daily forecasts with confidence intervals
   - Seasonal pattern multipliers applied to the forecast

### Seasonal Pattern Configuration
1. Go to "Forecasting" > "Seasonal Patterns"
2. View or edit seasonal multipliers for each month
3. Adjust factors based on known seasonal fluctuations (academic calendar)
4. Save changes to apply new patterns

### Auto-Order Settings
1. Navigate to "Forecasting" > "Auto-Order Settings"
2. Configure automatic ordering for specific products:
   - Enable/disable auto-ordering
   - Set minimum stock threshold
   - Configure order quantity
   - Review current stock levels and trends
3. Changes apply immediately to future auto-order decisions

## Order Management

### Viewing Orders
1. Go to "Orders" in the main menu
2. View all orders for your account (customers) or all orders (staff/admin)
3. Filter by status: pending, shipped, delivered, cancelled
4. Sort by date, customer, or order total

### Order Details
1. Click on an order number
2. View complete order information including:
   - Order number and status
   - Customer information
   - Shipping address
   - Order items with quantities and prices
   - Subtotal, tax, shipping, and total costs
   - Order date and any relevant timestamps

### Processing Orders (Staff Only)
Staff users can update order status:
1. Go to "Orders" > "Manage Orders"
2. Select an order to process
3. Update status as needed:
   - Pending → Shipped: When order ships
   - Shipped → Delivered: When delivered to customer
   - Pending → Cancelled: If order is cancelled

## Admin Functions

### Admin Dashboard
Admin users have access to additional analytics and management features:
1. Navigate to "Admin" > "Dashboard"
2. View comprehensive business metrics:
   - Sales trends over time
   - Top-selling products
   - Revenue analysis
   - Order processing statistics
   - Inventory performance metrics

### User Management (Admin Only)
1. Go to "Admin" > "Users"
2. View all registered users
3. Manage user roles and permissions
4. Activate/deactivate accounts
5. Reset user passwords if needed

### Product Management (Admin Only)
1. Navigate to "Admin" > "Products"
2. Create, update, or delete products
3. Manage product categories
4. Update inventory levels
5. Set product visibility and pricing

## RBAC Management

### Role-Based Access Control
The system implements role-based permissions:
- **Anonymous Users**: Browse products, create account
- **Customers**: Purchase products, view orders, manage profile
- **Staff**: All customer functions plus inventory management, order processing
- **Admins**: Complete system access including user management and configuration

### Managing Roles (Admin Only)
1. Go to "Admin" > "RBAC" > "Role Management"
2. View all available roles and permissions
3. Assign roles to users as needed
4. Customize permission sets for specific needs

### Setting Staff Status (Admin Only)
1. Navigate to "Admin" > "Users"
2. Find the user to promote/demote
3. Toggle "Staff" status as appropriate
4. Staff members gain additional inventory and order management capabilities

## Delivery Tracking

### Creating Shipments
1. Go to "Delivery" > "Create Shipment"
2. Select the order to ship
3. Choose delivery provider
4. Generate tracking information
5. Print/communicate tracking to customer

### Tracking Packages
1. Navigate to "Delivery" > "Track Package"
2. Enter tracking number
3. View current status and location
4. Check estimated delivery date

### Managing Delivery Providers
1. Go to "Delivery" > "Providers"
2. View available delivery options
3. Configure provider settings
4. Set default provider for automated shipments

## Troubleshooting

### Common Issues and Solutions

#### Login Issues
- **Problem**: Cannot log in
- **Solution**: 
  - Verify username/email and password are correct
  - Check if account is activated
  - Use "Forgot Password" to reset if needed

#### Inventory Not Updating
- **Problem**: Stock levels don't update after sales
- **Solution**:
  - Verify transactions are properly recorded
  - Check for system synchronization delays (usually <1 minute)
  - Contact administrator if issue persists

#### Forecasting Issues
- **Problem**: Forecasts seem inaccurate
- **Solution**:
  - Ensure sufficient historical data exists (at least 30 days)
  - Verify seasonal patterns are properly configured
  - Allow time for models to train with new data

#### Payment Problems
- **Problem**: Payment processing fails
- **Solution**:
  - Verify payment information is correct
  - Check internet connection
  - Contact administrator if issue persists

### Getting Help
- **System Administrator**: Contact internal IT support
- **Technical Issues**: Report to development team
- **Forecasting Accuracy**: Contact data science team
- **General Questions**: Reach out to management

### Support Information
- **Emergency Contact**: [Admin Contact]
- **Technical Support**: [Support Email]
- **Documentation**: Available in the application's Help section
- **Training Materials**: Available for new users

## Best Practices

### For Inventory Management
1. Regularly review low stock alerts
2. Adjust seasonal patterns based on observed demand
3. Verify auto-order settings periodically
4. Keep supplier information updated

### For Forecasting
1. Monitor forecast accuracy metrics
2. Investigate significant deviations
3. Update seasonal patterns as needed
4. Review and adjust confidence intervals

### For Order Processing
1. Process orders promptly
2. Update order statuses accurately
3. Communicate with customers about delays
4. Track delivery performance

## Keyboard Shortcuts
- **Ctrl+S**: Save current form/page
- **Ctrl+F**: Global search
- **Ctrl+N**: Create new item
- **Esc**: Close modal popup
- **Tab**: Navigate form controls

## Privacy and Security
- Never share login credentials
- Log out when leaving computer unattended
- Report suspicious activity immediately
- Use strong, unique passwords
- Enable two-factor authentication if available

---

For additional assistance, please contact your system administrator or refer to the detailed technical documentation available in the admin section.