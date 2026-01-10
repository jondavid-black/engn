Feature: Reference Primitive
  As a developer
  I want to define references between data types
  So that I can maintain referential integrity in my data

  Scenario: Define a schema with references
    Given a temporary directory for data storage
    When I define a data type "User" with properties
      | name | type | presence |
      | id   | int  | required |
      | name | str  | required |
    And I define a data type "Post" with properties
      | name    | type         | presence |
      | id      | int          | required |
      | user_id | ref[User.id] | required |
      | content | str          | required |
    And I save the definitions to "schema.jsonl"
    Then the file "schema.jsonl" should exist
    And reading "schema.jsonl" should return the types "User" and "Post"

  Scenario: Validate valid reference
    Given a temporary directory for data storage
    And I have a schema with "User" and "Post" types defined
    When I save a "User" with id 1 and name "Alice" to "data.jsonl"
    And I save a "Post" with id 101, user_id 1, and content "Hello" to "data.jsonl"
    Then reading "data.jsonl" should succeed without errors

  Scenario: Validate invalid reference
    Given a temporary directory for data storage
    And I have a schema with "User" and "Post" types defined
    When I save a "User" with id 1 and name "Alice" to "data.jsonl"
    And I save a "Post" with id 101, user_id 999, and content "Hello" to "data.jsonl"
    Then reading "data.jsonl" should fail with a reference error
