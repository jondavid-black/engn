Feature: Data Type Extension
  As a developer
  I want to define data types that extend other data types
  So that I can reuse existing schemas and create hierarchical data models

  Scenario: Define a child type that extends a base type
    Given a temporary directory for data storage
    When I define a data type "BasePerson" with properties
      | name | type | presence |
      | id   | int  | required |
      | name | str  | required |
    And I define a child data type "Employee" extending "BasePerson" with properties
      | name     | type | presence |
      | role     | str  | required |
      | salary   | int  | optional |
    Then the "Employee" type should extend "BasePerson"
    And the "Employee" type should have property "role"
    And the "Employee" type should have property "salary"
    
    # Note: The actual validation of inherited properties happens during model generation (runtime),
    # not strictly in the TypeDef structure itself (which only holds declared properties).
    # But we can verify the 'extends' field is set correctly.
