Feature: Project Branching
  As a developer
  I want to manage branches within a project
  So that I can work on features in isolation

  Scenario: Create and switch to a new branch
    Given I have a project named "my-branch-project"
    When I create a branch named "feature-login" in "my-branch-project"
    Then the active branch for "my-branch-project" should be "feature-login"
    And "feature-login" should be in the list of branches for "my-branch-project"

  Scenario: Delete a branch
    Given I have a project named "my-cleanup-project"
    And I have a branch named "old-feature" in "my-cleanup-project"
    When I checkout the "main" branch in "my-cleanup-project"
    And I delete the branch "old-feature" in "my-cleanup-project"
    Then "old-feature" should not be in the list of branches for "my-cleanup-project"
