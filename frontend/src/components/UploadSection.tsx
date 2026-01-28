import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { UploadCard } from "./UploadCard";

const UploadSection = () => {
  return (
    <section className="space-y-6">

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <UploadCard imgSrc="/pdf-upload.png" type="pdf"/>
        <UploadCard imgSrc="img-upload.png" type="image"/>
      </div>

      <Textarea
        placeholder="Or paste your text here..."
        className="min-h-35"
      />

      <Button className="w-full">
        Generate Study Material
      </Button>

    </section>
  );
};
export default UploadSection;
