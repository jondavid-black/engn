Feature: Check Command
  As a developer
  I want to check the validity of JSONL data files
  So that I can ensure data integrity

  Scenario: Check a single valid file
    Given a file "test_data/valid.jsonl" with content:
      """
      {"engn_type": "enum", "name": "Status", "values": ["active", "inactive"]}
      """
    When I run the "check" command with "test_data/valid.jsonl"
    Then the output should contain "All checks passed!"

  Scenario: Check a single invalid file
    Given a file "test_data/invalid.jsonl" with content:
      """
      {"engn_type": "enum", "name": "Status"}
      """
    When I run the "check" command with "test_data/invalid.jsonl"
    Then the output should contain "Found 1 errors."
    And the output should contain "test_data/invalid.jsonl"
    And the output should contain "Field required"

  Scenario: Check a directory with mixed files
    Given a directory "test_data/mixed"
    And a file "test_data/mixed/valid.jsonl" with content:
      """
      {"engn_type": "enum", "name": "Status", "values": ["active", "inactive"]}
      """
    And a file "test_data/mixed/nested/invalid.jsonl" with content:
      """
      {"engn_type": "type_def"}
      """
    When I run the "check" command with "test_data/mixed"
    Then the output should contain "Found 1 errors."
    And the output should contain "test_data/mixed/nested/invalid.jsonl"

  Scenario: Check default paths from configuration
    Given a file "engn.jsonl" with content:
      """
      {"engn_type": "ProjectConfig", "pm_path": "data_pm"}
      """
    And a directory "data_pm"
    And a file "data_pm/bad.jsonl" with content:
      """
      not valid json
      """
    When I run the "check" command
    Then the output should contain "Found 1 errors."
    And the output should contain "data_pm/bad.jsonl"
