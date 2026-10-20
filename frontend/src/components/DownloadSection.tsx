import { Download, CheckCircle, RefreshCcw } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface DownloadSectionProps {
  jobId: string | null;
  totalContacts: number;
  totalCost: number;
  totalTime: number;
  onDownload: () => void;
  onReset: () => void;
}

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs}s`;
};

const DownloadSection = ({
  jobId,
  totalContacts,
  totalCost,
  totalTime,
  onDownload,
  onReset,
}: DownloadSectionProps) => {
  return (
    <Card className="p-8 text-center bg-brand-ocean-blue/70 backdrop-blur-sm border-brand-deck-green/40 shadow-xl">
      <div className="flex justify-center mb-4">
        <div className="bg-brand-deck-green/20 p-4 rounded-full border-2 border-brand-deck-green/40">
          <CheckCircle className="h-12 w-12 text-brand-deck-green" />
        </div>
      </div>

      <h2 className="text-2xl font-bold mb-2 text-brand-hull-white">Pipeline Complete!</h2>

      <div className="text-brand-cargo-khaki mb-6 space-y-1">
        <p>Successfully processed {totalContacts} contacts in {formatTime(totalTime)}</p>
        <p className="text-sm">Total cost: ${totalCost.toFixed(2)}</p>
      </div>

      <div className="space-y-3 max-w-md mx-auto">
        <Button onClick={onDownload} size="lg" className="w-full bg-brand-container-rust hover:bg-brand-container-rust/80 text-brand-anchor-black font-semibold shadow-lg transition-all">
          <Download className="h-5 w-5 mr-2" />
          Download CSV
        </Button>

        <p className="text-xs text-brand-cargo-khaki">
          Ready for import to Instantly.ai or LinkedIn automation tools
        </p>

        <Button onClick={onReset} variant="outline" className="w-full border-brand-hull-white/30 text-brand-hull-white hover:bg-brand-hull-white/10">
          <RefreshCcw className="h-4 w-4 mr-2" />
          Run Another Pipeline
        </Button>
      </div>
    </Card>
  );
};

export default DownloadSection;
