/**
 * 绘制模块 - Canvas 绘制逻辑（检测框、掩膜、关键点、骨架）
 */

const SKELETON = [[0,1],[0,2],[1,3],[2,4],[5,6],[5,7],[7,9],[6,8],[8,10],[5,11],[6,12],[11,12],[11,13],[13,15],[12,14],[14,16]];
const COLORS = ['#ef4444','#f97316','#f59e0b','#84cc16','#22c55e','#06b6d4','#3b82f6','#6366f1','#a855f7','#ec4899'];

/** 根据 label 字符串计算颜色 */
export function getColor(label) {
  let h = 0;
  for (let i = 0; i < label.length; i++) h = label.charCodeAt(i) + ((h << 5) - h);
  return COLORS[Math.abs(h) % COLORS.length];
}

/** hex → rgb 对象 */
export function hexToRgb(hex) {
  const r = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return r ? { r: parseInt(r[1], 16), g: parseInt(r[2], 16), b: parseInt(r[3], 16) } : { r: 255, g: 0, b: 0 };
}

/**
 * 在 canvas 上绘制检测结果
 * @param {CanvasRenderingContext2D} ctx
 * @param {Array} detections
 * @param {object} opts - 绘制选项
 */
export function drawDetections(ctx, detections, inferSize, opts = {}) {
  if (!detections?.length) return;

  const cw = ctx.canvas.width, ch = ctx.canvas.height;
  const sx = cw / inferSize.width, sy = ch / inferSize.height;
  const alpha = opts.maskAlpha ?? 0.3;

  // 掩膜
  if (opts.showMasks) {
    for (const d of detections) {
      if (!d.polygons?.length) continue;
      const rgb = hexToRgb(getColor(d.label));
      ctx.fillStyle = `rgba(${rgb.r},${rgb.g},${rgb.b},${alpha})`;
      for (const p of d.polygons) {
        if (!p?.length) continue;
        ctx.beginPath();
        for (let i = 0; i < p.length; i += 2) {
          i === 0 ? ctx.moveTo(p[i] * sx, p[i + 1] * sy) : ctx.lineTo(p[i] * sx, p[i + 1] * sy);
        }
        ctx.closePath();
        ctx.fill();
      }
    }
  }

  ctx.lineWidth = 2;
  ctx.font = 'bold 12px sans-serif';

  for (const d of detections) {
    const [x1, y1, x2, y2] = d.bbox.map((v, i) => v * (i % 2 ? sy : sx));
    const c = getColor(d.label);

    // 边框
    if (opts.showBoxes) {
      ctx.strokeStyle = c;
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
    }

    // 标签
    if (opts.showLabels) {
      const l = `${d.label} ${(d.score * 100).toFixed(0)}%`;
      ctx.fillStyle = c;
      ctx.fillRect(x1, y1 - 16, ctx.measureText(l).width + 6, 16);
      ctx.fillStyle = '#000';
      ctx.fillText(l, x1 + 3, y1 - 4);
    }

    // 关键点 + 骨架
    if (d.keypoints?.length && (opts.showKeypoints || opts.showSkeleton)) {
      const kps = d.keypoints.map(k => [k[0] * sx, k[1] * sy]);
      if (opts.showSkeleton) {
        ctx.strokeStyle = c;
        for (const [i, j] of SKELETON) {
          if (kps[i] && kps[j] && kps[i][0] > 0 && kps[j][0] > 0) {
            ctx.beginPath();
            ctx.moveTo(...kps[i]);
            ctx.lineTo(...kps[j]);
            ctx.stroke();
          }
        }
      }
      if (opts.showKeypoints) {
        for (const [x, y] of kps) {
          if (x > 0 && y > 0) {
            ctx.fillStyle = c;
            ctx.beginPath();
            ctx.arc(x, y, 3, 0, Math.PI * 2);
            ctx.fill();
          }
        }
      }
    }
  }
}
