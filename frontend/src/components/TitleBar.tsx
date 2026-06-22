import { useNavigate } from "react-router-dom";

const TitleBar = () => {
  const navigate = useNavigate();
  return (
        <div className="flex items-center justify-between gap-4">
      <button className="flex items-center gap-3 rounded-full focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-cyan-300/60" onClick={() => navigate("/")} aria-label="Go to MakeMeStudy home">
        <img src="/logo.png" alt="" className="w-24 object-contain sm:w-30 cursor-pointer" />
        <span className="text-xl font-bold tracking-tight text-cyan-100 sm:text-2xl cursor-pointer">MakeMeStudy</span>
      </button>
    </div>
  );
};

export default TitleBar;
