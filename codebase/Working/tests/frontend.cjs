// Test-only HTTP server: no production data or backend modules are changed.
// Run with Playwright available: node tests/frontend.cjs
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const { setTimeout: delay } = require('node:timers/promises');
const root = path.resolve(__dirname, '..');
const corpus = [
  { topic_id: 'test-a', title: 'Chủ đề kiểm thử A', slides: [{ slide_ref: 'Slide 15', text: 'Nội dung đúng của Slide 15.' }, { slide_ref: 'Slide 16', text: 'Nội dung Slide 16.' }] },
  { topic_id: 'test-b', title: 'Chủ đề kiểm thử B', slides: [{ slide_ref: 'Slide 20', text: 'Tài liệu chủ đề B.' }] }
];
let mode = 'normal', corpusError = false, noteError = false;
const chats = [], notes = [], errors = [];
const server = http.createServer(async (req, res) => {
  if (req.url === '/data/slide_corpus.json') {
    res.writeHead(corpusError ? 404 : 200, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify(corpus));
  }
  if (req.method === 'POST') {
    let raw = ''; for await (const chunk of req) raw += chunk;
    const body = JSON.parse(raw);
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
  const files = { '/': 'index.html', '/index.html': 'index.html', '/app.js': 'app.js', '/style.css': 'style.css' };
  if (!files[req.url]) { res.writeHead(404); return res.end(); }
  res.setHeader('Content-Type', req.url.endsWith('.js') ? 'text/javascript' : req.url.endsWith('.css') ? 'text/css' : 'text/html');
  res.end(fs.readFileSync(path.join(root, files[req.url])));
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
  } finally { await browser.close(); server.closeAllConnections(); server.close(); }
})().catch(error => { console.error(error); server.closeAllConnections(); server.close(); process.exitCode = 1; });
