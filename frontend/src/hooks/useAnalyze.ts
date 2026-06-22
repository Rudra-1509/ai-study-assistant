import { useState } from "react";
import { analyze } from "@/api/analyze";
import type { StudyInput, StudyResponse } from "@/types/study";

interface AnalyzeResult {
  result: StudyResponse;
  duration: number;
}

const useAnalyze = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runAnalyze = async (input: StudyInput): Promise<AnalyzeResult> => {
    setLoading(true);
    setError(null);
    const startTime = performance.now();

    try {
      const result = await analyze(input);
      return {
        result,
        duration: performance.now() - startTime,
      };
    } catch (err: unknown) {
      const message =
        err instanceof Error
          ? err.message
          : String(err) || "Something went wrong";
      setError(message);
      if (err instanceof Error) throw err;
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, runAnalyze };
};

export default useAnalyze;
