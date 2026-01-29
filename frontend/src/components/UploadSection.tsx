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
  return (
    <section className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <UploadCard
          imgSrc="/pdf-upload.png"
          type="pdf"
          onFileSelect={(file) => {
            setSelectedFile(file);
            setActiveType("pdf");
          }}
          disabled={activeType === "text" || activeType === "image"}
        />
        <UploadCard
          imgSrc="img-upload.png"
          type="image"
          onFileSelect={(file) => {
            setSelectedFile(file);
            setActiveType("image");
          }}
          disabled={activeType === "text" || activeType === "pdf"}
        />
      </div>

      <Textarea
        className="w-full min-h-35 rounded-md p-3"
        placeholder="Or paste your text here..."
        disabled={activeType === "pdf" || activeType === "image"}
        onChange={(e) => {
          setTextValue(e.target.value);
          setActiveType("text");
        }}
        value={textValue}
      />

      <Button className="block mx-auto border-2 border-black rounded-2xl mb-8 pb-7 text-cyan-200 font-semibold shadow-lg shadow-indigo-500/20 hover:cursor-pointer hover:[text-shadow:0_0_10px_rgba(255,255,255,0.7)] transition duration-300"
      disabled={(activeType==="text" && !textValue.trim()) ||
        (activeType!="text" && !selectedFile)
      }
      >
        Generate Study Material
      </Button>
    </section>
  );
};
export default UploadSection;
