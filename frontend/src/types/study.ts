export type Difficulty="easy"|"medium"|"hard";
export type InputType="text"|"pdf"|"img";

export interface TextInput {
  input_type: "text";
  content: string;
}

export interface FileInput {
  input_type: "pdf" | "img";
  file: File;
}

export type StudyInput=TextInput|FileInput;

export interface TopicResult {
  difficulty: Difficulty;
  keywords: string[];
  explanation: string;
}

export type StudyResponse = Record<string, TopicResult>;