import { Navbar } from "@/components/Navbar";
import { Hero } from "@/components/Hero";
import { StatsFlow } from "@/components/StatsFlow";
import { PipelineSteps } from "@/components/PipelineSteps";
import { ResultsSection } from "@/components/ResultsSection";
import { GeneMap } from "@/components/GeneMap";
import { Downloads } from "@/components/Downloads";
import { About } from "@/components/About";
import { Footer } from "@/components/Footer";
import { PresentationBanner } from "@/components/PresentationBanner";
import { data } from "@/lib/data";

export default function Home() {
  return (
    <main className="relative z-10">
      <Navbar />
      <PresentationBanner />
      <Hero data={data} />
      <StatsFlow data={data} />
      <PipelineSteps data={data} />
      <ResultsSection data={data} />
      <GeneMap data={data} />
      <Downloads />
      <About />
      <Footer />
    </main>
  );
}
