import { useRef, useState } from "react";
import { analyze } from "@/api/analyze";
import type { StudyInput, StudyResponse } from "@/types/study";

interface AnalyzeResult {
  result: StudyResponse;
  duration: number;
}

const friendlyError = (err: unknown) => {
  if (err instanceof DOMException && err.name === "AbortError") {
    return "Analysis was canceled. You can adjust your upload and try again.";
  }
  const raw = err instanceof Error ? err.message : String(err || "");
  if (/ocr|image|pdf|parse|extract/i.test(raw)) {
    return "We couldn't read enough text from that file. Try a clearer scan, a smaller PDF, or paste the text directly.";
  }
  if (/api|network|fetch|failed|500|502|503|504/i.test(raw)) {
    return "The study generation service did not respond successfully. Please retry in a moment.";
  }
  return raw || "Something went wrong while analyzing your material.";
};

const useAnalyze = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const controllerRef = useRef<AbortController | null>(null);
  const cancelAnalyze = () => {
    controllerRef.current?.abort();
  };

  const runAnalyze = async (input: StudyInput): Promise<AnalyzeResult> => {
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    setLoading(true);
    setError(null);
    const startTime = performance.now();

    try {
      const result = await analyze(input, controller.signal);
      return { result, duration: performance.now() - startTime };
    } catch (err: unknown) {
      const message = friendlyError(err);
      setError(message);
      throw new Error(message);
    } finally {
      if (controllerRef.current === controller) {
        controllerRef.current = null;
        setLoading(false);
      }
    }
  };

  return { loading, error, runAnalyze, cancelAnalyze };
};

export default useAnalyze;
