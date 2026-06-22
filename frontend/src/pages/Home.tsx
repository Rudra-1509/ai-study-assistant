import Header from "@/components/Header";
import UploadSection from "@/components/UploadSection";

const Home = () => {
  return (
        <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(34,211,238,0.20),transparent_35%),linear-gradient(135deg,#0f172a,#27272a_55%,#111827)] px-4 py-6 sm:py-10">
      <main className="mx-auto w-full max-w-5xl space-y-8">
        <Header />
        <UploadSection />
      </main>
    </div>
  );
};

export default Home;
