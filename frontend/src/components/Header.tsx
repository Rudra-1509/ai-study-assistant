import { ArrowRight, CheckCircle2 } from "lucide-react";
import TitleBar from "./TitleBar";
import { Button } from "./ui/button";

const Header = () => {
  return (
    <header className="space-y-8 rounded-4xl border border-white/10 bg-white/3 p-5 shadow-2xl shadow-cyan-950/30 sm:p-8">
      <TitleBar />
      <div className="grid gap-8 lg:grid-cols-[1.25fr_0.75fr] lg:items-end">
        <div className="space-y-5">
          <p className="text-sm font-semibold uppercase tracking-[0.35em] text-cyan-200">AI study companion</p>
          <h1 className="text-4xl font-black leading-tight tracking-tight text-white sm:text-5xl">
            Turn dense notes into clear, exportable study guides.
          </h1>
          <p className="max-w-2xl text-base leading-7 text-slate-300 sm:text-lg">
            Upload text, PDFs, or images and get structured topics, keywords, difficulty cues, and polished notes ready for review.
          </p>
          <Button asChild className="rounded-full bg-cyan-300 px-6 text-slate-950 hover:bg-cyan-200">
            <a href="#upload">Create study material <ArrowRight aria-hidden="true" /></a>
          </Button>
        </div>
        <ul className="space-y-3 rounded-3xl border border-cyan-300/20 bg-slate-950/50 p-5 text-sm text-cyan-50">
          {["One document at a time", "OCR and topic extraction", "Markdown and PDF exports", "Long-note navigation tools"].map((item) => (
            <li key={item} className="flex items-center gap-3"><CheckCircle2 className="size-4 text-cyan-300" aria-hidden="true" />{item}</li>
          ))}
        </ul>
      </div>
    </header>
  );
};

export default Header;
