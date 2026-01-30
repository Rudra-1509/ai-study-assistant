import { useState } from "react";
import { analyze } from "@/api/analyze";
import type { StudyInput } from "@/types/study";
const useAnalyze = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runAnalyze = async (input: StudyInput) => {
    setLoading(true);
    setError(null);
    try {
      const result = await analyze(input);
      return result;
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
  return {loading, error, runAnalyze};
};

export default useAnalyze;
