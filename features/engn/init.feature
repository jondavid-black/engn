Feature: Initialize Engn Project
  As a user
  I want to initialize a new engn project
  So that I can start managing my engineering data

  Scenario: Initialize in current directory non-interactively
    Given the engn application is installed
    When I run "engn init --name 'Test Project' --language 'SysML v2' --strategy 'unified python'"
    Then a file named "engn.jsonl" should exist
    And a directory named "mbse" should exist
    And a directory named "pm" should exist
    And the file "engn.jsonl" should contain "sysengn_path"
    And a directory named ".beads" should exist


  Scenario: Initialize in a specific directory non-interactively
    Given I create a temporary directory named "test_project"
    When I run "engn init test_project --name 'Test Project' --language 'SysML v2' --strategy 'unified python'"
    Then a file named "test_project/engn.jsonl" should exist
    And a directory named "test_project/mbse" should exist
    And a directory named "test_project/pm" should exist
    And a directory named "test_project/.beads" should exist

