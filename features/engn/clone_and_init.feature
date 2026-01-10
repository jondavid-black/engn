Feature: Initialize Engn Project in Cloned Repo
  As a user
  I want to initialize an engn project in a cloned repository
  So that I can use engn with existing code

  Scenario: Clone and Initialize
    Given I clone the repository "https://github.com/jondavid-black/engn-test" to "test_repo"
    When I run "engn init test_repo"
    Then a file named "test_repo/engn.toml" should exist
    And a directory named "test_repo/arch" should exist
    And a directory named "test_repo/pm" should exist
    And a directory named "test_repo/ux" should exist
