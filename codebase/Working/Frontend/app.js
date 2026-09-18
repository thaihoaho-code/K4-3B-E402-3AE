'use strict';
// Topic and reference content comes from the shared corpus, never a reply script.
const $ = id => document.getElementById(id);
let catalog = [], current = null, turns = 0, pending = null, asked = new Set(), history = [];
let noteSession = null, savingNote = false;

function openReference(topic, slideRef = null) {
  if (!topic) return;
  $('reference-title').textContent = topic.title;
  $('reference-body').replaceChildren();
  const slides = topic.slides.filter(slide => slideRef === null || slide.slide_ref === slideRef);
  for (const slide of slides) {
    const heading = document.createElement('h3'); heading.textContent = slide.slide_ref;
    const p = document.createElement('p'); p.textContent = slide.text;
    $('reference-body').append(heading, p);
  }
  if (!slides.length) {
    const p = document.createElement('p');
    p.textContent = `${slideRef || 'Tài liệu'}: nội dung chưa có trong tài liệu được cung cấp.`;
    $('reference-body').append(p);
  }
  $('reference-dialog').showModal();
}
function addMessage(text, role = 'bot', slideRef = null) {
  const row = document.createElement('div'); row.className = `message ${role}`;
  const avatar = document.createElement('span'); avatar.className = `avatar ${role === 'bot' ? 'bot-avatar' : 'user-avatar'}`; avatar.textContent = role === 'bot' ? '✦' : 'B';
  const content = document.createElement('div'); content.className = 'message-content';
  const name = document.createElement('div'); name.className = 'message-name'; name.textContent = role === 'bot' ? 'Học trò · em đang lắng nghe' : 'Bạn · người hướng dẫn';
  const bubble = document.createElement('div'); bubble.className = 'bubble'; bubble.textContent = text;
  content.append(name, bubble);
  if (role === 'bot' && slideRef !== null) {
    const topic = current;
    const badge = document.createElement('button'); badge.className = 'source-badge'; badge.type = 'button';
    badge.textContent = `Nguồn tham khảo: ${slideRef} ↗`;
    badge.onclick = () => openReference(topic, slideRef);
    content.append(badge);
  }
  row.append(avatar, content); $('messages').append(row); $('messages').scrollTop = $('messages').scrollHeight;
  return { row, content, bubble };
}

function updateProgress() {
  const busy = pending !== null;
  $('turn-count').textContent = String(turns).padStart(2, '0');
  [...$('steps').children].forEach((li, index) => li.classList.toggle('active', index <= Math.min(turns, 2)));
  $('message').disabled = busy || !current;
  $('send').disabled = busy || !current || $('message').value.trim().length <= 20;
  $('skip-thread').disabled = busy || !current;
  
  $('open-reference').disabled = !current;
  $('chat-form').setAttribute('aria-busy', String(busy));
  $('send').textContent = busy ? '◌' : '↑';
  if (busy && !$('send').getAnimations().length) {
    $('send').animate([{ transform: 'rotate(0deg)' }, { transform: 'rotate(360deg)' }], { duration: 1000, iterations: Infinity });
  } else if (!busy) $('send').getAnimations().forEach(animation => animation.cancel());
  $('send').setAttribute('aria-label', busy ? 'Đang chờ phản hồi' : 'Gửi lời giải thích');
}
function start(topic) {
  pending?.abort(); pending = null; current = topic; turns = 0; asked = new Set(); history = [];
  $('messages').replaceChildren(); $('message').value = '';
  $('topic-title').textContent = topic.title; $('scope-topic').textContent = '“' + topic.title + '”';
  $('thread-status').textContent = '';
  [...$('topics').children].forEach((button, i) => {
    button.classList.toggle('selected', catalog[i] === topic);
    button.setAttribute('aria-pressed', String(catalog[i] === topic));
  });
  addMessage('Dạ, em chào thầy/cô! Em là Học trò. 🌱\n\nThầy/cô hãy giải thích chủ đề “' + topic.title + '” bằng lời của mình để em cùng tìm hiểu nhé.');
  $('suggestions').replaceChildren(); updateProgress();
}

// Streaming TextDecoder preserves Vietnamese characters split across network chunks.
// SSE frames can span chunks; CRLF, comments and multi-line data are supported.
async function readSSE(body, onEvent) {
  const reader = body.getReader(), decoder = new TextDecoder();
  let buffer = '', data = [], eventName = '', finished = false;
  function line(value) {
    if (!value) {
      if (data.length) {
        const payload = data.join('\n');
        if (payload === '[DONE]') finished = true;
        else {
          const event = JSON.parse(payload);
          if (!event || typeof event !== 'object' || Array.isArray(event)) throw new Error('Sự kiện SSE không hợp lệ.');
          if (eventName === 'error' || event.error) throw new Error(typeof event.error === 'string' ? event.error : 'Máy chủ không thể hoàn thành phản hồi.');
          onEvent(event);
          if (event.done === true || eventName === 'done') finished = true;
        }
      } else if (eventName === 'done') finished = true;
      data = []; eventName = ''; return;
    }
    if (value.startsWith(':')) return;
    const colon = value.indexOf(':');
    const field = colon < 0 ? value : value.slice(0, colon);
    const content = colon < 0 ? '' : value.slice(colon + 1).replace(/^ /, '');
    if (field === 'data') data.push(content);
    if (field === 'event') eventName = content;
  }
  function consume(final = false) {
    let match;
    while (!finished && (match = /[\r\n]/.exec(buffer))) {
      const i = match.index;
      if (!final && buffer[i] === '\r' && i === buffer.length - 1) break;
      const length = buffer[i] === '\r' && buffer[i + 1] === '\n' ? 2 : 1;
      line(buffer.slice(0, i)); buffer = buffer.slice(i + length);
    }
  }
  try {
    while (!finished) {
      const chunk = await reader.read();
      buffer += decoder.decode(chunk.value, { stream: !chunk.done });
      consume(chunk.done);
      if (chunk.done) {
        // Do not turn a truncated final event into an apparently successful reply.
        if (!finished && (buffer.trim() || data.length)) throw new Error('Luồng phản hồi bị ngắt trước khi hoàn tất.');
        break;
      }
    }
  } finally {
    try { await reader.cancel(); } catch { /* Preserve original stream error. */ }
    reader.releaseLock();
  }
}

async function sendMessage(text, action = null) {
  if (!current || pending) return;
  text = text.trim();
  if (!action && text.length <= 20) {
    $('thread-status').textContent = 'Bạn hãy giải thích dài hơn 20 ký tự nhé.'; return;
  }
  const controller = new AbortController(); pending = controller;
  const topic = current, previousHistory = history.slice();
  const userRow = action ? null : addMessage(text, 'user');
  if (!action) $('message').value = '';
  $('suggestions').replaceChildren();
  const reply = addMessage('Đang chờ Học trò…');
  reply.row.setAttribute('aria-busy', 'true');
  let answer = '', indexes = new Set(asked);
  $('thread-status').textContent = action ? 'Đang đổi góc hỏi…' : 'Đang chờ phản hồi…';
  updateProgress();
  // Bound a stalled stream and cancel on topic/reset without leaking old tokens.
  let timeout = setTimeout(() => controller.abort(), 60000);
  try {
    const response = await fetch('/chat', {
      method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
      signal: controller.signal,
      body: JSON.stringify({ topic_id: topic.id, user_text: text, history: previousHistory,
        asked_indexes: [...asked], ...(action ? { action } : {}) })
    });
    if (!response.ok) throw new Error(`Không thể nhận phản hồi (HTTP ${response.status}).`);
    if (!response.headers.get('content-type')?.includes('text/event-stream') || !response.body) {
      throw new Error('Máy chủ chưa cung cấp luồng phản hồi SSE.');
    }
    await readSSE(response.body, event => {
      if (pending !== controller) return;
      clearTimeout(timeout); timeout = setTimeout(() => controller.abort(), 60000);
      if (typeof event.text === 'string') {
        answer += event.text; reply.bubble.textContent = answer;
        $('thread-status').textContent = 'Học trò đang trả lời…';
      }
      if (typeof event.slide_ref === 'string' && event.slide_ref.trim()) {
        const slideRef = event.slide_ref.trim();
        let badge = reply.content.querySelector('.source-badge');
        if (!badge) { badge = document.createElement('button'); badge.type = 'button'; badge.className = 'source-badge'; reply.content.append(badge); }
        badge.textContent = `Nguồn tham khảo: ${slideRef} ↗`;
        const ref = slideRef; badge.onclick = () => openReference(topic, ref);
      }
      if (Number.isInteger(event.asked_index) && event.asked_index >= 0) indexes.add(event.asked_index);
      if (Array.isArray(event.asked_indexes)) event.asked_indexes.forEach(i => { if (Number.isInteger(i) && i >= 0) indexes.add(i); });
      $('messages').scrollTop = $('messages').scrollHeight;
    });
    if (pending !== controller) return;
    if (!answer.trim()) throw new Error('Máy chủ trả về phản hồi rỗng.');
    // Only the backend knows question indexes; a slide number is not a question ID.
    asked = indexes;
    if (!action) { history.push({ role: 'user', content: text }); turns++; }
    history.push({ role: 'assistant', content: answer });
    $('thread-status').textContent = action ? 'Đã đổi góc hỏi. Lời giải thích đang soạn được giữ lại.' : '';
  } catch (error) {
    if (pending !== controller) return;
    reply.bubble.textContent = answer ? answer + '\n\n[Phản hồi chưa hoàn tất — vui lòng thử lại.]' : 'Chưa nhận được phản hồi. Bạn hãy thử lại nhé.';
    reply.content.querySelector('.source-badge')?.remove();
    if (!action) { userRow.row.remove(); $('message').value = text; }
    $('thread-status').textContent = controller.signal.aborted ? 'Kết nối quá lâu hoặc bị gián đoạn. Vui lòng thử lại.' : error.message;
  } finally {
    clearTimeout(timeout); reply.row.setAttribute('aria-busy', 'false');
    if (pending === controller) { pending = null; updateProgress(); $('message').focus(); }
  }
}
function send() { return sendMessage($('message').value); }
$('skip-thread').onclick = () => sendMessage('', 'skip');
$('chat-form').onsubmit = event => { event.preventDefault(); send(); };
$('message').oninput = updateProgress;
$('message').onkeydown = event => { if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) { event.preventDefault(); send(); } };
$('reset').onclick = () => current ? start(current) : loadTopics();
$('open-reference').onclick = () => openReference(current);
$('save-note').onclick = async () => {
  if (savingNote || !noteSession) return;
  const reflection = $('reflection').value.trim();
  if (!reflection) { $('save-status').textContent = 'Bạn hãy viết một điều muốn ghi nhớ trước nhé.'; return; }
  savingNote = true; $('save-note').disabled = true; $('reflection').disabled = true;
  $('save-status').textContent = 'Đang lưu…';
  try {
    const response = await fetch('/notes', { method: 'POST', headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(30000), body: JSON.stringify({ ...noteSession, reflection }) });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    if ((await response.json()).saved !== true) throw new Error('Máy chủ chưa xác nhận lưu');
    $('save-status').textContent = 'Đã lưu ✓';
  } catch (error) { $('save-status').textContent = `Chưa lưu được ghi chú (${error.message}). Bạn có thể thử lại.`; }
  finally { savingNote = false; $('save-note').disabled = false; $('reflection').disabled = false; }
};
document.querySelectorAll('dialog').forEach(dialog => { dialog.querySelectorAll('.close, .close-action').forEach(button => button.onclick = () => dialog.close()); dialog.addEventListener('click', event => { if (event.target === dialog) { const rect = dialog.getBoundingClientRect(); if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close(); } }); });


async function loadTopics() {
  current = null; updateProgress(); $('reset').disabled = true;
  $('thread-status').textContent = 'Đang tải chủ đề…';
  try {
    const response = await fetch('/data/slide_corpus.json?t=' + Date.now(), { signal: AbortSignal.timeout(15000) });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const corpus = await response.json();
    if (!Array.isArray(corpus) || !corpus.length) throw new Error('Tài liệu chưa có chủ đề');
    catalog = corpus.map(topic => {
      const id = topic.topic_id ?? topic.id, title = topic.title ?? topic.topic_title;
      if (typeof id !== 'string' || !id.trim() || typeof title !== 'string' || !title.trim() || !Array.isArray(topic.slides) || !topic.slides.length) throw new Error('Chủ đề không đúng định dạng');
      const slides = topic.slides.map(slide => {
        const text = slide.text ?? slide.content;
        if (typeof slide.slide_ref !== 'string' || !slide.slide_ref.trim() || typeof text !== 'string') throw new Error('Slide không đúng định dạng');
        return { slide_ref: slide.slide_ref.trim(), text };
      });
      return { id, title, slides };
    });
    if (new Set(catalog.map(topic => topic.id)).size !== catalog.length) throw new Error('Mã chủ đề bị trùng');
    $('topics').replaceChildren();
    catalog.forEach(topic => {
      const button = document.createElement('button'); button.className = 'topic-button';
      const icon = document.createElement('span'); icon.textContent = '▤';
      button.append(icon, document.createTextNode(topic.title)); button.onclick = () => start(topic); $('topics').append(button);
    });
    start(catalog[0]);
  } catch (error) {
    $('topic-title').textContent = 'Chưa tải được chủ đề';
    $('thread-status').textContent = `Không thể tải tài liệu (${error.message}). Nhấn Buổi học mới để thử lại.`;
  } finally { $('reset').disabled = false; updateProgress(); }
}
loadTopics();
