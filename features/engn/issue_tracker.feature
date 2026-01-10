Feature: Issue Tracker Integration
  As a developer
  I want to interact with the issue tracker programmatically
  So that I can automate issue management workflows

  Scenario: Create and list a task
    Given the beads issue tracker is initialized
    When I create a new task with title "Test BDD Task"
    And I list open issues
    Then I should see an issue with title "Test BDD Task" in the list

  Scenario: Add a comment to an issue
    Given the beads issue tracker is initialized
    And a task exists with title "Comment Test Task"
    When I add a comment "This is a test comment" to the task
    Then the task should have a comment "This is a test comment"

  Scenario: Update issue status
    Given the beads issue tracker is initialized
    And a task exists with title "Status Test Task"
    When I update the task status to "in_progress"
    Then the task status should be "in_progress"
