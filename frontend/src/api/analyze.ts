import type { StudyInput, StudyResponse } from "../types/study";
const API_BASE_URL = "http://127.0.0.1:8000";

export async function analyze(input: StudyInput): Promise<StudyResponse> {
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
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || "Failed to analyze input");
  }

  return response.json();
}
