Feature: Upload and fetch skills and their settings
  Test all endpoints related to upload and fetch skill settings

  Scenario: A device requests the settings for its skills
    Given an authorized device
    When a device requests the settings for its skills
    Then the request will be successful
    And the settings are returned
    And an E-tag is generated for these settings
    And device last contact timestamp is updated

  # This scenario uses the ETag generated by the first scenario
  Scenario: Device requests skill settings that have not changed since last they were requested
    Given an authorized device
    And a valid device skill E-tag
    When a device requests the settings for its skills
    Then the request will succeed with a "not modified" return code
    And device last contact timestamp is updated

  # This scenario uses the ETag generated by the first scenario
  Scenario: Device requests skill settings that have changed since last they were requested
    Given an authorized device
    And an expired device skill E-tag
    When a device requests the settings for its skills
    Then the request will be successful
    And an E-tag is generated for these settings
    And device last contact timestamp is updated

  Scenario: A device uploads a change to a single skill setting value
    Given an authorized device
    And a valid device skill E-tag
    And skill settings with a new value
    When the device sends a request to update the skill settings
    Then the request will be successful
    And the skill settings are updated with the new value
    And the device skill E-tag is expired
    And device last contact timestamp is updated

  Scenario: A device uploads skill settings with a field deleted from the settings
    Given an authorized device
    And a valid device skill E-tag
    And skill settings with a deleted field
    When the device sends a request to update the skill settings
    Then the request will be successful
    And the field is no longer in the skill settings
    And the device skill E-tag is expired
    And device last contact timestamp is updated

  Scenario: A device requests a skill to be deleted
    Given an authorized device
    When the device requests a skill to be deleted
    Then the request will be successful
    And the skill will be removed from the device skill list
    And device last contact timestamp is updated