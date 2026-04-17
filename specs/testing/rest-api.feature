Feature: REST API Inference
  As a user
  I want to perform inference on images via REST API
  So that I can detect objects in my images

  Background:
    Given the server is running on port 8000
    And the default model is yolov8n.pt

  Scenario: Successful detection inference
    Given I have a valid image file "test.jpg"
    When I send a POST request to "/infer" with:
      | field   | value      |
      | file    | test.jpg   |
      | model   | yolov8n.pt |
      | conf    | 0.25       |
    Then the response status should be 200
    And the response should contain "width"
    And the response should contain "height"
    And the response should contain "task" with value "detect"
    And the response should contain "detections" as an array
    And the response should contain "inference_time"
    And the response should contain "model" with value "yolov8n.pt"

  Scenario: Detection with custom confidence threshold
    Given I have a valid image file "test.jpg"
    When I send a POST request to "/infer" with:
      | field   | value      |
      | file    | test.jpg   |
      | model   | yolov8n.pt |
      | conf    | 0.8        |
    Then the response status should be 200
    And all detection scores should be >= 0.8

  Scenario: Model not found error
    Given I have a valid image file "test.jpg"
    When I send a POST request to "/infer" with:
      | field   | value        |
      | file    | test.jpg     |
      | model   | unknown-model|
    Then the response status should be 404
    And the response should contain "detail"

  Scenario: Invalid image format error
    Given I have an invalid file "test.txt"
    When I send a POST request to "/infer" with:
      | field   | value      |
      | file    | test.txt   |
      | model   | yolov8n.pt |
    Then the response status should be 400

  Scenario: Segmentation inference
    Given I have a valid image file "test.jpg"
    When I send a POST request to "/infer" with:
      | field   | value          |
      | file    | test.jpg       |
      | model   | yolov8n-seg.pt |
    Then the response status should be 200
    And the response should contain "task" with value "segment"
    And detections should contain "polygons" field

  Scenario: Pose estimation inference
    Given I have a valid image file "person.jpg"
    When I send a POST request to "/infer" with:
      | field   | value           |
      | file    | person.jpg      |
      | model   | yolov8n-pose.pt |
    Then the response status should be 200
    And the response should contain "task" with value "pose"
    And detections should contain "keypoints" field
    And each keypoint should have "x", "y", and "confidence"

  Scenario Outline: Open-vocabulary detection with text queries
    Given I have a valid image file "test.jpg"
    When I send a POST request to "/infer" with:
      | field        | value                      |
      | file         | test.jpg                   |
      | model        | <model>                    |
      | text_queries | "cat, dog, person"         |
    Then the response status should be 200
    And the response should contain "detections"

    Examples:
      | model                          |
      | google/owlvit-base-patch32     |
      | IDEA-Research/grounding-dino-tiny |

Feature: Image Captioning API
  As a user
  I want to generate captions for images
  So that I can understand image content

  Scenario: Successful caption generation
    Given I have a valid image file "scene.jpg"
    When I send a POST request to "/caption" with:
      | field   | value                                |
      | file    | scene.jpg                            |
      | model   | Salesforce/blip-image-captioning-base|
    Then the response status should be 200
    And the response should contain "caption" as a string
    And the response should contain "inference_time"
    And the response should contain "model"

  Scenario: Caption with default model
    Given I have a valid image file "scene.jpg"
    When I send a POST request to "/caption" with:
      | field   | value     |
      | file    | scene.jpg |
    Then the response status should be 200
    And the response should contain "caption"

Feature: Visual Question Answering API
  As a user
  I want to ask questions about images
  So that I can get specific information from images

  Scenario: Successful VQA inference
    Given I have a valid image file "car.jpg"
    When I send a POST request to "/vqa" with:
      | field    | value                      |
      | file     | car.jpg                    |
      | question | "What color is the car?"   |
      | model    | Salesforce/blip-vqa-base   |
    Then the response status should be 200
    And the response should contain "answer" as a string
    And the response should contain "question"
    And the response should contain "inference_time"

  Scenario: VQA without question returns error
    Given I have a valid image file "car.jpg"
    When I send a POST request to "/vqa" with:
      | field   | value   |
      | file    | car.jpg |
    Then the response status should be 422

Feature: Health Check API
  As a system administrator
  I want to check server health
  So that I can monitor the service

  Scenario: Health check returns system info
    When I send a GET request to "/health"
    Then the response status should be 200
    And the response should contain "status" with value "ok"
    And the response should contain "version"
    And the response should contain "device"
    And the response should contain "default_model"
    And the response should contain "defaults"

Feature: Model Discovery API
  As a user
  I want to list available models
  So that I can choose the right model for my task

  Scenario: List all models
    When I send a GET request to "/models"
    Then the response status should be 200
    And the response should contain "categories"
    And each category should contain "name" and "models"
    And each model should contain "id", "name", "description"

  Scenario: Get specific model details
    When I send a GET request to "/models/yolov8n.pt"
    Then the response status should be 200
    And the response should contain "id" with value "yolov8n.pt"
    And the response should contain "category"
    And the response should contain "name"
    And the response should contain "task"

  Scenario: Get non-existent model returns 404
    When I send a GET request to "/models/unknown-model"
    Then the response status should be 404
    And the response should contain "detail"

Feature: Model Labels API
  As a user
  I want to get class labels for a model
  So that I can understand detection results

  Scenario: Get labels for default model
    When I send a GET request to "/labels"
    Then the response status should be 200
    And the response should contain "model"
    And the response should contain "labels" as an array

  Scenario: Get labels for specific model
    When I send a GET request to "/labels?model=yolov8s.pt"
    Then the response status should be 200
    And the response should contain "model" with value "yolov8s.pt"
    And the response should contain "labels"
