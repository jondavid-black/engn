Feature: Application Context Management
  As a user of Digital Engine applications
  I want my active project and branch to be maintained across the application
  So that my actions are performed in the correct context

  Scenario: Active project is shared across components
    Given a new application context is initialized
    When I set the active project to "project-a" in the context
    Then the active project in the context should be "project-a"

  Scenario: Components are notified of context changes
    Given a new application context is initialized
    And a component is subscribed to context changes
    When I set the active project to "project-b" in the context
    Then the component should be notified of the change

  Scenario: Toolbar updates context when project is selected
    Given the SysEngn toolbar component is initialized
    When I select project "my-project" in the toolbar dropdown
    Then the application context active project should be "my-project"
