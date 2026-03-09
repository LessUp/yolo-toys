/**
 * YOLO-Toys 增强版前端 - 多模型实时视觉识别
 */
import { buildInferUrl, buildWsUrl } from './js/api.js';
import { setupCamera as initCamera, captureFrame } from './js/camera.js';
import { getColor, drawDetections as drawDetectionsOnCanvas } from './js/draw.js';

const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const startBtn = document.getElementById('start');
const stopBtn = document.getElementById('stop');
const statsEl = document.getElementById('stats');
const emptyState = document.getElementById('emptyState');
const overlayInfo = document.getElementById('overlayInfo');
const captionResult = document.getElementById('captionResult');
const captionLabel = captionResult?.querySelector('.caption-label');
const captionText = document.getElementById('captionText');
const serverInput = document.getElementById('server');
const useWsCb = document.getElementById('useWs');
const quickModelSelect = document.getElementById('quickModelSelect');
const modelTabs = document.getElementById('modelTabs');
const modelList = document.getElementById('modelList');
const customModelInput = document.getElementById('customModel');
const deviceSelect = document.getElementById('device');
const halfCb = document.getElementById('half');
const confInput = document.getElementById('conf');
const iouInput = document.getElementById('iou');
const maxDetInput = document.getElementById('maxDet');
const imgszInput = document.getElementById('imgsz');
const fpsSelect = document.getElementById('fps');
const sendSizeSelect = document.getElementById('sendSize');
const qualitySelect = document.getElementById('quality');
const showBoxesCb = document.getElementById('showBoxes');
const showLabelsCb = document.getElementById('showLabels');
const showMasksCb = document.getElementById('showMasks');
const showKeypointsCb = document.getElementById('showKeypoints');
const showSkeletonCb = document.getElementById('showSkeleton');
const showOverlayCb = document.getElementById('showOverlay');
const maskAlphaInput = document.getElementById('maskAlpha');
const textQueriesInput = document.getElementById('textQueries');
const vqaQuestionInput = document.getElementById('vqaQuestion');
const multimodalSection = document.getElementById('multimodalSection');
const textQueriesGroup = textQueriesInput?.closest('.form-group');
const vqaQuestionGroup = vqaQuestionInput?.closest('.form-group');
const detectionsSidebar = document.getElementById('detectionsSidebar');
const classCountsEl = document.getElementById('classCounts');
const summaryTotalEl = document.getElementById('summaryTotal');
const summaryModelEl = document.getElementById('summaryModel');
const summaryDeviceEl = document.getElementById('summaryDevice');
const summaryTimingEl = document.getElementById('summaryTiming');
const overlayInferTime = document.getElementById('overlayInferTime');
const overlayObjects = document.getElementById('overlayObjects');
const permissionStatus = document.getElementById('permissionStatus');
const imageFileInput = document.getElementById('imageFile');
const inferImageBtn = document.getElementById('inferImage');
const settingsOverlay = document.getElementById('settingsOverlay');
const openSettingsBtn = document.getElementById('openSettings');
const closeSettingsBtn = document.getElementById('closeSettings');
const toggleSidebarBtn = document.getElementById('toggleSidebar');
const themeToggleBtn = document.getElementById('themeToggle');
const versionBadge = document.querySelector('.version-badge');

let running = false, busy = false, detections = [], sendInterval = 200;
let baseUrl = window.location.origin, sendWidth = 640;
let lastInferSize = { width: 1, height: 1 }, lastTask = 'detect';
let ws = null, wsReady = false, currentModel = 'yolov8s.pt', currentCategory = 'yolo_detect';
let modelCategories = {};
let modelIdToCategory = {};
let lastInferErrorToastAt = 0;

const toastContainer = document.getElementById('toastContainer');

const SETTINGS_KEY = 'yolo_toys_v4';

// Toast 通知系统
function showToast(message, type = 'info', duration = 3000) {
  if (!toastContainer) return;
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, duration);
}

// Theme
function setTheme(t) {
  document.documentElement.setAttribute('data-theme', t);
  localStorage.setItem('theme', t);
  const moon = themeToggleBtn?.querySelector('.icon-moon');
  const sun = themeToggleBtn?.querySelector('.icon-sun');
  if (moon) moon.style.display = t === 'light' ? 'none' : 'block';
  if (sun) sun.style.display = t === 'light' ? 'block' : 'none';
}
setTheme(localStorage.getItem('theme') || (matchMedia('(prefers-color-scheme:light)').matches ? 'light' : 'dark'));
themeToggleBtn?.addEventListener('click', () => setTheme(document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light'));

// UI
openSettingsBtn?.addEventListener('click', () => settingsOverlay?.classList.add('open'));
closeSettingsBtn?.addEventListener('click', () => settingsOverlay?.classList.remove('open'));
settingsOverlay?.addEventListener('click', e => e.target === settingsOverlay && settingsOverlay.classList.remove('open'));
toggleSidebarBtn?.addEventListener('click', () => {
  if (!detectionsSidebar) return;
  if (innerWidth <= 768) {
    detectionsSidebar.classList.remove('collapsed');
    detectionsSidebar.classList.toggle('open');
  } else {
    detectionsSidebar.classList.remove('open');
    detectionsSidebar.classList.toggle('collapsed');
  }
});

window.addEventListener('resize', () => {
  if (!detectionsSidebar) return;
  if (innerWidth <= 768) detectionsSidebar.classList.remove('collapsed');
  else detectionsSidebar.classList.remove('open');
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && settingsOverlay?.classList.contains('open')) settingsOverlay.classList.remove('open');
});

// Settings
function loadSettings() { try { return JSON.parse(localStorage.getItem(SETTINGS_KEY) || '{}'); } catch { return {}; } }
function saveSettings(s) { localStorage.setItem(SETTINGS_KEY, JSON.stringify(s)); }

async function refreshHealth(base) {
  if (!versionBadge) return;
  try {
    const res = await fetch(`${base}/health`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    versionBadge.textContent = `v${data.version || '-'}`;
    versionBadge.classList.remove('offline');
    versionBadge.title = `device=${data.device || '-'} | default=${data.default_model || '-'}`;
  } catch {
    versionBadge.textContent = 'offline';
    versionBadge.classList.add('offline');
    versionBadge.title = '后端不可达';
  }
}

function applySettings() {
  const s = loadSettings();
  if (s.server) serverInput.value = s.server;
  if (s.useWs !== undefined) useWsCb.checked = s.useWs;
  if (s.fps) fpsSelect.value = s.fps;
  if (s.sendSize) sendSizeSelect.value = s.sendSize;
  if (s.conf) confInput.value = s.conf;
  if (s.iou) iouInput.value = s.iou;
  if (s.maxDet) maxDetInput.value = s.maxDet;
  if (s.device) deviceSelect.value = s.device;
  if (s.quality) qualitySelect.value = s.quality;
  if (s.imgsz) imgszInput.value = s.imgsz;
  if (s.half !== undefined) halfCb.checked = s.half;
  if (s.showBoxes !== undefined) showBoxesCb.checked = s.showBoxes;
  if (s.showLabels !== undefined) showLabelsCb.checked = s.showLabels;
  if (s.showMasks !== undefined) showMasksCb.checked = s.showMasks;
  if (s.showKeypoints !== undefined) showKeypointsCb.checked = s.showKeypoints;
  if (s.showSkeleton !== undefined) showSkeletonCb.checked = s.showSkeleton;
  if (s.showOverlay !== undefined && showOverlayCb) showOverlayCb.checked = s.showOverlay;
  if (s.maskAlpha) maskAlphaInput.value = s.maskAlpha;
  if (s.model) currentModel = s.model;
  if (s.customModel !== undefined && customModelInput) customModelInput.value = s.customModel;
  if (s.textQueries !== undefined && textQueriesInput) textQueriesInput.value = s.textQueries;
  if (s.vqaQuestion !== undefined && vqaQuestionInput) vqaQuestionInput.value = s.vqaQuestion;
  updateVars();
  updateTaskControls();
}

function updateVars() {
  sendInterval = 1000 / parseInt(fpsSelect?.value || '5');
  sendWidth = parseInt(sendSizeSelect?.value || '640');
  saveSettings({
    server: serverInput?.value, useWs: useWsCb?.checked, fps: fpsSelect?.value, sendSize: sendSizeSelect?.value,
    conf: confInput?.value, iou: iouInput?.value, maxDet: maxDetInput?.value, device: deviceSelect?.value,
    quality: qualitySelect?.value, imgsz: imgszInput?.value, half: halfCb?.checked,
    showBoxes: showBoxesCb?.checked, showLabels: showLabelsCb?.checked, showMasks: showMasksCb?.checked,
    showKeypoints: showKeypointsCb?.checked, showSkeleton: showSkeletonCb?.checked,
    showOverlay: showOverlayCb?.checked, maskAlpha: maskAlphaInput?.value, model: currentModel,
    customModel: customModelInput?.value, textQueries: textQueriesInput?.value, vqaQuestion: vqaQuestionInput?.value
  });

  // WebSocket 运行中动态更新配置（后端支持文本消息 config）
  if (running && useWsCb?.checked && ws && wsReady) {
    try {
      const p = getParams();
      const tq = (p.textQueries || '').split(',').map(s => s.trim()).filter(Boolean);
      const payload = {
        type: 'config',
        model: p.model,
        conf: p.conf,
        iou: p.iou,
        max_det: p.maxDet,
        imgsz: p.imgsz,
        half: !!p.half,
      };
      if (p.device !== 'auto') payload.device = p.device;
      if (tq.length) payload.text_queries = tq;
      if (p.question) payload.question = p.question;
      ws.send(JSON.stringify(payload));
    } catch {}
  }
  updateTaskControls();
}

[fpsSelect, sendSizeSelect, serverInput, customModelInput, confInput, iouInput, maxDetInput, deviceSelect, qualitySelect,
 imgszInput, halfCb, showBoxesCb, showLabelsCb, showMasksCb, showKeypointsCb, showSkeletonCb, showOverlayCb,
 maskAlphaInput, useWsCb, textQueriesInput, vqaQuestionInput].forEach(el => el?.addEventListener('change', updateVars));

customModelInput?.addEventListener('input', () => {
  syncCategoryFromModel();
  renderModels();
  updateTaskControls();
});

serverInput?.addEventListener('change', async () => {
  if (running) {
    showToast('服务地址已变更（运行中需停止后重新启动生效）', 'info');
    return;
  }
  await loadModels();
});

// Models
function getEffectiveModelId() {
  return customModelInput?.value?.trim() || currentModel;
}

function inferBackendCategory(modelId) {
  if (!modelId) return '';
  if (modelIdToCategory[modelId]) return modelIdToCategory[modelId];

  const id = String(modelId).toLowerCase();
  if (id.endsWith('.pt')) {
    if (id.includes('seg')) return 'yolo_segment';
    if (id.includes('pose')) return 'yolo_pose';
    return 'yolo_detect';
  }
  if (id.includes('owlvit')) return 'hf_owlvit';
  if (id.includes('grounding') || id.includes('dino')) return 'hf_grounding_dino';
  if (id.includes('detr')) return 'hf_detr';
  if (id.includes('blip') && id.includes('vqa')) return 'multimodal_vqa';
  if (id.includes('blip') && (id.includes('caption') || id.includes('captioning'))) return 'multimodal_caption';
  return '';
}

function rebuildModelIndex() {
  modelIdToCategory = {};
  Object.entries(modelCategories || {}).forEach(([cat, data]) => {
    data.models?.forEach(m => { modelIdToCategory[m.id] = cat; });
  });
}

function setActiveTab(cat) {
  modelTabs?.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b.dataset.cat === cat));
}

function syncCategoryFromModel() {
  const backendCat = inferBackendCategory(getEffectiveModelId());
  if (backendCat) currentCategory = backendCat.startsWith('multimodal') ? 'multimodal' : backendCat;
  setActiveTab(currentCategory);
}

function updateTaskControls() {
  const backendCat = inferBackendCategory(getEffectiveModelId());
  const showTextQueries =
    currentCategory === 'hf_owlvit' ||
    currentCategory === 'hf_grounding_dino' ||
    backendCat === 'hf_owlvit' ||
    backendCat === 'hf_grounding_dino';
  const showVqaQuestion = backendCat === 'multimodal_vqa';

  const showSection = showTextQueries || showVqaQuestion;
  if (multimodalSection) multimodalSection.style.display = showSection ? '' : 'none';
  if (textQueriesGroup) textQueriesGroup.style.display = showTextQueries ? '' : 'none';
  if (vqaQuestionGroup) vqaQuestionGroup.style.display = showVqaQuestion ? '' : 'none';
}

function setModel(modelId) {
  currentModel = modelId;
  if (customModelInput) customModelInput.value = '';
  syncCategoryFromModel();
  renderModels();
  updateTaskControls();
  updateVars();
}

function setCategory(cat) {
  currentCategory = cat;
  setActiveTab(currentCategory);
  renderModels();
  updateTaskControls();
}

async function loadModels() {
  const base = (serverInput?.value?.trim() || baseUrl).replace(/\/$/, '');
  try {
    const res = await fetch(`${base}/models`);
    const data = await res.json();
    modelCategories = data.categories || {};
  } catch {
    modelCategories = {
      yolo_detect: { name: 'YOLO 检测', models: [{ id: 'yolov8n.pt', name: 'YOLOv8 Nano' }, { id: 'yolov8s.pt', name: 'YOLOv8 Small' }] },
      yolo_segment: { name: '分割', models: [{ id: 'yolov8s-seg.pt', name: 'YOLOv8 Seg' }] },
      yolo_pose: { name: '姿态', models: [{ id: 'yolov8s-pose.pt', name: 'YOLOv8 Pose' }] }
    };
  }
  await refreshHealth(base);
  rebuildModelIndex();
  syncCategoryFromModel();
  renderModels();
  updateTaskControls();
}

function renderModels() {
  if (!modelList || !quickModelSelect) return;
  quickModelSelect.innerHTML = '';
  modelList.innerHTML = '';
  
  // 判断是否应该显示该类别的模型
  const shouldShowCategory = (cat) => {
    if (cat === currentCategory) return true;
    // YOLO 类别相互显示
    if (currentCategory.startsWith('yolo') && cat.startsWith('yolo') && currentCategory === cat) return true;
    // 多模态标签页显示所有多模态类别
    if (currentCategory === 'multimodal' && cat.startsWith('multimodal')) return true;
    // 精确匹配
    return cat === currentCategory;
  };
  
  Object.entries(modelCategories).forEach(([cat, data]) => {
    const grp = document.createElement('optgroup');
    grp.label = data.name;
    data.models?.forEach(m => {
      const opt = document.createElement('option');
      opt.value = m.id; opt.textContent = m.name;
      if (m.id === currentModel) opt.selected = true;
      grp.appendChild(opt);
      
      if (shouldShowCategory(cat)) {
        const item = document.createElement('div');
        item.className = `model-item${m.id === currentModel ? ' selected' : ''}`;
        item.dataset.model = m.id;
        item.setAttribute('role', 'button');
        item.tabIndex = 0;
        item.innerHTML = `<div class="model-item-name">${m.name}</div><div class="model-item-desc">${m.description || ''}</div>${m.speed ? `<div class="model-item-meta"><span>速度: ${m.speed}</span><span>精度: ${m.accuracy || '-'}</span></div>` : ''}`;
        item.onclick = () => { setModel(m.id); showToast(`已选择 ${m.name}`, 'info'); };
        item.onkeydown = (e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            item.click();
          }
        };
        modelList.appendChild(item);
      }
    });
    quickModelSelect.appendChild(grp);
  });
  
  if (!modelList.children.length) {
    modelList.innerHTML = '<div class="empty-hint">此类别暂无可用模型</div>';
  }
}

modelTabs?.querySelectorAll('.tab-btn').forEach(btn => btn.addEventListener('click', () => setCategory(btn.dataset.cat)));

quickModelSelect?.addEventListener('change', () => setModel(quickModelSelect.value));

// Camera
async function setupCamera() {
  try {
    await initCamera(video, canvas);
    showToast('摄像头启动成功', 'success');
  } catch (e) {
    if (e.name === 'NotAllowedError') {
      showToast('摄像头权限被拒绝', 'error');
      if (permissionStatus) { permissionStatus.hidden = false; permissionStatus.textContent = '请在浏览器设置中允许摄像头访问'; permissionStatus.className = 'notice error'; }
    } else if (e.name === 'NotFoundError') {
      showToast('未找到摄像头设备', 'error');
    } else {
      showToast(`摄像头错误: ${e.message}`, 'error');
    }
    throw e;
  }
}

// Drawing
function draw() {
  if (!running) return;
  requestAnimationFrame(draw);
  if (video.srcObject && !video.paused) {
    if (canvas.width !== video.videoWidth) canvas.width = video.videoWidth;
    if (canvas.height !== video.videoHeight) canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);
  }
  drawDetections();
}

function drawDetections() {
  if (!detections?.length) return;
  drawDetectionsOnCanvas(ctx, detections, lastInferSize, {
    showBoxes: showBoxesCb?.checked,
    showLabels: showLabelsCb?.checked,
    showMasks: showMasksCb?.checked,
    showKeypoints: showKeypointsCb?.checked,
    showSkeleton: showSkeletonCb?.checked,
    maskAlpha: parseFloat(maskAlphaInput?.value || '0.3'),
  });
}

// Inference
function getParams() {
  const base = (serverInput?.value?.trim() || baseUrl).replace(/\/$/, '');
  return { base, conf: parseFloat(confInput?.value || '0.25'), iou: parseFloat(iouInput?.value || '0.45'),
    maxDet: parseInt(maxDetInput?.value || '300'), device: deviceSelect?.value || 'auto',
    model: getEffectiveModelId(),
    imgsz: parseInt(imgszInput?.value || '640'),
    half: halfCb?.checked,
    textQueries: textQueriesInput?.value?.trim(),
    question: vqaQuestionInput?.value?.trim(),
  };
}

async function sendFrame() {
  if (!running || busy) return;
  busy = true;
  const t0 = performance.now();
  const quality = parseFloat(qualitySelect?.value || '0.8');
  const blob = await captureFrame(video, sendWidth, quality);
  const p = getParams();
  try {
    if (useWsCb?.checked && ws && wsReady) { ws.send(blob); }
    else {
      const fd = new FormData(); fd.append('file', blob, 'f.jpg');
      const u = buildInferUrl(p);
      const res = await fetch(u, { method: 'POST', body: fd });
      if (res.ok) {
        handleResult(await res.json(), t0, p.device);
      } else {
        const now = Date.now();
        if (now - lastInferErrorToastAt > 3000) {
          let detail = '';
          try {
            const err = await res.json();
            detail = err?.detail ? String(err.detail) : '';
          } catch {}
          showToast(`推理失败: HTTP ${res.status}${detail ? ` - ${detail}` : ''}`, 'error');
          lastInferErrorToastAt = now;
        }
      }
    }
  } catch (e) {
    console.error(e);
    const now = Date.now();
    if (now - lastInferErrorToastAt > 3000) {
      showToast('推理请求失败', 'error');
      lastInferErrorToastAt = now;
    }
  }
  busy = false;
  if (running) setTimeout(sendFrame, sendInterval);
}

function handleResult(data, t0, device) {
  detections = data.detections || [];
  if (data.width && data.height) lastInferSize = { width: data.width, height: data.height };
  const rt = performance.now() - t0, bt = data.inference_time;
  const summary = data.caption ? '图像描述' : (data.answer ? '视觉问答' : `${detections.length} 目标`);
  statsEl.textContent = `推理: ${bt?.toFixed(0) || '-'}ms | RTT: ${rt.toFixed(0)}ms | ${summary}`;
  if (summaryTimingEl) summaryTimingEl.textContent = data.inference_time ? `${data.inference_time.toFixed?.(1)} ms` : '-';
  if (showOverlayCb?.checked && overlayInfo) { overlayInfo.hidden = false; overlayInferTime.textContent = `${bt?.toFixed(0)}ms`; overlayObjects.textContent = detections.length; }
  else if (overlayInfo) overlayInfo.hidden = true;
  if (data.caption) {
    captionResult.hidden = false;
    if (captionLabel) captionLabel.textContent = '图像描述';
    captionText.textContent = data.caption;
  } else if (data.answer) {
    captionResult.hidden = false;
    if (captionLabel) captionLabel.textContent = '视觉问答';
    captionText.textContent = `问题：${data.question || ''}  回答：${data.answer}`;
  } else {
    captionResult.hidden = true;
  }
  const counts = {}; detections.forEach(d => counts[d.label] = (counts[d.label] || 0) + 1);
  classCountsEl.innerHTML = Object.keys(counts).length
    ? Object.entries(counts).sort((a, b) => b[1] - a[1]).map(([c, n]) => `<div class="class-item"><span style="color:${getColor(c)}">${c}</span><span class="count">${n}</span></div>`).join('')
    : '<div class="empty-hint">暂无检测</div>';
}
function initWS() {
  if (!useWsCb?.checked) return;
  const p = getParams();
  const u = buildWsUrl(p);
  ws = new WebSocket(u); ws.binaryType = 'arraybuffer';
  ws.onopen = () => { wsReady = true; showToast('WebSocket 已连接', 'success'); };
  ws.onmessage = e => { 
    try { 
      const d = JSON.parse(e.data); 
      if (d.type === 'result') handleResult(d.data, performance.now(), p.device);
      else if (d.type === 'error') {
        const now = Date.now();
        if (now - lastInferErrorToastAt > 3000) {
          showToast(d.detail || '推理错误', 'error');
          lastInferErrorToastAt = now;
        }
      }
    } catch {} 
  };
  ws.onclose = () => { wsReady = false; ws = null; if (running) showToast('WebSocket 连接断开', 'error'); };
  ws.onerror = () => { wsReady = false; showToast('WebSocket 连接失败', 'error'); };
}
function closeWS() { try { ws?.close(); } catch {} ws = null; wsReady = false; }

// Image Inference
async function runImageInference(file) {
  const p = getParams(), fd = new FormData(); fd.append('file', file);
  const u = buildInferUrl(p);
  statsEl.textContent = '推理中...';
  const t0 = performance.now();
  try {
    const res = await fetch(u, { method: 'POST', body: fd });
    if (!res.ok) {
      let detail = '';
      try {
        const err = await res.json();
        detail = err?.detail ? String(err.detail) : '';
      } catch {
        try { detail = await res.text(); } catch {}
      }
      throw new Error(detail ? `HTTP ${res.status}: ${detail}` : `HTTP ${res.status}`);
    }
    const data = await res.json();
    handleResult(data, t0, p.device);
    const img = new Image();
    img.onload = () => { 
      canvas.width = img.width; canvas.height = img.height; ctx.drawImage(img, 0, 0); 
      drawDetections(); emptyState.style.display = 'none'; 
      if (data.caption) showToast('图像描述已生成', 'success');
      else if (data.answer) showToast('视觉问答已生成', 'success');
      else showToast(`检测到 ${detections.length} 个目标`, 'success');
    };
    img.src = URL.createObjectURL(file);
  } catch (e) { 
    statsEl.textContent = '推理失败'; 
    showToast(`推理失败: ${e.message}`, 'error');
  }
}

// Event Handlers
startBtn?.addEventListener('click', async () => {
  startBtn.disabled = true; startBtn.innerHTML = '<span class="loader"></span> 启动中...';
  try {
    updateVars();
    await loadModels();
    await setupCamera();
    closeWS(); initWS(); running = true; stopBtn.disabled = false; emptyState.style.display = 'none';
    draw(); sendFrame();
  } catch (e) { 
    console.error(e); 
    statsEl.textContent = '启动失败'; 
    showToast(`启动失败: ${e.message || '未知错误'}`, 'error');
  }
  startBtn.disabled = false; startBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg> 开始摄像头';
});

stopBtn?.addEventListener('click', () => {
  running = false; closeWS();
  video.srcObject?.getTracks().forEach(t => t.stop()); video.srcObject = null;
  stopBtn.disabled = true; statsEl.textContent = '就绪'; emptyState.style.display = 'flex';
  ctx.clearRect(0, 0, canvas.width, canvas.height);
});

inferImageBtn?.addEventListener('click', () => { const f = imageFileInput?.files?.[0]; if (f) { if (running) stopBtn.click(); runImageInference(f); } });
imageFileInput?.addEventListener('change', () => { if (imageFileInput.files?.[0]) { if (running) stopBtn.click(); runImageInference(imageFileInput.files[0]); } });

// Init
applySettings();
loadModels();
