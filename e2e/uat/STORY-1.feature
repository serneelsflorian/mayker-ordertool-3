Feature: Admin starts a group order and sets up the menu
  As an admin
  I want to start a group order and configure the restaurant menu
  So that team members can browse and place their selections

  Background:
    Given I open the application at "/"

  Scenario: AC1 – Application bootstraps and redirects to the order page
    When the page loads
    Then I should be redirected to "/order/<uuid>"
    And the restaurant name should be visible in the top bar
    And the order status should read "Group order · Open"

  Scenario: AC2 – Admin adds a menu item with price and category
    Given I am on the order setup page
    When I fill in "Item name" with "Margherita"
    And I fill in "Price (optional)" with "9.99"
    And I fill in "Category (optional)" with "Pizza"
    And I click "Add item"
    Then a menu item row for "Margherita" should be visible
    And the empty-state message should not be shown

  Scenario: AC2 – Admin adds a menu item without a price
    Given I am on the order setup page
    When I fill in "Item name" with "House Salad"
    And I leave "Price (optional)" blank
    And I click "Add item"
    Then a menu item row for "House Salad" should be visible

  Scenario: AC3 – Blank item name shows a validation error
    Given I am on the order setup page
    When I leave "Item name" blank
    And I click "Add item"
    Then an error message should appear below the name field

  Scenario: AC3 – Empty price is accepted (no error)
    Given I am on the order setup page
    When I fill in "Item name" with "Tiramisu"
    And I leave "Price (optional)" blank
    And I click "Add item"
    Then no price error should be shown
    And a menu item row for "Tiramisu" should be visible

  Scenario: AC3 – Non-numeric price shows a validation error
    Given I am on the order setup page
    When I fill in "Item name" with "Espresso"
    And I fill in "Price (optional)" with "abc"
    And I click "Add item"
    Then an error message should appear below the price field

  Scenario: AC4 – Item row displays name, price, and category correctly
    Given I am on the order setup page
    When I add an item "Quattro Formaggi" with price "11.50" and category "Pizza"
    Then the item row should contain "Quattro Formaggi"
    And the item row should contain "11.50"
    And the item row should contain "Pizza"

  Scenario: AC5 – Admin removes a menu item
    Given I am on the order setup page
    And I have added the item "Bruschetta"
    When I click the remove button for "Bruschetta"
    Then the item row for "Bruschetta" should no longer be visible

  Scenario: AC6 – Generate link button is disabled when no items exist
    Given I am on the order setup page with no menu items
    Then the "Generate share link" button should be disabled
    And the helper text "Add at least one menu item first." should be visible

  Scenario: AC6 – Generate link button is enabled after adding an item
    Given I am on the order setup page with no menu items
    When I add the item "Calzone"
    Then the "Generate share link" button should be enabled
    And the helper text should no longer be visible
