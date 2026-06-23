import { useMemo, useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Check, Clipboard, Download, FileText } from "lucide-react";

import TitleBar from "@/components/TitleBar";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { generateStudyNotesPdf } from "@/lib/pdf";
import type { StudyResponse } from "@/types/study";

const cleanMarkdown = (text: string) =>
  text
    .replace(/\r/g, "")
    .replace(/\\n/g, "\n")
    .replace(/\u2022/g, "-")
    .replace(/^\s*\*\s+/gm, "- ")
    .replace(/[^\S\n]+/g, " ")
    .replace(/^[^\S\n]*(#{1,6})[^\S\n]+/gm, "$1 ")
    .trim();

const formatWordCount = (text: string) =>
  text.trim().split(/\s+/).filter(Boolean).length;

const titleFor = (id: string) => `Topic ${parseInt(id, 10) + 1}`;

const summarizeDifficulty = (result: StudyResponse) =>
  Object.values(result).reduce<Record<string, number>>((acc, topic) => {
    acc[topic.difficulty] = (acc[topic.difficulty] ?? 0) + 1;
    return acc;
  }, {});

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
    lines.push(`## ${titleFor(id)}: ${topic.difficulty.toUpperCase()}`);
    lines.push(
      `**Keywords:** ${topic.keywords.join(", ")}`,
      "",
      topic.explanation.trim(),
      "",
    );
  });

  return lines.join("\n\n");
};

const Output = () => {
  const location = useLocation();
  const state = location.state as {
    result?: StudyResponse;
    duration?: number;
  } | null;

  const result = state?.result;
  const duration = typeof state?.duration === "number" ? state.duration : 0;

  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [openTopics, setOpenTopics] = useState<Record<string, boolean>>({});

  const safeResult = useMemo(() => result ?? {}, [result]);
  const entries = Object.entries(safeResult);
  const topicCount = entries.length;

  const totalWords = entries.reduce(
    (sum, [, topic]) => sum + formatWordCount(topic.explanation),
    0,
  );

  const difficultyCounts = summarizeDifficulty(safeResult);

  const markdown = useMemo(
    () => buildMarkdown(safeResult, duration / 1000),
    [safeResult, duration],
  );

  if (!result) return <Navigate to="/" replace />;

  const downloadBlob = (blob: Blob, filename: string) => {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  };

  const downloadMarkdown = () =>
    downloadBlob(
      new Blob([markdown], { type: "text/markdown;charset=utf-8" }),
      "study-notes.md",
    );

  const exportPDF = () =>
    downloadBlob(
      generateStudyNotesPdf({
        title: "Generated Study Notes",
        meta: `Processed in ${(duration / 1000).toFixed(1)} seconds · ${topicCount} topics · ${totalWords} total words`,
        sections: entries.map(([id, topic]) => ({
          heading: `${titleFor(id)} · ${topic.difficulty.toUpperCase()}`,
          keywords: topic.keywords,
          body: cleanMarkdown(topic.explanation),
        })),
      }),
      "study-notes.pdf",
    );

  const copyTopic = async (id: string, text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 1600);
    } catch {
      alert("Unable to copy to clipboard.");
    }
  };

  const scrollToTopic = (id: string) => {
    const el = document.getElementById(`topic-${id}`);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_right,rgba(34,211,238,0.16),transparent_32%),linear-gradient(135deg,#0f172a,#27272a_55%,#111827)] px-4 py-6 sm:py-10">
      <main className="mx-auto w-full max-w-6xl space-y-8">
        <TitleBar />

        <Card className="border border-white/10 bg-zinc-900/95 shadow-xl shadow-cyan-500/10">
          <CardHeader className="gap-5 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <CardTitle className="text-3xl tracking-tight text-white">
                Generated Study Notes
              </CardTitle>
              <CardDescription className="mt-2 text-slate-300">
                Navigate topics, copy sections, and export browser-independent
                PDF or Markdown files.
              </CardDescription>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <Button
                variant="secondary"
                onClick={downloadMarkdown}
                className="cursor-pointer text-white border border-cyan-400/30 bg-cyan-500/10 hover:bg-cyan-500/10 hover:text-white hover:shadow-[0_0_18px_rgba(34,211,238,0.45)] transition-all duration-300"
              >
                <FileText className="mr-2 h-4 w-4" />
                Export Markdown
              </Button>

              <Button
                onClick={exportPDF}
                className="cursor-pointer text-white border border-cyan-400/30 bg-cyan-500/10 hover:bg-cyan-500/20 hover:text-white hover:shadow-[0_0_18px_rgba(34,211,238,0.45)] transition-all duration-300"
              >
                <Download className="mr-2 h-4 w-4" />
                Download PDF
              </Button>
            </div>
          </CardHeader>

          <CardContent className="grid gap-4 md:grid-cols-3">
            {[
              ["Processing time", `${(duration / 1000).toFixed(1)}s`],
              ["Topics generated", topicCount],
              ["Total words", totalWords],
            ].map(([label, value]) => (
              <div
                key={label}
                className="rounded-3xl border border-white/10 bg-slate-950/80 p-4"
              >
                <p className="mb-2 text-sm uppercase tracking-[0.3em] text-slate-400">
                  {label}
                </p>
                <p className="text-3xl font-semibold text-white">{value}</p>
              </div>
            ))}
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

        <div className="grid gap-6 lg:grid-cols-[260px_1fr] lg:items-start">
          {/* Sidebar / Contents */}
          <aside className="sticky top-4 rounded-3xl border border-white/10 bg-zinc-900/90 p-5 text-slate-200 shadow-xl shadow-cyan-950/20">
            <h2 className="text-lg font-semibold text-white">Contents</h2>
            <p className="mt-1 text-sm text-slate-400">
              Jump to any generated topic.
            </p>

            <nav
              className="mt-4 space-y-2"
              aria-label="Study notes table of contents"
            >
              {entries.map(([id, topic]) => (
                <button
                  key={id}
                  type="button"
                  onClick={() => scrollToTopic(id)}
                  className="block w-full rounded-2xl px-3 py-2 text-left text-sm hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300"
                >
                  {titleFor(id)}{" "}
                  <span className="text-slate-400">· {topic.difficulty}</span>
                </button>
              ))}
            </nav>
          </aside>

          {/* Topic Sections */}
          <section className="space-y-5" aria-label="Generated topic sections">
            {entries.map(([id, topic]) => {
              const isOpen = openTopics[id] ?? true;

              const topicText = `${titleFor(id)}
Keywords: ${topic.keywords.join(", ")}

${cleanMarkdown(topic.explanation)}`;

              return (
                <article
                  id={`topic-${id}`}
                  key={id}
                  className="scroll-mt-6 rounded-3xl border border-white/5 bg-zinc-900 p-5 shadow-lg shadow-black/20 sm:p-6"
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <button
                      className="text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300"
                      onClick={() =>
                        setOpenTopics((current) => ({
                          ...current,
                          [id]: !isOpen,
                        }))
                      }
                      aria-expanded={isOpen}
                      aria-controls={`topic-panel-${id}`}
                    >
                      <h2 className="text-2xl font-semibold text-white">
                        {titleFor(id)}
                      </h2>
                      <p className="mt-1 text-sm text-slate-400">
                        Difficulty:{" "}
                        {topic.difficulty.charAt(0).toUpperCase() +
                          topic.difficulty.slice(1)}{" "}
                        · {formatWordCount(topic.explanation)} words
                      </p>
                    </button>

                    <Button
                      variant="secondary"
                      size="sm"
                      className="bg-white text-black hover:bg-gray-100 border border-gray-300 cursor-pointer"
                      onClick={() => copyTopic(id, topicText)}
                    >
                      {copiedId === id ? (
                        <Check className="mr-2 h-4 w-4" />
                      ) : (
                        <Clipboard className="mr-2 h-4 w-4" />
                      )}
                      {copiedId === id ? "Copied" : "Copy"}
                    </Button>
                  </div>

                  <div className="mt-4 flex flex-wrap gap-2">
                    {topic.keywords.map((k) => (
                      <span
                        key={k}
                        className="rounded-full bg-cyan-500/10 px-3 py-1 text-xs font-medium text-cyan-200"
                      >
                        {k}
                      </span>
                    ))}
                  </div>

                  {isOpen && (
                    <div
                      id={`topic-panel-${id}`}
                      className="prose prose-invert mt-5 max-w-none text-slate-200 prose-pre:overflow-x-auto prose-pre:rounded-2xl prose-pre:border prose-pre:border-cyan-300/20 prose-pre:bg-slate-950 prose-pre:p-4 prose-code:text-cyan-100"
                    >
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          h2: ({ children }) => (
                            <h2 className="mb-3 mt-7 border-b border-cyan-300/20 pb-2 text-2xl font-semibold tracking-tight text-cyan-100 first:mt-0">
                              {children}
                            </h2>
                          ),
                          h3: ({ children }) => (
                            <h3 className="mb-2 mt-5 text-xl font-semibold text-white">
                              {children}
                            </h3>
                          ),
                        }}
                      >
                        {cleanMarkdown(topic.explanation)}
                      </ReactMarkdown>
                    </div>
                  )}
                </article>
              );
            })}
          </section>
        </div>
      </main>
    </div>
  );
};

export default Output;
