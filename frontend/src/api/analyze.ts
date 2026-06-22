const API_BASE_URL = import.meta.env.VITE_API_URL;
import type { StudyInput, StudyResponse } from "../types/study";

export async function analyze(input: StudyInput, signal?: AbortSignal): Promise<StudyResponse> {
  const formData = new FormData();

  formData.append("input_type", input.input_type);

  if (input.input_type === "text") {
    formData.append("content", input.content);
  }

  if (input.input_type === "pdf" || input.input_type === "image") {
    formData.append("file", input.file); 
  }
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    body: formData,
    signal
  });

  if (!response.ok) {
    const contentType = response.headers.get("content-type") ?? "";
    const detail = contentType.includes("application/json")
      ? JSON.stringify(await response.json())
      : await response.text();
    throw new Error(detail || `Analysis failed with status ${response.status}`);
  }

  return response.json();
}
