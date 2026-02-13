/**
 * API 通信层 - REST + WebSocket
 */

/** 构建推理请求 URL */
export function buildInferUrl(p, endpoint = '/infer') {
  const u = new URL(`${p.base}${endpoint}`);
  u.searchParams.set('conf', p.conf);
  u.searchParams.set('iou', p.iou);
  u.searchParams.set('max_det', p.maxDet);
  if (p.device !== 'auto') u.searchParams.set('device', p.device);
  u.searchParams.set('model', p.model);
  u.searchParams.set('imgsz', p.imgsz);
  if (p.half) u.searchParams.set('half', '1');
  if (p.textQueries) u.searchParams.set('text_queries', p.textQueries);
  if (p.question) u.searchParams.set('question', p.question);
  return u;
}

/** 构建 WebSocket URL */
export function buildWsUrl(p) {
  const proto = p.base.startsWith('https') ? 'wss' : 'ws';
  return buildInferUrl({ ...p, base: p.base.replace(/^http(s)?/, proto) }, '/ws');
}

/** 健康检查 */
export async function fetchHealth(base) {
  const res = await fetch(`${base}/health`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

/** 获取模型列表 */
export async function fetchModels(base) {
  const res = await fetch(`${base}/models`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

/** REST 推理 */
export async function postInfer(url, blob) {
  const fd = new FormData();
  fd.append('file', blob, 'f.jpg');
  const res = await fetch(url, { method: 'POST', body: fd });
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
  return res.json();
}

// ------------------------------------------------------------------
// WebSocket 管理
// ------------------------------------------------------------------

export class WsManager {
  constructor() {
    this.ws = null;
    this.ready = false;
    this._onResult = null;
    this._onError = null;
    this._onStatusChange = null;
    this._reconnectTimer = null;
    this._reconnectDelay = 1000;
    this._maxReconnectDelay = 16000;
    this._params = null;
    this._intentionalClose = false;
    this._pingTimer = null;
  }

  /** 注册回调 */
  on(event, fn) {
    if (event === 'result') this._onResult = fn;
    else if (event === 'error') this._onError = fn;
    else if (event === 'status') this._onStatusChange = fn;
    return this;
  }

  /** 连接 */
  connect(params) {
    this.close();
    this._params = params;
    this._intentionalClose = false;
    this._doConnect(params);
  }

  /** 发送帧 */
  send(blob) {
    if (this.ws && this.ready) this.ws.send(blob);
  }

  /** 发送配置更新 */
  sendConfig(payload) {
    if (this.ws && this.ready) {
      this.ws.send(JSON.stringify({ type: 'config', ...payload }));
    }
  }

  /** 关闭 */
  close() {
    this._intentionalClose = true;
    clearTimeout(this._reconnectTimer);
    clearInterval(this._pingTimer);
    try { this.ws?.close(); } catch {}
    this.ws = null;
    this.ready = false;
  }

  _doConnect(params) {
    const url = buildWsUrl(params);
    this.ws = new WebSocket(url);
    this.ws.binaryType = 'arraybuffer';

    this.ws.onopen = () => {
      this.ready = true;
      this._reconnectDelay = 1000;
      this._onStatusChange?.('connected');
      this._startPing();
    };

    this.ws.onmessage = (e) => {
      try {
        const d = JSON.parse(e.data);
        if (d.type === 'result') this._onResult?.(d.data);
        else if (d.type === 'error') this._onError?.(d.detail || '推理错误');
        else if (d.type === 'pong') { /* 心跳响应 */ }
      } catch {}
    };

    this.ws.onclose = () => {
      this.ready = false;
      this.ws = null;
      clearInterval(this._pingTimer);
      if (!this._intentionalClose) {
        this._onStatusChange?.('disconnected');
        this._scheduleReconnect();
      }
    };

    this.ws.onerror = () => {
      this.ready = false;
      this._onStatusChange?.('error');
    };
  }

  _scheduleReconnect() {
    if (this._intentionalClose || !this._params) return;
    this._reconnectTimer = setTimeout(() => {
      this._onStatusChange?.('reconnecting');
      this._doConnect(this._params);
    }, this._reconnectDelay);
    this._reconnectDelay = Math.min(this._reconnectDelay * 2, this._maxReconnectDelay);
  }

  _startPing() {
    clearInterval(this._pingTimer);
    this._pingTimer = setInterval(() => {
      if (this.ws && this.ready) {
        try { this.ws.send(JSON.stringify({ type: 'ping' })); } catch {}
      }
    }, 30000);
  }
}
