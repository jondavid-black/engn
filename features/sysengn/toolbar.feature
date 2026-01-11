Feature: SysEngn Toolbar
  As a user of SysEngn
  I want to see a toolbar with a logo and navigation tabs
  So that I can navigate between different work domains

  # Component-level tests (fast, no browser needed)
  Scenario: Toolbar displays application logo
    Given the SysEngn toolbar component is initialized
    Then the toolbar should contain a logo image
    And the logo should use the engn logo asset

  Scenario: Toolbar displays navigation tabs
    Given the SysEngn toolbar component is initialized
    Then the toolbar should have 4 navigation tabs
    And the tabs should be labeled "Home, MBSE, UX, Docs"

  Scenario: Tab selection triggers callback
    Given the SysEngn toolbar component is initialized
    When I simulate selecting tab index 2
    Then the tab change callback should be invoked with index 2

  Scenario: Toolbar uses standalone navigation component
    Given the SysEngn toolbar component is initialized
    Then the navigation tabs should be a standalone flet control
    And the navigation tabs should not require a parent container

  # UI tests (requires browser via playwright)
  @ui
  Scenario: Toolbar renders in browser without errors
    Given the SysEngn app is running in the browser
    Then no error messages should be displayed
    And the logo should be visible in the browser
    And all navigation tabs should be visible

  @ui @skip
  Scenario: Tab navigation works in browser
    # Given the SysEngn app is running in the browser
    # When I click on the "MBSE" tab
    # Then the MBSE view content should be displayed

