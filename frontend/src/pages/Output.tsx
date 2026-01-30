import { Navigate, useLocation } from "react-router-dom";
import TitleBar from "@/components/TitleBar";
import type { StudyResponse } from "@/types/study";
import ReactMarkdown from "react-markdown";

const Output = () => {
  const { state } = useLocation();
  const result = state?.result as StudyResponse | undefined;
  if (!result) {
    return <Navigate to="/" replace />;
  }
  const mainTitle = "Generated Study Notes";
  return (
    <>
      <div className="min-h-screen flex justify-center">
        <div className="w-full max-w-3xl bg-linear-to-b from-zinc-800 to-zinc-700 px-4 pt-6 space-y-10">
          <TitleBar />
          <h1 className="text-xl text-center ml-6 text-white font-semibold mb-6 underline decoration-neutral-300">
            {mainTitle}
          </h1>

          {Object.entries(result).map(([id, topic]) => (
            <div key={id} className="bg-zinc-800 rounded-xl p-4 space-y-3">
              <h2 className="text-lg font-semibold text-white">
                Topic {parseInt(id) + 1} ·{" "}
                {topic.difficulty.charAt(0).toUpperCase() +
                  topic.difficulty.slice(1)}
              </h2>

              <div className="flex gap-2 flex-wrap">
                {topic.keywords.map((k: string) => (
                  <span
                    key={k}
                    className="px-2 py-1 text-xs bg-zinc-700 rounded-full text-yellow-200"
                  >
                    {k}
                  </span>
                ))}
              </div>

              <div className="text-zinc-300 whitespace-pre-wrap">
                <div className=" text-zinc-300 leading-relaxed">
                  <ReactMarkdown
                    components={{
                      h2: ({ children }) => (
                        <h2 className="text-xl font-semibold text-white">
                          {children}
                        </h2>
                      ),
                      strong: ({ children }) => (
                        <strong className="font-bold text-white underline underline-offset-2 decoration-white/50">
                          {children}
                        </strong>
                      ),
                      p: ({ children }) => <p>{children}</p>,
                    }}
                  >
                    {topic.explanation}
                  </ReactMarkdown>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
};

export default Output;
