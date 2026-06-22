interface PdfTextOptions {
  title: string;
  meta: string;
  sections: Array<{ heading: string; keywords: string[]; body: string }>;
}

const escapePdfText = (value: string) =>
  value.replace(/\\/g, "\\\\").replace(/\(/g, "\\(").replace(/\)/g, "\\)");

const wrapText = (text: string, maxChars: number) => {
  const lines: string[] = [];
  text.split(/\n+/).forEach((paragraph) => {
    const words = paragraph.trim().split(/\s+/).filter(Boolean);
    let line = "";
    words.forEach((word) => {
      const next = line ? `${line} ${word}` : word;
      if (next.length > maxChars) {
        if (line) lines.push(line);
        line = word;
      } else {
        line = next;
      }
    });
    if (line) lines.push(line);
    lines.push("");
  });
  return lines;
};

export const generateStudyNotesPdf = ({ title, meta, sections }: PdfTextOptions) => {
  const pageWidth = 612;
  const pageHeight = 792;
  const margin = 48;
  const bottom = 52;
  const objects: string[] = [];
  const pages: number[] = [];
  let currentLines: Array<{ text: string; x: number; y: number; size: number; bold?: boolean }> = [];
  let y = pageHeight - margin;

  const addPage = () => {
    if (!currentLines.length) return;
    const stream = ["BT", ...currentLines.map((line) => {
      const font = line.bold ? "F2" : "F1";
      return `/${font} ${line.size} Tf ${line.x} ${line.y} Td (${escapePdfText(line.text)}) Tj`;
    }), "ET"].join("\n");
    const contentId = objects.push(`<< /Length ${stream.length} >>\nstream\n${stream}\nendstream`);
    const pageId = objects.push(`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${pageWidth} ${pageHeight}] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents ${contentId} 0 R >>`);
    pages.push(pageId);
    currentLines = [];
    y = pageHeight - margin;
  };

  const addLine = (text: string, size = 11, bold = false, gap = 16) => {
    if (y < bottom) addPage();
    currentLines.push({ text, x: margin, y, size, bold });
    y -= gap;
  };

  addLine(title, 24, true, 28);
  addLine(meta, 10, false, 22);

  sections.forEach((section, index) => {
    if (index > 0) y -= 8;
    addLine(section.heading, 16, true, 22);
    addLine(`Keywords: ${section.keywords.join(", ")}`, 10, false, 18);
    wrapText(section.body, 88).forEach((line) => addLine(line || " ", 11, false, line ? 15 : 8));
  });
  addPage();

  const catalog = `<< /Type /Catalog /Pages 2 0 R >>`;
  const kids = pages.map((id) => `${id} 0 R`).join(" ");
  const pageTree = `<< /Type /Pages /Kids [${kids}] /Count ${pages.length} >>`;
  const helvetica = `<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>`;
  const helveticaBold = `<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>`;
  objects.unshift(catalog, pageTree, helvetica, helveticaBold);

  let offset = 0;
  const chunks = ["%PDF-1.4\n"];
  offset += chunks[0].length;
  const xref = ["0000000000 65535 f "];
  objects.forEach((object, index) => {
    xref.push(`${String(offset).padStart(10, "0")} 00000 n `);
    const chunk = `${index + 1} 0 obj\n${object}\nendobj\n`;
    chunks.push(chunk);
    offset += chunk.length;
  });
  chunks.push(`xref\n0 ${objects.length + 1}\n${xref.join("\n")}\ntrailer << /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${offset}\n%%EOF`);
  return new Blob(chunks, { type: "application/pdf" });
};