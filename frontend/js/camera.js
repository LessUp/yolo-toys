/**
 * 摄像头管理模块
 */

/** 启动摄像头 */
export async function setupCamera(video, canvas) {
  const stream = await navigator.mediaDevices.getUserMedia({
    video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: 'environment' },
  });
  video.srcObject = stream;
  await new Promise(r => (video.onloadedmetadata = r));
  video.play();
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
}

/** 停止摄像头 */
export function stopCamera(video) {
  video.srcObject?.getTracks().forEach(t => t.stop());
  video.srcObject = null;
}

/** 捕获帧为 JPEG Blob */
export function captureFrame(video, sendWidth, quality = 0.8) {
  return new Promise(resolve => {
    const scale = sendWidth / video.videoWidth;
    const sw = Math.round(video.videoWidth * scale);
    const sh = Math.round(video.videoHeight * scale);
    const sc = document.createElement('canvas');
    sc.width = sw;
    sc.height = sh;
    sc.getContext('2d').drawImage(video, 0, 0, sw, sh);
    sc.toBlob(resolve, 'image/jpeg', quality);
  });
}
