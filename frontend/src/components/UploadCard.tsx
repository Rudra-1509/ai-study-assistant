import { useRef, useState } from "react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Card, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "./ui/button";

interface UploadCardProps {
  type: "pdf" | "image";
  imgSrc: string;
  isActive: boolean;
  onFileSelect: (file: File) => void;
  disabled: boolean;
  onRemove: () => void;
  error?: string | null;
}

export function UploadCard({ imgSrc, type, isActive, onFileSelect, disabled, onRemove, error }: UploadCardProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const accept = type === "pdf" ? "application/pdf" : "image/*";
  const label = type === "pdf" ? "PDF" : "image";

  const chooseFile = (file?: File) => {
    if (file && !disabled) onFileSelect(file);
    if (inputRef.current) inputRef.current.value = "";
    setDragging(false);
  };
  return (
    <div className={cn("block", disabled && "opacity-45")}>
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        disabled={disabled}
        accept={accept}
        aria-label={`Choose ${label} file`}
        onClick={(e) => e.stopPropagation()}
        onChange={(e) => chooseFile(e.target.files?.[0])}
      />
      <Card
        role="button"
        tabIndex={disabled || isActive ? -1 : 0}
        aria-label={`Upload ${label} by clicking or dragging a file here`}
        onKeyDown={(e) => {
          if ((e.key === "Enter" || e.key === " ") && !isActive && !disabled) inputRef.current?.click();
        }}
        onClick={() => {
          if (!isActive && !disabled) inputRef.current?.click();
        }}
        onDragOver={(e) => {
          if (disabled) return;
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          chooseFile(e.dataTransfer.files?.[0]);
        }}
        className={cn(
          "group relative transition border border-border rounded-xl overflow-hidden max-w-[16rem] mx-auto outline-none focus-visible:ring-3 focus-visible:ring-cyan-300/60",
          dragging && "border-cyan-300 bg-cyan-400/10",
          !disabled && !isActive && "hover:border-cyan-200 hover:bg-muted/30",

          disabled ? "cursor-not-allowed" : isActive ? "cursor-default" : "cursor-pointer",
        )}
      >
        <div className="absolute inset-0 z-10 pointer-events-none bg-linear-to-t from-black/20 via-black/5 to-transparent rounded-xl" />

        <div className="relative z-20 aspect-square overflow-hidden">
          <img
            src={isActive ? "/upload-done.png" : imgSrc}
            alt=""
            className={cn(
              "h-full w-full object-cover opacity-85 transition-all duration-300",
              !disabled && !isActive && ["group-hover:opacity-100", "group-hover:scale-[1.03]", "group-hover:drop-shadow-[0_0_18px_rgba(255,255,255,0.35)]"],
            )}
          />
        </div>
        <Separator className="h-px bg-white/40" />
        <CardHeader className="relative z-30 p-4">
          <div className="absolute top-3 right-3"><Badge variant="outline" className="text-white">{type.toUpperCase()}</Badge></div>
          <CardTitle className="text-white font-medium">{type === "pdf" ? "Upload PDF" : "Upload Image"}</CardTitle>

          <CardDescription className="text-sm text-white/80 mt-1">
            {isActive ? "Ready to analyze" : `Click or drop a ${label} here.`}
          </CardDescription>
          {error && <p className="text-xs text-red-300" role="alert">{error}</p>}
        </CardHeader>
        <CardFooter className="relative z-30">
          {isActive && <Button onClick={(e) => { e.stopPropagation(); onRemove(); }} className="mx-auto border rounded-full border-red-500 text-red-300 hover:bg-red-300 hover:text-red-700">Remove</Button>}
        </CardFooter>
      </Card>
    </div>
  );
}
