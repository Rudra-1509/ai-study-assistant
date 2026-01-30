import { useLocation, Navigate } from "react-router-dom";
import TitleBar from "@/components/TitleBar";

const Output = () => {
  const location = useLocation();
  const result = location.state?.result;
  if (!result) {
    return <Navigate to="/" replace/>
  }
  const mainTitle = "Generated Study Notes";
  return (
    <>
      <div className="min-h-screen flex justify-center">
        <div className="w-full max-w-3xl bg-linear-to-b from-zinc-800 to-zinc-700 px-4 pt-6 space-y-10">
          <TitleBar />
          <h1 className="text-xl text-center text-white font-semibold mb-6 underline decoration-neutral-300">
            {mainTitle}
          </h1>

          <pre className="text-zinc-300 text-sm whitespace-pre-wrap">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      </div>
    </>
  );
};

export default Output;
