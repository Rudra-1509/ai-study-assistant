import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { UploadCard } from "./UploadCard";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import useAnalyze from "@/hooks/useAnalyze";
import type { StudyInput } from "@/types/study";

const progressStages = [
  "Preparing your document",
  "Running OCR and ingestion",
  "Chunking content",
  "Building embeddings",
  "Finding structure",
  "Generating study notes",
];

const UploadSection = () => {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [activeType, setActiveType] = useState<"pdf" | "image" | "text" | null>(null);
  const [textValue, setTextValue] = useState("");
  const [progressStep, setProgressStep] = useState(0);
  const [fileError, setFileError] = useState<string | null>(null);
  const [lastInput, setLastInput] = useState<StudyInput | null>(null);

  const { loading, error, runAnalyze, cancelAnalyze } = useAnalyze();

  useEffect(() => {
    if (!loading) {
      return;
    }

    const interval = window.setInterval(() => {
      setProgressStep((current) => Math.min(current + 1, progressStages.length - 2));
    }, 1200);

    return () => window.clearInterval(interval);
  }, [loading]);

    const buildInput = () => {
    if (activeType === "image" && selectedFile) return { input_type: "image" as const, file: selectedFile };
    if (activeType === "pdf" && selectedFile) return { input_type: "pdf" as const, file: selectedFile };
    if (activeType === "text" && textValue.trim()) return { input_type: "text" as const, content: textValue.trim() };
    return null;
  };

    const handleSubmit = async (input = buildInput()) => {
    if (!input) return;
    setProgressStep(0);
    setLastInput(input);
    try {
      const result = await runAnalyze(input);
      setProgressStep(progressStages.length - 1);
      navigate("/output", { state: { result: result.result, duration: result.duration } });
    } catch (err) {
      console.warn(err);
    }
  };

    const handleGenerateClick = () => {
    void handleSubmit();
    };

    const validateFile = (type: "pdf" | "image", file: File) => {
    const isValidType = type === "pdf" ? file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf") : file.type.startsWith("image/");
    if (!isValidType) return `Please choose a valid ${type === "pdf" ? "PDF" : "image"} file.`;
    if (file.size > 15 * 1024 * 1024) return "Files must be smaller than 15 MB for reliable processing.";
    return null;
  };

  const handleFileSelect = (type: "pdf" | "image", file: File) => {
    const validation = validateFile(type, file);
    setFileError(validation);
    if (validation) return;
    setSelectedFile(file);
    setActiveType(type);
  };

  const resetAll = () => {
    setSelectedFile(null);
    setActiveType(null);
    setTextValue("");
    setProgressStep(0);
    setFileError(null);
  };

    const progressPercent = useMemo(() => {
    if (!loading && progressStep === progressStages.length - 1) return 100;
    return Math.min(92, Math.round(((progressStep + 1) / progressStages.length) * 100));
  }, [loading, progressStep]);

  const selectedLabel =
    activeType === "text"
      ? `${textValue.trim().length} characters ready`
      : selectedFile
      ? `${selectedFile.name} selected`
      : "No document selected yet";

  return (
    <section id="upload" className="space-y-6" aria-labelledby="upload-heading">
      <Card className="bg-zinc-900/95 border border-white/10 shadow-xl shadow-cyan-500/10">
        <CardHeader>
          <CardTitle className="text-white text-2xl tracking-tight">
            Create a polished study summary
          </CardTitle>
          <CardDescription className="text-slate-300 leading-relaxed">
            Upload a PDF or image, or paste your text, then let the assistant analyze it through OCR, chunking, embeddings, clustering, and generation.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <UploadCard
              imgSrc="/pdf-upload.png"
              type="pdf"
              isActive={activeType === "pdf"}
              error={activeType === "pdf" ? fileError : null}
              onFileSelect={(file) => handleFileSelect("pdf", file)}
              disabled={activeType !== null && activeType !== "pdf"}
              onRemove={resetAll}
            />
            <UploadCard
              imgSrc="img-upload.png"
              type="image"
              isActive={activeType === "image"}
              error={activeType === "image" ? fileError : null}
              onFileSelect={(file) => handleFileSelect("image", file)}
              disabled={activeType !== null && activeType !== "image"}
              onRemove={resetAll}
            />
          </div>

          <div className="space-y-3">
            <Textarea
              className="w-full min-h-52 rounded-3xl p-4 text-slate-100 bg-slate-950/80 border border-white/10 focus:border-cyan-400"
              placeholder="Or paste your text here..."
              disabled={activeType !== null && activeType !== "text"}
              onChange={(e) => {
                setTextValue(e.target.value);
                setActiveType("text");
              }}
              value={textValue}
            />
            <div className="flex flex-wrap items-center justify-between gap-3 text-sm text-slate-400">
              <span>{selectedLabel}</span>
              {activeType === "text" && (
                <Button
                  variant="ghost"
                  className="text-red-300 hover:text-red-400 hover:underline"
                  onClick={resetAll}
                >
                  Clear text
                </Button>
              )}
            </div>
          </div>

          {loading && (
            <div className="rounded-3xl border border-cyan-500/20 bg-cyan-500/10 p-4">
              <div className="flex items-center justify-between text-sm text-cyan-100 mb-3">
                <span className="font-medium">Analyzing document</span>
                <span>{progressPercent}%</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-white/10" role="progressbar" aria-valuenow={progressPercent} aria-valuemin={0} aria-valuemax={100}>
                <div
                  className="h-full rounded-full bg-cyan-400 transition-all duration-500"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
              <p className="mt-3 text-sm text-slate-200">
                {loading && progressStep === progressStages.length - 2 ? "Finalizing results from the backend" : progressStages[progressStep]}
              </p>
            </div>
          )}

          {error && <div className="rounded-2xl border border-red-400/30 bg-red-500/10 p-4 text-center text-sm text-red-200" role="alert">{error}</div>}
        </CardContent>

        <CardFooter className="flex flex-col items-center gap-4 pt-4">
          <Button
            className="w-full max-w-md rounded-3xl border border-cyan-500/30 bg-cyan-500/10 text-cyan-100 shadow-lg shadow-cyan-500/10 hover:bg-cyan-500/20"
            disabled={
              loading ||
              activeType === null ||
              (activeType === "text" && !textValue.trim()) ||
              (activeType !== "text" && !selectedFile)
            }
            onClick={handleGenerateClick}
          >
            {loading ? "Analyzing content..." : "Generate Study Material"}
          </Button>
           {loading && <Button variant="ghost" className="text-slate-200" onClick={cancelAnalyze}>Cancel analysis</Button>}
          {!loading && error && lastInput && <Button variant="secondary" onClick={() => handleSubmit(lastInput)}>Retry last upload</Button>}
          <p className="text-center text-sm text-slate-400 max-w-xl">
            Once analysis completes, you can review topic summaries, difficulty levels, and export your notes as Markdown or PDF.
          </p>
        </CardFooter>
      </Card>
    </section>
  );
};
export default UploadSection;
