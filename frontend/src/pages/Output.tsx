import { Navigate, useLocation } from "react-router-dom";
import TitleBar from "@/components/TitleBar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import type { StudyResponse } from "@/types/study";
import ReactMarkdown from "react-markdown";

const cleanMarkdown = (text: string) => {
  return text
    .replace(/\r/g, "")
    .replace(/\u2022/g, "-") // normalize bullet dots
    .replace(/\*\s/g, "- ") // normalize weird bullets
    .replace(/ +/g, " ") // remove extra spaces
    .trim();
};

const summarizeDifficulty = (result: StudyResponse) => {
  return Object.values(result).reduce<Record<string, number>>((acc, topic) => {
    acc[topic.difficulty] = (acc[topic.difficulty] ?? 0) + 1;
    return acc;
  }, {});
};

const formatWordCount = (text: string) => text.trim().split(/\s+/).filter(Boolean).length;

const buildMarkdown = (result: StudyResponse, durationSeconds: number) => {
  const lines = [
    "# Generated Study Notes",
    "",
    `Processed in ${durationSeconds.toFixed(1)} seconds`,
    `Topics: ${Object.keys(result).length}`,
    `Total words: ${Object.values(result).reduce(
      (sum, topic) => sum + formatWordCount(topic.explanation),
      0,
    )}`,
    "",
  ];

  Object.entries(result).forEach(([id, topic]) => {
    lines.push(`## Topic ${parseInt(id, 10) + 1}: ${topic.difficulty.toUpperCase()}`);
    lines.push(`**Keywords:** ${topic.keywords.join(", ")}`);
    lines.push("");
    lines.push(topic.explanation.trim());
    lines.push("");
  });

  return lines.join("\n\n");
};

const Output = () => {
  const { state } = useLocation();
  const result = state?.result as StudyResponse | undefined;
  const duration = typeof state?.duration === "number" ? state.duration : 0;

  if (!result) {
    return <Navigate to="/" replace />;
  }

  const topicCount = Object.keys(result).length;
  const totalWords = Object.values(result).reduce(
    (sum, topic) => sum + formatWordCount(topic.explanation),
    0,
  );
  const difficultyCounts = summarizeDifficulty(result);

  const downloadMarkdown = () => {
    const markdown = buildMarkdown(result, duration / 1000);
    const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "study-notes.md";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  };

  const exportPDF = () => {
    const printWindow = window.open("", "_blank");
    if (!printWindow) return;

    const title = "Generated Study Notes";
    const content = Object.entries(result)
      .map(([id, topic]) => {
        const keywords = topic.keywords.map((word) => `• ${word}`).join("\n");
        return `
          <section style="margin-bottom:1.5rem;">
            <h2 style="font-size:18px;margin:0 0 0.5rem;color:#111;">Topic ${parseInt(id, 10) + 1} · ${topic.difficulty.toUpperCase()}</h2>
            <div style="margin-bottom:0.75rem;color:#0f172a;font-size:14px;">
              Keywords: ${topic.keywords.join(", ")}
            </div>
            <div style="font-size:14px;line-height:1.7;color:#202020;white-space:pre-wrap;">${topic.explanation}</div>
          </section>`;
      })
      .join("");

    printWindow.document.write(`
      <html>
        <head>
          <title>${title}</title>
          <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; padding: 24px; background: #fff; color: #111; }
            h1 { margin-bottom: 0.5rem; font-size: 28px; }
            .meta { margin-bottom: 1.5rem; color: #475569; font-size: 14px; }
            h2 { margin: 1.5rem 0 0.5rem; font-size: 18px; }
            ul { margin: 0.5rem 0 1rem 1.2rem; }
            li { margin-bottom: 0.4rem; }
            p { margin: 0 0 1rem 0; }
          </style>
        </head>
        <body>
          <h1>${title}</h1>
          <div class="meta">Processed in ${(duration / 1000).toFixed(1)} seconds · ${topicCount} topics · ${totalWords} total words</div>
          ${content}
        </body>
      </html>
    `);

    printWindow.document.close();
    printWindow.focus();
    printWindow.print();
  };

  const mainTitle = "Generated Study Notes";

  return (
    <>
      <div className="min-h-screen flex justify-center">
        <div className="w-full max-w-4xl bg-linear-to-b from-zinc-800 to-zinc-700 px-4 pt-6 pb-12 space-y-10">
          <TitleBar />

          <Card className="border border-white/10 bg-zinc-900/95 shadow-xl shadow-cyan-500/10">
            <CardHeader>
              <div>
                <CardTitle className="text-3xl text-white tracking-tight">
                  {mainTitle}
                </CardTitle>
                <CardDescription className="text-slate-300 mt-2">
                  Review the AI-generated study notes, difficulty levels, and export them for sharing.
                </CardDescription>
              </div>
              <div className="flex flex-wrap items-center gap-3">
                <Button variant="secondary" onClick={downloadMarkdown}>
                  Export Markdown
                </Button>
                <Button variant="default" onClick={exportPDF}>
                  Export as PDF
                </Button>
              </div>
            </CardHeader>

            <CardContent className="grid gap-4 md:grid-cols-3 md:items-stretch">
              <div className="rounded-3xl border border-white/10 bg-slate-950/80 p-4">
                <p className="text-sm uppercase tracking-[0.3em] text-slate-400 mb-2">Processing time</p>
                <p className="text-3xl font-semibold text-white">{(duration / 1000).toFixed(1)}s</p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-slate-950/80 p-4">
                <p className="text-sm uppercase tracking-[0.3em] text-slate-400 mb-2">Topics generated</p>
                <p className="text-3xl font-semibold text-white">{topicCount}</p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-slate-950/80 p-4">
                <p className="text-sm uppercase tracking-[0.3em] text-slate-400 mb-2">Total words</p>
                <p className="text-3xl font-semibold text-white">{totalWords}</p>
              </div>
            </CardContent>

            <CardFooter className="flex flex-wrap gap-3 text-sm text-slate-300">
              {Object.entries(difficultyCounts).map(([level, count]) => (
                <span
                  key={level}
                  className="rounded-full border border-white/10 bg-white/5 px-3 py-2"
                >
                  {level.charAt(0).toUpperCase() + level.slice(1)}: {count}
                </span>
              ))}
            </CardFooter>
          </Card>

          {Object.entries(result).map(([id, topic]) => (
            <div key={id} className="bg-zinc-900 rounded-3xl p-6 space-y-4 border border-white/5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 className="text-2xl font-semibold text-white">
                    Topic {parseInt(id, 10) + 1}
                  </h2>
                  <p className="text-sm text-slate-400 mt-1">
                    Difficulty: {topic.difficulty.charAt(0).toUpperCase() + topic.difficulty.slice(1)}
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {topic.keywords.map((k: string) => (
                    <span
                      key={k}
                      className="rounded-full bg-cyan-500/10 px-3 py-1 text-xs font-medium text-cyan-200"
                    >
                      {k}
                    </span>
                  ))}
                </div>
              </div>

              <div className="text-slate-200 leading-relaxed">
                <ReactMarkdown
                  components={{
                    h2: ({ children }) => (
                      <h2 className="text-xl font-semibold text-white mt-6 mb-2">
                        {children}
                      </h2>
                    ),
                    p: ({ children }) => (
                      <p className="my-3 leading-relaxed text-slate-200">
                        {children}
                      </p>
                    ),
                    strong: ({ children }) => (
                      <strong className="font-semibold text-white">
                        {children}
                      </strong>
                    ),
                    ul: ({ children }) => (
                      <ul className="list-disc ml-6 my-2 space-y-1 text-slate-200">
                        {children}
                      </ul>
                    ),
                    ol: ({ children }) => (
                      <ol className="list-decimal ml-6 my-2 space-y-1 text-slate-200">
                        {children}
                      </ol>
                    ),
                    li: ({ children }) => (
                      <li className="leading-relaxed">{children}</li>
                    ),
                  }}
                >
                  {cleanMarkdown(topic.explanation)}
                </ReactMarkdown>
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
};

export default Output;
