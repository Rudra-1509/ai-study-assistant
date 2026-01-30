const TitleBar = () => {
  return (
    <div className="flex items-center gap-40">
      <img
        src="/logo.png"
        alt="MakeMeStudy logo"
        className="w-30 md:w-36 object-contain cursor-pointer"
        onClick={() => window.location.reload()}
      />
      <h1
        className="text-2xl text-cyan-100 font-semibold cursor-pointer hover:[text-shadow:0_0_10px_rgba(255,255,255,0.5)] transition duration-300"
        onClick={() => window.location.reload()}
      >
        MakeMeStudy
      </h1>
    </div>
  );
};

export default TitleBar;
