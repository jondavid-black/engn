Feature: SysEngn CLI Version
  Scenario: Check version
    Given the sysengn application is installed
    When I run "sysengn --version"
    Then the output should contain the version number
