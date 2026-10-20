import { useState } from "react";
import { FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import DocsModal from "./DocsModal";
import ApiStatusIndicator from "./ApiStatusIndicator";

const Header = () => {
  const [docsOpen, setDocsOpen] = useState(false);

  return (
    <>
      <header className="border-b border-brand-ocean-blue/20 bg-gradient-to-r from-brand-ocean-blue to-brand-ocean-blue/90 sticky top-0 z-50 shadow-lg">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* Waypoint Icon */}
              <div className="bg-brand-hull-white/10 p-2 rounded-lg backdrop-blur-sm border border-brand-hull-white/20">
                <img
                  src="/logos/icon-white.svg"
                  alt="Waypoint"
                  className="h-8 w-8"
                />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-tight text-brand-hull-white">
                  Prospector
                </h1>
                <p className="text-xs text-brand-container-rust font-medium">
                  AI-Powered B2B Lead Generation for Logistics
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <ApiStatusIndicator />
              <Button
                size="sm"
                onClick={() => setDocsOpen(true)}
                className="bg-brand-container-rust/90 hover:bg-brand-container-rust text-brand-anchor-black font-semibold border-2 border-brand-container-rust shadow-lg transition-all"
              >
                <FileText className="h-4 w-4 mr-2" />
                Documentation
              </Button>
            </div>
          </div>
        </div>
      </header>

      <DocsModal open={docsOpen} onOpenChange={setDocsOpen} />
    </>
  );
};

export default Header;
