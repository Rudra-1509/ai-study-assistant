const Header = () => {
  return (
    <header className="space-y-3">
      <div className="flex items-center gap-40">
        <img
          src="/logo.png"
          alt="MakeMeStudy logo"
          className="w-30 md:w-36 object-contain cursor-pointer"
        />
        <h1 className="text-2xl text-cyan-100 font-semibold cursor-pointer hover:[text-shadow:0_0_10px_rgba(255,255,255,0.5)] transition duration-300">
          MakeMeStudy
        </h1>
      </div>

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
