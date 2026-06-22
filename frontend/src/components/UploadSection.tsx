import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { UploadCard } from "./UploadCard";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import useAnalyze from "@/hooks/useAnalyze";

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

  const { loading, error, runAnalyze } = useAnalyze();

  useEffect(() => {
    if (!loading) {
      return;
    }

    const interval = window.setInterval(() => {
      setProgressStep((current) => Math.min(current + 1, progressStages.length - 1));
    }, 1200);

    return () => window.clearInterval(interval);
  }, [loading]);

  const handleSubmit = async () => {
    if (!activeType) return;
    setProgressStep(0);
    try{
          let result;

    if (activeType === "image" && selectedFile) {
      result = await runAnalyze({
        input_type: "image",
        file: selectedFile,
      });
    } else if (activeType === "pdf" && selectedFile) {
      result = await runAnalyze({
        input_type: "pdf",
        file: selectedFile,
      });
    } else if (activeType === "text" && textValue.trim()) {
      result = await runAnalyze({
        input_type: "text",
        content: textValue,
      });
    }

    if (result) {
      navigate("/output", { state: { result: result.result, duration: result.duration } });
    }
    }
    catch(err){
      console.log(err);
    }
  };

  const resetAll = () => {
    setSelectedFile(null);
    setActiveType(null);
    setTextValue("");
    setProgressStep(0);
  };

  const progressPercent = Math.round(
    (progressStep / Math.max(progressStages.length - 1, 1)) * 100,
  );

  const selectedLabel =
    activeType === "text"
      ? `${textValue.trim().length} characters ready`
      : selectedFile
      ? `${selectedFile.name} selected`
      : "No document selected yet";

  return (
    <section className="space-y-6">
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
              onFileSelect={(file) => {
                setSelectedFile(file);
                setActiveType("pdf");
              }}
              disabled={activeType !== null && activeType !== "pdf"}
              onRemove={resetAll}
            />
            <UploadCard
              imgSrc="img-upload.png"
              type="image"
              isActive={activeType === "image"}
              onFileSelect={(file) => {
                setSelectedFile(file);
                setActiveType("image");
              }}
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
              <div className="h-2 overflow-hidden rounded-full bg-white/10">
                <div
                  className="h-full rounded-full bg-cyan-400 transition-all duration-500"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
              <p className="mt-3 text-sm text-slate-200">
                {progressStages[progressStep]}
              </p>
            </div>
          )}

          {error && <p className="text-center text-red-400 text-sm">{error}</p>}
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
            onClick={handleSubmit}
          >
            {loading ? "Analyzing content..." : "Generate Study Material"}
          </Button>
          <p className="text-center text-sm text-slate-400 max-w-xl">
            Once analysis completes, you can review topic summaries, difficulty levels, and export your notes as Markdown or PDF.
          </p>
        </CardFooter>
      </Card>
    </section>
  );
};
export default UploadSection;
