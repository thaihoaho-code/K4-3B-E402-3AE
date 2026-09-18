'use strict';
const PDF_LIMITS = Object.freeze({ bytes: 20 * 1024 * 1024, pages: 100, text: 1000000 });
const PDF_NO_TEXT = 'File PDF không có lớp văn bản để trích xuất. PDF dạng ảnh chưa được hỗ trợ.';
const PDF_ASSET_BASE = new URL('./vendor/pdfjs/', document.baseURI).href;
let pdfLibraryPromise;

function validatePdfFile(file) {
  if (!file || file.type !== 'application/pdf') throw new Error('Vui lòng chọn file có MIME type application/pdf.');
  if (file.size > PDF_LIMITS.bytes) throw new Error('File PDF vượt quá giới hạn 20 MB.');
  if (!file.size) throw new Error('File PDF rỗng. Vui lòng chọn file khác.');
}

// Optional signal/progress keep extraction independent of the upload UI.
async function extractPdfSlides(file, { signal, onProgress = () => {} } = {}) {
  validatePdfFile(file);
  let task;
  const checkCancelled = () => { if (signal?.aborted) throw new DOMException('Đã hủy đọc PDF.', 'AbortError'); };
  const cancel = () => { if (task) void task.destroy().catch(() => {}); };
  try {
    checkCancelled();
    pdfLibraryPromise ??= import(new URL('pdf.mjs', PDF_ASSET_BASE).href).catch(() => {
      pdfLibraryPromise = null;
      throw new Error('Chưa tải được thư viện PDF. Hãy chạy npm install trong thư mục Frontend rồi thử lại.');
    });
    const pdfjs = await pdfLibraryPromise;
    checkCancelled();
    pdfjs.GlobalWorkerOptions.workerSrc = new URL('pdf.worker.mjs', PDF_ASSET_BASE).href;
    const data = new Uint8Array(await file.arrayBuffer());
    checkCancelled();
    task = pdfjs.getDocument({ data, cMapUrl: new URL('cmaps/', PDF_ASSET_BASE).href,
      cMapPacked: true, standardFontDataUrl: new URL('standard_fonts/', PDF_ASSET_BASE).href,
      wasmUrl: new URL('wasm/', PDF_ASSET_BASE).href, isEvalSupported: false });
    signal?.addEventListener('abort', cancel, { once: true });
    const pdf = await task.promise;
    checkCancelled();
    onProgress(0, pdf.numPages);
    if (pdf.numPages > PDF_LIMITS.pages) throw new Error('PDF vượt quá giới hạn 100 trang.');
    const slides = [];
    let total = 0;
    for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {
      checkCancelled();
      const page = await pdf.getPage(pageNumber);
      try {
        const content = await page.getTextContent();
        checkCancelled();
        const parts = [];
        for (const item of content.items) {
          if (typeof item.str !== 'string') continue;
          total += item.str.length + 1;
          if (total > PDF_LIMITS.text) throw new Error('Nội dung PDF vượt quá giới hạn 1.000.000 ký tự. Vui lòng chia nhỏ tài liệu.');
          parts.push(item.str, item.hasEOL ? '\n' : ' ');
        }
        const text = parts.join('').replace(/[^\S\n]+/gu, ' ').replace(/ *\n */g, '\n').replace(/\n{3,}/g, '\n\n').trim();
        slides.push({ slide_ref: `Slide ${pageNumber}`, text });
      } finally { page.cleanup(); }
      onProgress(pageNumber, pdf.numPages);
      // Yield between pages instead of blocking input/paint for the full document.
      await new Promise(resolve => setTimeout(resolve, 0));
    }
    checkCancelled();
    if (!slides.some(slide => slide.text.trim())) throw new Error(PDF_NO_TEXT);
    return { title: file.name, slides };
  } catch (error) {
    checkCancelled();
    if (error.name === 'PasswordException') throw new Error('PDF có mật khẩu. Vui lòng chọn bản PDF không khóa.');
    if (error.name === 'InvalidPDFException') throw new Error('Không đọc được PDF. File có thể bị hỏng hoặc không đúng định dạng.');
    throw error;
  } finally {
    signal?.removeEventListener('abort', cancel);
    if (task) { try { await task.destroy(); } catch { /* Keep the original result/error. */ } }
  }
}
