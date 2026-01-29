import { useRef } from "react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "./ui/button";
interface UploadCardProps {
  type: "pdf" | "image";
  imgSrc: string;
  isActive: boolean;
  onFileSelect: (file: File) => void;
  disabled: boolean;
  onRemove: () => void;
}

export function UploadCard({
  imgSrc,
  type,
  isActive,
  onFileSelect,
  disabled,
  onRemove,
}: UploadCardProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  return (
    <div
      className={`block 
      ${disabled ? "opacity-45" : ""}
    `}
    >
      <input
        ref={inputRef}
        key={isActive ? "active" : "inactive"}
        type="file"
        className="hidden"
        disabled={disabled}
        accept={type === "pdf" ? "application/pdf" : "image/*"}
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) {
            onFileSelect(file);
          }
        }}
      />
      <Card
        onClick={() => {
          if (!isActive && !disabled) {
            inputRef.current?.click();
          }
        }}
        className={cn(
          "group relative transition border border-border rounded-xl overflow-hidden max-w-[16rem] mx-auto",
          !disabled && !isActive && "hover:border-white/20 hover:bg-muted/30",

          // cursor states
          disabled
            ? "cursor-not-allowed"
            : isActive
              ? "cursor-default"
              : "cursor-pointer",
        )}
      >
        {/* overlay */}
        <div className="absolute inset-0 z-10 pointer-events-none bg-linear-to-t from-black/20 via-black/5 to-transparent rounded-xl" />

        {/* image */}
        <div className="relative z-20 aspect-square overflow-hidden">
          <img
            src={isActive ? "/upload-done.png" : imgSrc}
            alt={type}
            className={cn(
              "h-full w-full object-cover opacity-85 transition-all duration-300",
              !disabled &&
                !isActive && [
                  "group-hover:opacity-100",
                  "group-hover:scale-[1.03]",
                  "group-hover:drop-shadow-[0_0_18px_rgba(255,255,255,0.35)]",
                ],
            )}
          />
        </div>
        <Separator className="h-px bg-white/40" />
        <CardHeader className="relative z-30 p-4">
          <div className="absolute top-3 right-3">
            <Badge variant="outline" className="text-white">
              {type.toUpperCase()}
            </Badge>
          </div>

          <CardTitle className="text-white font-medium">
            {type === "pdf" ? "Upload PDF" : "Upload Image"}
          </CardTitle>

          <CardDescription className="text-sm text-white/80 mt-1">
            {isActive
              ? "Upload Done"
              : type === "pdf"
                ? "PDF extractions are not the best FYI."
                : "Image extractions are good."}
          </CardDescription>
        </CardHeader>
        <CardFooter className="relative z-30">
          {isActive && (
            <Button
              onClick={(e) => {
                e.stopPropagation();
                onRemove();
              }}
              className="mx-auto border rounded-full border-red-500 text-red-400 pb-3 hover:bg-red-300 hover:text-red-600 hover:cursor-pointer"
            >
              Remove X
            </Button>
          )}
        </CardFooter>
      </Card>
    </div>
  );
}
