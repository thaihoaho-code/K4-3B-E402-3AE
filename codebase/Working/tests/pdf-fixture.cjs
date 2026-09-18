// Small, real PDF with a ToUnicode map. No external fixture/font/download required.
module.exports = function pdfFixture(pages) {
  const chars = [...new Set(pages.join(''))];
  if (chars.length > 222) throw new Error('Fixture supports at most 222 distinct characters');
  const codes = new Map(chars.map((char, i) => [char, (i + 33).toString(16).padStart(2, '0')]));
  const objects = [], add = text => { objects.push(text); return objects.length; };
  const stream = text => `<< /Length ${Buffer.byteLength(text)} >>\nstream\n${text}\nendstream`;
  add('<< /Type /Catalog /Pages 2 0 R >>'); add('');
  add('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /ToUnicode 4 0 R >>');
  const mapping = chars.map(char => `<${codes.get(char)}> <${char.charCodeAt(0).toString(16).padStart(4, '0')}>`).join('\n');
  add(stream(`/CIDInit /ProcSet findresource begin\n12 dict begin\nbegincmap\n/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def\n/CMapName /TestUnicode def\n/CMapType 2 def\n1 begincodespacerange\n<00> <FF>\nendcodespacerange\n${chars.length} beginbfchar\n${mapping}\nendbfchar\nendcmap\nCMapName currentdict /CMap defineresource pop\nend\nend`));
  const ids = [];
  for (const text of pages) {
    const id = objects.length + 1; ids.push(id);
    add(`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents ${id + 1} 0 R >>`);
    add(stream(text ? `BT /F1 12 Tf 30 700 Td <${[...text].map(char => codes.get(char)).join('')}> Tj ET` : ''));
  }
  objects[1] = `<< /Type /Pages /Kids [${ids.map(id => `${id} 0 R`).join(' ')}] /Count ${pages.length} >>`;
  let pdf = '%PDF-1.7\n', offsets = [0];
  objects.forEach((object, i) => { offsets.push(Buffer.byteLength(pdf)); pdf += `${i + 1} 0 obj\n${object}\nendobj\n`; });
  const xref = Buffer.byteLength(pdf);
  pdf += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
  pdf += offsets.slice(1).map(offset => String(offset).padStart(10, '0') + ' 00000 n \n').join('');
  pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF\n`;
  return Buffer.from(pdf);
};
