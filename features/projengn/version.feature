Feature: ProjEngn CLI Version
  Scenario: Check version
    Given the projengn application is installed
    When I run "projengn --version"
    Then the output should contain the version number
