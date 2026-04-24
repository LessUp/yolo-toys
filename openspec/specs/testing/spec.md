## Purpose

Define acceptance criteria for API behavior validation.

---

### Requirement: REST API Inference

The system MUST support inference for detection, segmentation, and pose tasks via `/infer` endpoint.

#### Scenario: Successful detection inference
Given: A valid image file
When: POST to `/infer` with model=yolov8n.pt and conf=0.25
Then: Response status is 200, contains width, height, task="detect", detections array, inference_time, model

#### Scenario: Detection with custom confidence threshold
Given: A valid image file
When: POST to `/infer` with conf=0.8
Then: All detection scores are >= 0.8

#### Scenario: Segmentation inference
Given: A valid image file
When: POST to `/infer` with model=yolov8n-seg.pt
Then: Response task is "segment", detections contain polygons field

#### Scenario: Pose estimation inference
Given: A valid image file with a person
When: POST to `/infer` with model=yolov8n-pose.pt
Then: Response task is "pose", detections contain keypoints with x, y, confidence

#### Scenario: Model not found error
Given: A valid image but unknown model ID
When: POST to `/infer`
Then: Response status is 404 with detail message

#### Scenario: Invalid image format error
Given: An invalid file (not an image)
When: POST to `/infer`
Then: Response status is 400

---

### Requirement: Open-Vocabulary Detection

The system MUST support text-query based detection.

#### Scenario: OWL-ViT with text queries
Given: A valid image and text_queries="cat, dog, person"
When: POST to `/infer` with model=google/owlvit-base-patch32
Then: Response contains detections matching text queries

#### Scenario: Grounding DINO with text queries
Given: A valid image and text_queries
When: POST to `/infer` with model=IDEA-Research/grounding-dino-tiny
Then: Response contains detections for specified objects

---

### Requirement: Image Captioning API

The system MUST provide `/caption` endpoint for image captioning.

#### Scenario: Successful caption generation
Given: A valid image file
When: POST to `/caption`
Then: Response status is 200, contains caption string, inference_time, model

#### Scenario: Caption with default model
Given: A valid image file
When: POST to `/caption` without model parameter
Then: Response contains caption using default model

---

### Requirement: Visual Question Answering API

The system MUST provide `/vqa` endpoint for answering questions about images.

#### Scenario: Successful VQA inference
Given: A valid image file and question="What color is the car?"
When: POST to `/vqa`
Then: Response contains answer string, question, inference_time, model

#### Scenario: VQA without question returns error
Given: A valid image file without question parameter
When: POST to `/vqa`
Then: Response status is 422 (validation error)

---

### Requirement: Health Check API

The system MUST provide `/health` endpoint for service monitoring.

#### Scenario: Health check returns system info
Given: The server is running
When: GET to `/health`
Then: Response status is 200, contains status="ok", version, device, default_model, defaults

---

### Requirement: Model Discovery API

The system MUST provide endpoints to list and query models.

#### Scenario: List all models
Given: The server is running
When: GET to `/models`
Then: Response status is 200, contains categories with name and models array

#### Scenario: Get specific model details
Given: A valid model_id
When: GET to `/models/yolov8n.pt`
Then: Response contains id, category, name, task

#### Scenario: Get non-existent model returns 404
Given: An unknown model_id
When: GET to `/models/unknown-model`
Then: Response status is 404 with detail message

---

### Requirement: Model Labels API

The system MUST provide `/labels` endpoint for class labels.

#### Scenario: Get labels for default model
Given: The server is running
When: GET to `/labels`
Then: Response status is 200, contains model and labels array

---

### Requirement: Repository health validation SHALL be reproducible
The project MUST provide a reproducible repository-health validation path that covers engineering entry points, linting behavior, tests, and other archive-readiness checks required by the normalized workflow.

#### Scenario: Running the repository validation flow
- **WHEN** a contributor follows the documented repository validation commands
- **THEN** the commands execute in a predictable order with explicit prerequisites and clearly reveal whether the repository is ready to merge or finalize

### Requirement: Finalization changes SHALL include a bug sweep
The project MUST require a final bug sweep for repository-wide normalization changes before they are considered complete.

#### Scenario: Closing a large cleanup change
- **WHEN** a repository-wide cleanup or archive-readiness change reaches its final phase
- **THEN** the workflow includes an explicit bug sweep that checks remaining correctness issues across code, docs, automation, and public project surfaces
