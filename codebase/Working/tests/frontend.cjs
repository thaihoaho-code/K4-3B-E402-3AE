// Test-only HTTP server: no production data or backend modules are changed.
// Run with Playwright available: node tests/frontend.cjs
const { chromium } = require('../Frontend/node_modules/playwright');
const assert = require('node:assert/strict');
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const { setTimeout: delay } = require('node:timers/promises');
const pdfFixture = require('./pdf-fixture.cjs');
const root = path.resolve(__dirname, '../Frontend');
const corpus = [
  { topic_id: 'test-a', title: 'Chủ đề kiểm thử A', slides: [{ slide_ref: 'Slide 15', text: 'Nội dung đúng của Slide 15.' }, { slide_ref: 'Slide 16', text: 'Nội dung Slide 16.' }] },
  { topic_id: 'test-b', title: 'Chủ đề kiểm thử B', slides: [{ slide_ref: 'Slide 20', text: 'Tài liệu chủ đề B.' }] }
];
let mode = 'normal', corpusError = false, noteError = false;
let uploadMode = 'wrapped';
const uploads = [];
const chats = [], notes = [], errors = [];
async function testPdfUpload(page, chats, uploads, setMode) {
  const text = 'Giới thiệu về mô hình ngôn ngữ và tiếng Việt.';
  const pages = [text, '', 'Quá trình huấn luyện: học và giải thích.'];
  const file = { name: 'AI_Training_Process.pdf', mimeType: 'application/pdf', buffer: pdfFixture(pages) };
  const choose = value => page.setInputFiles('#pdf-file', value);
  const statusHas = async text => {
    try { await page.waitForFunction(text => document.getElementById('upload-status').textContent.includes(text), text, { timeout: 15000 }); }
    catch (error) { throw new Error(`Expected upload status: ${text}; actual: ${await page.locator('#upload-status').textContent()}`, { cause: error }); }
  };
  const before = await page.locator('#messages').textContent();
  await choose({ ...file, mimeType: 'text/plain' }); await statusHas('application/pdf');
  assert.equal(await page.locator('#upload-topic').isDisabled(), true);
  await choose({ ...file, buffer: Buffer.alloc(20 * 1024 * 1024 + 1) }); await statusHas('20 MB');
  assert.equal(await page.locator('#upload-topic').isDisabled(), true);
  await choose({ ...file, buffer: pdfFixture(['', '']) }); await page.click('#upload-topic'); await statusHas('File PDF không có lớp văn bản để trích xuất. PDF dạng ảnh chưa được hỗ trợ.');
  assert.equal(uploads.length, 0); assert.equal(await page.locator('#messages').textContent(), before);
  await choose({ ...file, buffer: pdfFixture(Array(101).fill('Page')) }); await page.click('#upload-topic'); await statusHas('100 trang');
  await choose({ ...file, buffer: Buffer.from('not a pdf') }); await page.click('#upload-topic'); await statusHas('Không đọc được PDF');
  assert.equal(uploads.length, 0);
  await choose(file);
  assert.equal(await page.locator('#pdf-filename').textContent(), file.name);
  assert.equal(await page.locator('#upload-topic').isDisabled(), false);
  await page.click('#upload-topic'); await statusHas('tạo chủ đề thành công');
  assert.deepEqual(uploads.at(-1), { title: file.name, slides: pages.map((text, i) => ({ slide_ref: `Slide ${i + 1}`, text })) });
  assert.equal(await page.locator('#pdf-pages').textContent(), 'Số trang: 3');
  assert.equal(await page.locator('#topics button').count(), 3);
  assert.equal(await page.locator('#topics button.selected').textContent(), '▤' + file.name);
  await page.click('#open-reference'); assert.equal(await page.locator('#reference-body h3').count(), 3);
  assert.equal(await page.locator('#reference-body p').first().textContent(), text);
  await page.click('#reference-dialog .close');
  const explanation = 'Em giải thích lại nội dung bằng lời của mình.';
  await page.fill('#message', explanation); await page.click('#send');
  await page.waitForFunction(() => document.getElementById('turn-count').textContent === '01');
  assert.equal(chats.at(-1).topic_id, 'uploaded-1');
  const snapshot = await page.evaluate(() => ({ title: current.title, history: JSON.stringify(history), count: catalog.length, messages: document.getElementById('messages').textContent }));
  for (const mode of ['http-error', 'invalid-json', 'invalid-topic']) {
    setMode(mode); await choose(file); await page.click('#upload-topic'); await statusHas('Chưa tải được slide.');
    assert.deepEqual(await page.evaluate(() => ({ title: current.title, history: JSON.stringify(history), count: catalog.length, messages: document.getElementById('messages').textContent })), snapshot);
    assert.equal(await page.locator('#upload-topic').isDisabled(), false);
  }
  setMode('direct'); await choose({ ...file, name: 'Direct.pdf' }); await page.click('#upload-topic'); await statusHas('tạo chủ đề thành công');
  assert.equal(await page.locator('#topic-title').textContent(), 'Direct.pdf');
  setMode('no-id'); await choose({ ...file, name: 'Fallback.pdf' }); await page.click('#upload-topic'); await statusHas('ID fallback');
  assert.equal(await page.evaluate(() => current.id), await page.evaluate(() => fallbackTopicId('Fallback.pdf')));
  assert.match(await page.locator('#upload-status').textContent(), /backend thiếu topic_id/);
  setMode('slow'); await choose({ ...file, name: 'Old.pdf' });
  const count = uploads.length; await page.click('#upload-topic');
  for (let i = 0; i < 250 && uploads.length === count; i++) await delay(20);
  assert.ok(uploads.length > count, 'Old request reached the test server');
  assert.equal(await page.locator('#upload-topic').isDisabled(), true);
  await choose({ ...file, name: 'New.pdf' }); setMode('wrapped'); await page.click('#upload-topic'); await statusHas('tạo chủ đề thành công');
  await delay(1100); assert.equal(await page.locator('#topic-title').textContent(), 'New.pdf');
  assert.equal(await page.locator('#topics').textContent().then(text => text.includes('Old.pdf')), false);
  // Untrusted strings are displayed as text, never interpreted as HTML.
  const hostile = '<img src=x onerror=alert(1)>';
  await choose({ ...file, name: hostile + '.pdf', buffer: pdfFixture([hostile]) });
  await page.click('#upload-topic'); await statusHas('tạo chủ đề thành công'); await page.click('#open-reference');
  assert.equal(await page.locator('#reference-body img').count(), 0);
  assert.equal(await page.locator('#reference-body p').textContent(), hostile);
  await page.click('#reference-dialog .close');
  const validation = await page.evaluate(() => {
    const base = { id: 'alias-id', title: 'Topic', slides: [{ slide_ref: 'Slide 1', text: 'Text' }] };
    const valid = normalizeUploadedTopic(base, 'name.pdf').topic.id;
    const invalid = [null, {}, { ...base, id: 42 }, { ...base, slides: [{ slide_ref: 'Slide 1', text: null }] },
      { ...base, slides: [{ slide_ref: 'Slide 1', text: 'x'.repeat(PDF_LIMITS.text + 1) }] }];
    return { valid, rejected: invalid.map(value => { try { normalizeUploadedTopic(value, 'name.pdf'); return false; } catch { return true; } }) };
  });
  assert.equal(validation.valid, 'alias-id'); assert.ok(validation.rejected.every(Boolean));
  for (const width of [320, 390, 768]) {
    await page.setViewportSize({ width, height: 844 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
  }
}
const server = http.createServer(async (req, res) => {
  const pathname = new URL(req.url, 'http://localhost').pathname;
  if (pathname === '/data/slide_corpus.json') {
    res.writeHead(corpusError ? 404 : 200, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify(corpus));
  }
  if (req.method === 'POST') {
    let raw = ''; for await (const chunk of req) raw += chunk;
    const body = JSON.parse(raw);
    if (pathname === '/topics/from-slides') {
      uploads.push(body);
      const requestedMode = uploadMode;
      if (requestedMode === 'slow') await delay(900);
      res.writeHead(requestedMode === 'http-error' ? 503 : 200, { 'Content-Type': 'application/json' });
      if (requestedMode === 'invalid-json') return res.end('{bad');
      if (requestedMode === 'invalid-topic') return res.end(JSON.stringify({ topic: { title: 'Invalid', slides: [] } }));
      const topic = { topic_id: 'uploaded-' + uploads.length, title: body.title, slides: body.slides };
      if (requestedMode === 'no-id') delete topic.topic_id;
      return res.end(JSON.stringify(requestedMode === 'direct' ? topic : { topic }));
    }
    if (req.url === '/notes') {
      notes.push(body); res.writeHead(noteError ? 500 : 200, { 'Content-Type': 'application/json' });
      return res.end(JSON.stringify({ saved: !noteError }));
    }
    chats.push(body);
    const requestMode = mode;
    if (requestMode === 'http-error') { res.writeHead(503); return res.end(); }
    if (requestMode === 'json') { res.setHeader('Content-Type', 'application/json'); return res.end('null'); }
    res.writeHead(200, { 'Content-Type': 'text/event-stream' }); res.flushHeaders();
    if (requestMode === 'slow') await delay(600);
    const text = body.action === 'skip' ? 'Góc hỏi mới: ' : 'Thầy/cô ơi, ';
    // Byte-by-byte writes split UTF-8 and CRLF delimiters over actual HTTP.
    const first = Buffer.from(': heartbeat\r\ndata: ' + JSON.stringify({ text }) + '\r\n\r\n');
    for (const byte of first) { if (res.destroyed) return; res.write(Buffer.from([byte])); await delay(1); }
    await delay(150);
    if (res.destroyed) return;
    if (requestMode === 'truncated') return res.end('data: {"text":"unfinished');
    if (requestMode === 'sse-error') return res.end('event: error\ndata: {"error":"Lỗi kiểm thử"}\n\n');
    res.write('data: {"text":"hãy giải thích thêm nhé 🌱",\ndata: "slide_ref":"Slide 15", "asked_index":' + (body.action ? 1 : 0) + '}\n\n');
    res.end('data: [DONE]\n\n');
    return;
  }
  const file = path.resolve(root, '.' + (pathname === '/' ? '/index.html' : pathname));
  if (!file.startsWith(root + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404); return res.end(); }
  const mime = { '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.html': 'text/html', '.wasm': 'application/wasm' };
  res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream');
  res.end(fs.readFileSync(file));
});

(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ channel: process.env.BROWSER_CHANNEL || 'msedge', headless: true });
  try {
    const page = await browser.newPage();
    page.on('pageerror', error => errors.push(error.message));
    await page.route('https://fonts.googleapis.com/**', route => route.abort());
    const url = `http://127.0.0.1:${server.address().port}`;
    const waitReady = () => page.waitForFunction(() => !document.getElementById('message').disabled);
    await page.goto(url); await waitReady();
    assert.equal(await page.locator('#topics button').count(), 2);
    const input = 'Mình giải thích khái niệm này bằng một ví dụ của riêng mình.';
    await page.fill('#message', input); await page.click('#send');
    await page.waitForFunction(() => document.getElementById('message').disabled);
    await page.waitForFunction(() => [...document.querySelectorAll('.bubble')].at(-1).textContent === 'Thầy/cô ơi, ');
    assert.equal(await page.locator('#skip-thread').isDisabled(), true);
    await waitReady();
    assert.equal(await page.locator('.bubble').last().textContent(), 'Thầy/cô ơi, hãy giải thích thêm nhé 🌱');
    assert.deepEqual(chats[0], { topic_id: 'test-a', user_text: input, history: [], asked_indexes: [] });
    assert.equal(await page.locator('#turn-count').textContent(), '01');
    await page.click('.source-badge');
    assert.equal(await page.locator('#reference-body h3').textContent(), 'Slide 15');
    assert.equal(await page.locator('#reference-body p').textContent(), corpus[0].slides[0].text);
    await page.click('#reference-dialog .close');
    await page.fill('#message', 'Bản nháp được giữ lại'); await page.click('#skip-thread'); await waitReady();
    assert.equal(chats[1].action, 'skip'); assert.deepEqual(chats[1].asked_indexes, [0]);
    assert.equal(chats[1].history.length, 2);
    assert.equal(await page.inputValue('#message'), 'Bản nháp được giữ lại');
    assert.equal(await page.locator('#turn-count').textContent(), '01');
    await page.click('#finish'); await page.fill('#reflection', 'Điều mình đã hiểu');
    noteError = true; await page.click('#save-note');
    await page.waitForFunction(() => document.getElementById('save-status').textContent.includes('Chưa lưu'));
    assert.equal(await page.inputValue('#reflection'), 'Điều mình đã hiểu');
    noteError = false; await page.click('#save-note');
    await page.waitForFunction(() => document.getElementById('save-status').textContent === 'Đã lưu ✓');
    assert.deepEqual(notes.at(-1), { topic_id: 'test-a', turns: 1, reflection: 'Điều mình đã hiểu' });
    await page.click('#summary-dialog .close');
    console.log('PASS: streamed Vietnamese, pending controls, exact slide, skip history/indexes, notes failure/retry');

    for (const failure of ['http-error', 'json', 'truncated', 'sse-error']) {
      mode = failure; await page.fill('#message', input); await page.click('#send'); await waitReady();
      assert.equal(await page.inputValue('#message'), input);
      assert.equal(await page.locator('#turn-count').textContent(), '01');
      assert.notEqual(await page.locator('#thread-status').textContent(), '');
    }
    console.log('PASS: HTTP error, non-SSE backend stub, truncated stream, SSE error; draft and count preserved');
    mode = 'slow'; await page.click('#send');
    await page.waitForFunction(() => document.getElementById('message').disabled);
    await page.locator('#topics button').nth(1).click(); await delay(1000);
    assert.equal(await page.locator('.message').count(), 1);
    assert.equal(await page.locator('#topic-title').textContent(), corpus[1].title);
    assert.equal(await page.locator('#turn-count').textContent(), '00');
    mode = 'normal'; await page.fill('#message', input); await page.click('#send'); await waitReady();
    assert.deepEqual(chats.at(-1).history, []);
    assert.deepEqual(chats.at(-1).asked_indexes, []);
    await page.click('.source-badge');
    assert.match(await page.locator('#reference-body').textContent(), /chưa có/);
    await page.click('#reference-dialog .close');
    await page.setViewportSize({ width: 390, height: 844 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    corpusError = true; await page.reload();
    await page.waitForFunction(() => document.getElementById('topic-title').textContent === 'Chưa tải được chủ đề');
    assert.equal(await page.locator('#send').isDisabled(), true);
    corpusError = false; await page.click('#reset'); await waitReady();
    assert.deepEqual(errors, []);
    console.log('PASS: topic cancellation, unknown reference, mobile layout, missing corpus and retry; no browser JS errors');
    await testPdfUpload(page, chats, uploads, value => { uploadMode = value; });
    assert.deepEqual(errors, []);
    console.log('PASS: upload scenarios, real pdf.js worker, Vietnamese extraction, mobile layout; no browser JS errors');
  } finally { await browser.close(); server.closeAllConnections(); server.close(); }
})().catch(error => { console.error(error); server.closeAllConnections(); server.close(); process.exitCode = 1; });
