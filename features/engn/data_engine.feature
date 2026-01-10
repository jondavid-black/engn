Feature: Data Engine Storage
  As a developer
  I want to define and store structured data using schemas
  So that I can manage application data reliably

  Scenario: Define and persist a data type
    Given a temporary directory for data storage
    When I define a data type "UserProfile" with properties
      | name  | type | presence |
      | email | str  | required |
      | age   | int  | optional |
    And I save the "UserProfile" type definition to "types.jsonl"
    Then the file "types.jsonl" should exist
    And reading "types.jsonl" should return the type "UserProfile"

  Scenario: Define and persist an enumeration
    Given a temporary directory for data storage
    When I define an enumeration "UserRole" with values "admin, user, guest"
    And I save the "UserRole" enum definition to "enums.jsonl"
    Then the file "enums.jsonl" should exist
    And reading "enums.jsonl" should return the enum "UserRole"
