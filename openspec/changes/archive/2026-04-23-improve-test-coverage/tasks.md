# Tasks: Improve Test Coverage

## Implementation Tasks

### Phase 1: Handler Tests (Priority: High)

- [x] **T1: Create test directory structure**
  - Create `tests/test_handlers/` directory
  - Create `tests/test_handlers/__init__.py`
  - Files: `tests/test_handlers/`

- [x] **T2: Add YOLOHandler tests**
  - Test `load()` with valid/invalid model_id
  - Test `infer()` for detection task with mock results
  - Test `infer()` for segmentation task with mock results
  - Test `infer()` for pose task with mock results
  - Test parameter passing (conf, iou, max_det, imgsz, half)
  - Files: `tests/test_handlers/test_yolo_handler.py`
  - Target: YOLOHandler coverage > 60%

- [x] **T3: Add HFHandler tests (DETR, OWL-ViT, Grounding DINO)**
  - Test `load()` for DETR models
  - Test `load()` for OWL-ViT models
  - Test `load()` for Grounding DINO models
  - Test `infer()` with mock pipeline results
  - Test text_queries parameter for open-vocabulary models
  - Files: `tests/test_handlers/test_hf_handler.py`
  - Target: HFHandler coverage > 60%

- [x] **T4: Add BLIPHandler tests (Caption, VQA)**
  - Test `load()` for caption models
  - Test `load()` for VQA models
  - Test `infer()` for caption generation
  - Test `infer()` for VQA with question parameter
  - Test max_tokens parameter
  - Files: `tests/test_handlers/test_blip_handler.py`
  - Target: BLIPHandler coverage > 60%

### Phase 2: WebSocket Tests (Priority: Medium)

- [x] **T5: Add WebSocket error handling tests**
  - Test decode error response
  - Test model not found error
  - Test inference error response
  - Test file size limit error
  - Files: `tests/test_api.py` (extend existing)

- [x] **T6: Add WebSocket edge case tests**
  - Test empty binary frame
  - Test invalid JSON config message
  - Test ping/pong heartbeat
  - Test connection timeout
  - Files: `tests/test_api.py` (extend existing)

### Phase 3: Model Manager Tests (Priority: Medium)

- [x] **T7: Add ModelManager cache tests**
  - Test cache hit scenario
  - Test cache miss and load
  - Test TTL expiration
  - Test cache clear
  - Test concurrent model loading
  - Files: `tests/test_model_manager.py` (new file)

### Phase 4: Configuration & Cleanup (Priority: Low)

- [x] **T8: Update coverage threshold**
  - Update `pyproject.toml` fail_under to 80
  - Ensure all tests pass with new threshold
  - Files: `pyproject.toml`

- [x] **T9: Add shared fixtures to conftest.py**
  - Mock YOLO model fixture
  - Mock HuggingFace pipeline fixture
  - Mock BLIP processor/model fixture
  - Sample test images
  - Files: `tests/conftest.py`

## Execution Order

1. T1 → T2 → T3 → T4 (Handler tests, sequential dependency)
2. T5 → T6 (WebSocket tests, parallel with Phase 1)
3. T7 (Model Manager tests)
4. T9 → T8 (Finalize and update threshold)

## Estimated Effort

- Phase 1: ~2 hours
- Phase 2: ~1 hour
- Phase 3: ~1 hour
- Phase 4: ~30 minutes

**Total**: ~4.5 hours
