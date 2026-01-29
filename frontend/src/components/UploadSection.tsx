import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { UploadCard } from "./UploadCard";

import { useState } from "react";

const UploadSection = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [activeType, setActiveType] = useState<"pdf" | "image" | "text" | null>(
    null,
  );
  const [textValue, setTextValue] = useState("");

  const resetAll = () => {
    setSelectedFile(null);
    setActiveType(null);
    setTextValue("");
  };

  return (
    <section className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <UploadCard
          imgSrc="/pdf-upload.png"
          type="pdf"
          isActive={activeType === "pdf"}
          onFileSelect={(file) => {
            setSelectedFile(file);
            setActiveType("pdf");
          }}
          disabled={activeType !==null && activeType!=="pdf"}
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
          disabled={activeType !==null && activeType!=="image"}
          onRemove={resetAll}
        />
      </div>

      <Textarea
        className="w-full min-h-35 rounded-md p-3 text-white/75"
        placeholder="Or paste your text here..."
        disabled={activeType !==null && activeType!=="text"}
        onChange={(e) => {
          setTextValue(e.target.value);
          setActiveType("text");
        }}
        value={textValue}
      />
      {activeType === "text" && (
        <div className="flex justify-end">
          <Button
            variant="ghost"
            className="text-red-400 hover:text-red-600 hover:underline decoration-red-700 hover:cursor-pointer"
            onClick={resetAll}
          >
            Clear text
          </Button>
        </div>
      )}

      <Button
        className="block mx-auto border-2 border-black rounded-2xl mb-8 pb-7 text-cyan-200 font-semibold shadow-lg shadow-indigo-500/20 hover:cursor-pointer hover:[text-shadow:0_0_10px_rgba(255,255,255,0.5)] transition duration-300"
        disabled={
           activeType===null ||
          (activeType === "text" && !textValue.trim()) ||
          (activeType != "text" && !selectedFile)
        }
      >
        Generate Study Material
      </Button>
    </section>
  );
};
export default UploadSection;
