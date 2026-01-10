Feature: Project Management and Initialization
  As a user
  I want to manage projects (create, list, delete) and initialize them
  So that I can maintain my engineering workspace

  Scenario: Create, Initialize, Verify, and Delete Project
    Given I use the ProjectManager to create a project from "https://github.com/jondavid-black/engn-test"
    Then the project "engn-test" should be listed in the project list
    When I run "engn init engn-test"
    Then a file named "engn-test/engn.toml" should exist
    And a directory named "engn-test/arch" should exist
    And a directory named "engn-test/pm" should exist
    And a directory named "engn-test/ux" should exist
    When I use the ProjectManager to delete the project "engn-test"
    Then the project "engn-test" should not be listed in the project list
