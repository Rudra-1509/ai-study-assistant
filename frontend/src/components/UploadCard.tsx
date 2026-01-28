import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface UploadCardProps {
  type: "pdf" | "image";
  imgSrc: string;
}

export function UploadCard({ imgSrc, type }: UploadCardProps) {
  return (
    <label className="block cursor-pointer">
      <input
        type="file"
        className="hidden"
        accept={type === "pdf" ? "application/pdf" : "image/*"}
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) {
            console.log("Selected:", file);
          }
        }}
      />
      <Card
        className="
        group relative cursor-pointer
        transition
        border border-border
        hover:border-white/20
        hover:bg-muted/30
        rounded-xl
        overflow-hidden
        max-w-[16rem] mx-auto
      "
      >
        {/* overlay */}
        <div className="absolute inset-0 z-10 bg-linear-to-t from-black/20 via-black/5 to-transparent rounded-xl" />

        {/* image */}
        <div className="relative z-20 aspect-square overflow-hidden">
          <img
            src={imgSrc}
            alt={type}
            className="
            h-full w-full object-cover
            opacity-85
            transition-all duration-300
            group-hover:opacity-100
            group-hover:scale-[1.03]
            group-hover:drop-shadow-[0_0_18px_rgba(255,255,255,0.35)]
          "
          />
        </div>

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
            {type === "pdf"
              ? "PDF extractions are not the best FYI."
              : "Image extractions are good."}
          </CardDescription>
        </CardHeader>
      </Card>
    </label>
  );
}
