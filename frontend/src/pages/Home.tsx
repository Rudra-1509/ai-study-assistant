import Header from "@/components/Header";
import UploadSection from "@/components/UploadSection";

const Home = () => {
  return (
    <>
      <div className="min-h-screen flex justify-center">
        <div className="w-full max-w-3xl bg-linear-to-b from-zinc-800 to-zinc-700 px-4 pt-6 space-y-10">
          <Header />
          <UploadSection/>
        </div>
      </div>
    </>
  );
};

export default Home;
