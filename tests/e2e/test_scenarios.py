"""
End-to-End Test Scenarios for Mugnificent

This file documents the test scenarios based on the user story.
Run these tests after seeding the database.
"""
from dataclasses import dataclass


@dataclass
class TestScenario:
    """Test scenario definition"""
    name: str
    user_role: str
    steps: list
    expected_result: str


# Test Scenarios based on User Story
SCENARIOS = [
    # Scenario 1: Staff views forecasting dashboard
    TestScenario(
        name="Staff views forecasting recommendations",
        user_role="warehouse",
        steps=[
            "1. Login as warehouse staff",
            "2. Navigate to Stock Forecasting",
            "3. View dashboard showing products needing attention",
            "4. Click on product to see 30-day forecast",
            "5. Verify seasonal patterns are applied"
        ],
        expected_result="Dashboard shows products with stock levels, predicted demand, and recommended order dates"
    ),
    
    # Scenario 2: Staff configures seasonal patterns
    TestScenario(
        name="Staff configures seasonal patterns for university intake",
        user_role="warehouse",
        steps=[
            "1. Login as warehouse staff",
            "2. Go to Stock Forecasting > Seasonal Patterns",
            "3. Select a product",
            "4. Set September multiplier to 2.0 (intake season)",
            "5. Save patterns",
            "6. Verify forecast shows increased demand for September"
        ],
        expected_result="Seasonal patterns saved and reflected in forecast"
    ),
    
    # Scenario 3: Enable auto-order
    TestScenario(
        name="Staff enables auto-stock ordering",
        user_role="manager",
        steps=[
            "1. Login as manager",
            "2. Go to Stock Forecasting > Auto-Order Settings",
            "3. Enable auto-order for a product",
            "4. Set minimum stock threshold to 15",
            "5. Set order quantity to 50",
            "6. Save settings"
        ],
        expected_result="Auto-order settings saved, system will create purchase orders when stock falls below threshold"
    ),
    
    # Scenario 4: Customer places order
    TestScenario(
        name="Customer places order and stock is deducted",
        user_role="customer",
        steps=[
            "1. Login as student customer",
            "2. Browse products",
            "3. Add UoS Classic Mug to cart",
            "4. Complete checkout",
            "5. Verify order confirmation"
        ],
        expected_result="Order created, stock deducted, sales recorded for forecasting"
    ),
    
    # Scenario 5: Low stock triggers auto-refill
    TestScenario(
        name="Low stock triggers automatic refill request",
        user_role="system",
        steps=[
            "1. System detects stock below reorder level",
            "2. Restock alert created automatically",
            "3. Refill request generated",
            "4. Manager notified"
        ],
        expected_result="Refill request created with pending status"
    ),
    
    # Scenario 6: Manager approves refill
    TestScenario(
        name="Manager approves refill request",
        user_role="manager",
        steps=[
            "1. Login as manager",
            "2. Go to Inventory ML > Refill Requests",
            "3. View pending refill requests",
            "4. Click approve",
            "5. Status changes to approved"
        ],
        expected_result="Refill request approved and ready for ordering"
    ),
    
    # Scenario 7: Staff records received stock
    TestScenario(
        name="Staff records received stock",
        user_role="warehouse",
        steps=[
            "1. Login as warehouse staff",
            "2. Go to Inventory ML > Refill Requests",
            "3. Find ordered refill",
            "4. Click Receive",
            "5. Enter quantity received",
            "6. Confirm"
        ],
        expected_result="Stock added to inventory, alert resolved"
    ),
    
    # Scenario 8: Admin manages users
    TestScenario(
        name="Admin manages user roles",
        user_role="admin",
        steps=[
            "1. Login as admin",
            "2. Go to Admin Dashboard",
            "3. View users",
            "4. Change user role",
            "5. Verify permissions updated"
        ],
        expected_result="User permissions updated correctly"
    ),
]


def print_test_guide():
    """Print test guide for manual testing"""
    print("=" * 70)
    print("MUGNIFICENT E2E TEST GUIDE")
    print("=" * 70)
    
    print("\nQUICK START:")
    print("-" * 70)
    print("1. Seed database:")
    print("   cd backend")
    print("   python -m app.seed_data")
    print()
    print("2. Start application:")
    print("   docker-compose up -d")
    print()
    print("3. Access app at http://localhost")
    
    print("\n\nTEST SCENARIOS:")
    print("-" * 70)
    
    for i, scenario in enumerate(SCENARIOS, 1):
        print(f"\n{i}. {scenario.name}")
        print(f"   User Role: {scenario.user_role}")
        print(f"   Steps:")
        for step in scenario.steps:
            print(f"      {step}")
        print(f"   Expected: {scenario.expected_result}")
    
    print("\n\nCREDENTIALS:")
    print("-" * 70)
    print("| Role       | Username   | Password   |")
    print("|------------|------------|------------|")
    print("| Admin      | admin      | admin123   |")
    print("| Manager    | manager    | manager123 |")
    print("| Warehouse  | warehouse  | warehouse123|")
    print("| Customer   | student1   | student123 |")
    print("| Customer   | alumni1    | alumni123  |")
    
    print("\n\nKEY TESTING POINTS:")
    print("-" * 70)
    print("""
1. FORECASTING
   - Sep 2026 should show HIGH demand (2.0x multiplier)
   - January/February should show LOW demand (0.3x)
   
2. AUTO-ORDER
   - When stock < threshold, auto-create PO
   - Check /api/v1/forecasting/auto-order/process
   
3. SALES RECORDING
   - After order: check /api/v1/inventory-ml/predictions
   - Stock should decrease, sales history should update
   
4. SECURITY
   - Non-staff cannot access /forecasting
   - Non-staff cannot access /inventory-ml
   - Non-admin cannot access /admin
""")


if __name__ == "__main__":
    print_test_guide()
