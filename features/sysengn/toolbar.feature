Feature: SysEngn Toolbar
  As a user of SysEngn
  I want to see a toolbar with a logo and navigation tabs
  So that I can navigate between different work domains

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
