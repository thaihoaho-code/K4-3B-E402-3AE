const topics = [
  { id: 'llm', icon: '✧', short: 'Vì sao LLM “bịa”?', title: 'Vì sao mô hình ngôn ngữ có thể “bịa”?', intro: 'Em thấy AI trả lời câu nào cũng có vẻ rất chắc chắn, nên em cứ tưởng AI biết hết. Thầy/cô giảng cho em vì sao AI vẫn có thể “bịa” thông tin được không ạ?', sample: 'Mình nghĩ LLM chỉ bịa khi không có đủ dữ liệu.', questions: ['Thầy/cô ơi, nếu AI đã đọc cả một thư viện rất lớn rồi thì nó còn có thể kể tên một cuốn sách không có thật không ạ?', 'Em thấy AI giải thích nghe rất xuôi tai, nên em dễ tin lắm ạ. Làm sao em biết lúc nào cần kiểm tra lại lời AI nói ạ?', 'Nếu em nhờ AI tìm một cuốn sách để đọc, thầy/cô sẽ kiểm tra điều gì trước khi giới thiệu cuốn đó cho em ạ?'], keywords: /dữ liệu|du lieu|thiếu|thieu/, source: ['Mô hình ngôn ngữ tạo văn bản bằng cách dự đoán token tiếp theo dựa trên ngữ cảnh và các mẫu đã học.', 'Một câu hợp lý về mặt ngôn ngữ không bảo đảm đúng về mặt sự thật. Dữ liệu huấn luyện nhiều cũng không bảo đảm mọi câu trả lời đều chính xác.', 'Hãy tự đối chiếu các khẳng định quan trọng với nguồn có thể kiểm chứng.'] },
  { id: 'probability', icon: '◷', short: 'Xác suất độc lập', title: 'Thế nào là hai biến cố độc lập?', intro: 'Em vừa tung đồng xu ra mặt ngửa ba lần liền, thấy lạ quá ạ. Thầy/cô có thể giảng cho em “độc lập” trong xác suất là thế nào không ạ?', sample: 'Ra ngửa nhiều rồi thì lần tiếp theo dễ ra sấp hơn.', questions: ['Thầy/cô ơi, em hơi băn khoăn: đồng xu có biết ba lần trước đã ra ngửa để lần này đổi sang sấp không ạ?', 'Em thấy có hai chuyện xảy ra cùng lúc, nên em định gọi chúng là “độc lập”. Em còn cần tìm hiểu điều gì trước khi gọi như vậy ạ?', 'Nếu em bốc một viên bi rồi giữ luôn, lần bốc tiếp theo có còn giống lúc đầu không ạ?'], keywords: /sấp|sap|ngửa|ngua|lần|lan/, source: ['Hai biến cố A và B độc lập khi P(A ∩ B) = P(A) × P(B). Khi P(B) > 0, điều này tương đương P(A | B) = P(A).', 'Với đồng xu cân đối và các lần tung độc lập, xác suất ngửa ở mỗi lần vẫn là 1/2, bất kể kết quả các lần trước.', 'Độc lập khác với xung khắc: hai biến cố xung khắc không thể cùng xảy ra.'] },
  { id: 'overfit', icon: '▧', short: 'Overfitting là gì?', title: 'Vì sao mô hình bị overfitting?', intro: 'Em thấy một mô hình làm bài đã học gần như hoàn hảo, nên em nghĩ mô hình ấy giỏi lắm. Thầy/cô giảng cho em overfitting là gì được không ạ?', sample: 'Mô hình đạt 99% trên dữ liệu huấn luyện thì chắc là tốt.', questions: ['Thầy/cô ơi, nếu em thuộc hết đáp án bài ôn mà đề thi đổi cách hỏi, em có làm tốt như lúc ôn không ạ?', 'Nếu em cứ đưa lại những bài mô hình đã làm rồi để kiểm tra, làm sao em biết nó sẽ làm được bài mới ạ?', 'Em vẫn chưa hình dung rõ “hiểu cách làm” khác “nhớ đáp án” ở đâu. Thầy/cô có thể kể cho em một ví dụ gần gũi được không ạ?'], keywords: /99|huấn luyện|huan luyen|thuộc|thuoc/, source: ['Overfitting xảy ra khi mô hình khớp quá sát dữ liệu huấn luyện, kể cả nhiễu, và khái quát kém trên dữ liệu chưa thấy.', 'Cần đánh giá trên dữ liệu tách biệt với dữ liệu huấn luyện. Kết quả huấn luyện cao chưa đủ để kết luận khả năng khái quát tốt.', 'Các hướng giảm overfitting gồm regularization, early stopping, điều chỉnh độ phức tạp và cải thiện dữ liệu.'] }
];
let current = topics[0], turns = 0, pending = null;
const $ = id => document.getElementById(id);
function openReference(topic) {
  $('reference-title').textContent = topic.title;
  $('reference-body').replaceChildren();
  topic.source.forEach((text, index) => {
    const heading = document.createElement('h3');
    heading.textContent = `Tài liệu tham chiếu · mục ${index + 1}`;
    const p = document.createElement('p'); p.textContent = text;
    $('reference-body').append(heading, p);
  });
  $('reference-dialog').showModal();
}
function addMessage(text, role = 'bot', meta = {}) {
  const row = document.createElement('div'); row.className = `message ${role}`;
  const avatar = document.createElement('span'); avatar.className = `avatar ${role === 'bot' ? 'bot-avatar' : 'user-avatar'}`; avatar.textContent = role === 'bot' ? '✦' : 'B';
  const content = document.createElement('div'); content.className = 'message-content';
  const name = document.createElement('div'); name.className = 'message-name'; name.textContent = role === 'bot' ? 'Học trò · em đang lắng nghe' : 'Bạn · người hướng dẫn';
  const bubble = document.createElement('div'); bubble.className = 'bubble'; bubble.textContent = text;
  content.append(name, bubble);
  if (role === 'bot' && meta.live) {
    const badge = document.createElement('div'); badge.className = 'source-badge';
    badge.textContent = 'Phản hồi từ model AI thật · dựa trên tài liệu tham chiếu đã nạp';
    content.append(badge);
  }
  row.append(avatar, content); $('messages').append(row); $('messages').scrollTop = $('messages').scrollHeight;
}
function updateProgress() {
  $('turn-count').textContent = String(turns).padStart(2, '0');
  [...$('steps').children].forEach((li, index) => li.classList.toggle('active', index <= Math.min(turns, 2)));
  $('send').disabled = pending !== null || !$('message').value.trim();
  $('skip-thread').disabled = pending !== null;
  $('simulate-uncertain').disabled = pending !== null;
}
function start(topic) {
  clearTimeout(pending); pending = null; current = topic; turns = 0;
  $('messages').replaceChildren(); $('message').value = ''; $('topic-title').textContent = current.title;
  $('scope-topic').textContent = '“' + current.title + '”'; $('thread-status').textContent = '';
  [...$('topics').children].forEach((button, i) => { button.classList.toggle('selected', topics[i] === current); button.setAttribute('aria-pressed', String(topics[i] === current)); });
  addMessage('Dạ, em chào thầy/cô! Em là Học trò. 🌱\n\n' + current.intro + '\n\nEm xin phép hỏi từng chút nếu có chỗ chưa hiểu ạ.');
  $('suggestions').replaceChildren();
  const sample = document.createElement('button'); sample.textContent = '✎ Thử một lời giải thích mẫu'; sample.onclick = () => { $('message').value = current.sample; $('message').focus(); updateProgress(); };
  const help = document.createElement('button'); help.textContent = 'Mình chưa biết bắt đầu từ đâu'; help.onclick = () => { $('message').value = 'Mình chưa biết bắt đầu từ đâu'; send(); };
  $('suggestions').append(sample, help); updateProgress();
}
async function send() {
  const input = $('message').value.trim();
  if (!input || pending !== null) return;

  addMessage(input, 'user');
  $('message').value = '';
  $('suggestions').replaceChildren();
  turns++;
  updateProgress();

  pending = true;
  $('send').disabled = true;

  try {
    const res = await fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_text: input,
        topic: current.title,
        topic_id: current.id
      })
    });
    const data = await res.json().catch(() => ({}));
    if (res.ok && data.reply) {
      addMessage(data.reply, 'bot', { live: true });
      $('thread-status').textContent = 'Đã nhận phản hồi từ model thật và ghi log kỹ thuật.';
    } else {
      addMessage(`Em chưa thể trả lời lúc này ạ. ${data.error || 'Thầy/cô thử lại giúp em nhé.'}`, 'bot');
    }
  } catch (err) {
    addMessage('Em chưa kết nối được server ạ. Thầy/cô mở sản phẩm qua python server.py rồi thử lại giúp em nhé.', 'bot');
  } finally {
    pending = null;
    updateProgress();
  }
}

$('skip-thread').onclick = () => {
  if (pending !== null) return;
  $('message').value = 'Em muốn đổi góc hỏi: hãy hỏi em một câu khác dựa trên phần em vừa giải thích.';
  $('suggestions').replaceChildren();
  send();
};
$('simulate-uncertain').onclick = () => {
  if (pending !== null) return;
  $('message').value = 'LLM chém gió giống như một chiếc hộp biết mọi thứ, kể cả ví dụ không có trong tài liệu này.';
  $('thread-status').textContent = 'Đang gửi một input ngoài tài liệu qua model thật.';
  send();
};
topics.forEach(topic => { const button = document.createElement('button'); button.className = 'topic-button'; const icon = document.createElement('span'); icon.textContent = topic.icon; button.append(icon, document.createTextNode(topic.short)); button.onclick = () => start(topic); $('topics').append(button); });
$('chat-form').onsubmit = event => { event.preventDefault(); send(); };
$('message').oninput = updateProgress;
$('message').onkeydown = event => { if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) { event.preventDefault(); send(); } };
$('reset').onclick = () => start(current);
$('open-reference').onclick = () => openReference(current);
$('finish').onclick = () => {
  $('summary-text').textContent = `Chủ đề: ${current.short} Bạn đã chia sẻ ${turns} lượt. Hãy ghi lại điều bạn muốn diễn đạt rõ hơn ở lần học tiếp theo.`;
  $('save-status').textContent = ''; $('reflection').value = '';
  try { $('reflection').value = localStorage.getItem('vlearn-note-' + current.id) || ''; } catch { /* Storage may be unavailable in private browsing. */ }
  $('summary-dialog').showModal();
};
$('save-note').onclick = () => { if (!$('reflection').value.trim()) { $('save-status').textContent = 'Bạn hãy viết một điều muốn ghi nhớ trước nhé.'; return; } try { localStorage.setItem('vlearn-note-' + current.id, $('reflection').value); $('save-status').textContent = 'Đã lưu ghi chú cho chủ đề này ✓'; } catch { $('save-status').textContent = 'Trình duyệt chưa cho phép lưu. Bạn có thể sao chép ghi chú để giữ lại.'; } };
document.querySelectorAll('dialog').forEach(dialog => { dialog.querySelectorAll('.close, .close-action').forEach(button => button.onclick = () => dialog.close()); dialog.addEventListener('click', event => { if (event.target === dialog) { const rect = dialog.getBoundingClientRect(); if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close(); } }); });
start(current);
