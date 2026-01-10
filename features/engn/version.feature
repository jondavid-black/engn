Feature: Engn CLI Version
  Scenario: Check version
    Given the engn application is installed
    When I run "engn --version"
    Then the output should contain the version number
