import TitleBar from "./TitleBar";

const Header = () => {
  return (
    <header className="space-y-3">
      <TitleBar/>
      <ul className="max-w-xl space-y-1 text-sm text-muted-foreground text-cyan-50 list-disc pl-5">
        <li>Upload text, PDFs, or images</li>
        <li>Only one document is allowed</li>
        <li>We analyze your material and extract key topics</li>
        <li>Generate structured study content for effective learning</li>
      </ul>
    </header>
  );
};

export default Header;
