Feature: Initialize Engn Project
  As a user
  I want to initialize a new engn project
  So that I can start managing my engineering data

  Scenario: Initialize in current directory
    Given the engn application is installed
    When I run "engn proj init"
    Then a file named "engn.toml" should exist
    And a directory named "arch" should exist
    And a directory named "pm" should exist
    And a directory named "ux" should exist
    And the file "engn.toml" should contain "sysengn"
    And a directory named ".beads" should exist


  Scenario: Initialize in a specific directory
    Given I create a temporary directory named "test_project"
    When I run "engn proj init test_project"
    Then a file named "test_project/engn.toml" should exist
    And a directory named "test_project/arch" should exist
    And a directory named "test_project/pm" should exist
    And a directory named "test_project/ux" should exist
    And a directory named "test_project/.beads" should exist

