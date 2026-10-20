import { useEffect, useState } from "react";
import { CheckCircle2, XCircle, Loader2, Plug } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";

interface ApiStatus {
  name: string;
  description: string;
  connected: boolean;
  required: boolean;
}

interface ApiStatusData {
  apollo: ApiStatus;
  apify: ApiStatus;
  perplexity: ApiStatus;
  anthropic: ApiStatus;
  openai: ApiStatus;
  instantly: ApiStatus;
}

const API_BASE = "http://localhost:8001";

export default function ApiStatusIndicator() {
  const [apiStatus, setApiStatus] = useState<ApiStatusData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchApiStatus = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/status`);
        const data = await response.json();
        setApiStatus(data.apis);
        setLoading(false);
      } catch (error) {
        console.error("Failed to fetch API status:", error);
        setLoading(false);
      }
    };

    // Fetch immediately
    fetchApiStatus();

    // Refresh every 30 seconds
    const interval = setInterval(fetchApiStatus, 30000);

    return () => clearInterval(interval);
  }, []);

  if (loading || !apiStatus) {
    return (
      <Button
        size="sm"
        variant="ghost"
        className="text-brand-hull-white/70 hover:text-brand-hull-white hover:bg-brand-hull-white/10"
        disabled
      >
        <Loader2 className="h-4 w-4 animate-spin" />
      </Button>
    );
  }

  const apis = Object.entries(apiStatus);
  const allConnected = apis.filter(([_, api]) => api.required).every(([_, api]) => api.connected);
  const connectedCount = apis.filter(([_, api]) => api.connected).length;

  return (
    <HoverCard openDelay={0}>
      <HoverCardTrigger asChild>
        <Button
          size="sm"
          variant="ghost"
          className="text-brand-hull-white/70 hover:text-brand-hull-white hover:bg-brand-hull-white/10"
        >
          {allConnected ? (
            <CheckCircle2 className="h-4 w-4 text-green-400" />
          ) : (
            <XCircle className="h-4 w-4 text-red-400" />
          )}
          <span className="ml-2 text-xs font-medium">
            {connectedCount}/{apis.length}
          </span>
        </Button>
      </HoverCardTrigger>
      <HoverCardContent className="w-80 p-4" side="bottom" align="end">
        <div className="space-y-3">
          <div className="flex items-center justify-between border-b pb-2">
            <h4 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <Plug className="h-4 w-4" />
              API Connections
            </h4>
            {allConnected ? (
              <span className="text-xs text-green-600 font-medium">All Connected</span>
            ) : (
              <span className="text-xs text-red-600 font-medium">Missing Keys</span>
            )}
          </div>

          <div className="space-y-2">
            {apis.map(([key, api]) => (
              <div key={key} className="flex items-center justify-between text-xs py-1">
                <div className="flex flex-col gap-0.5">
                  <span className="text-gray-700 font-medium">
                    {api.name}
                  </span>
                  <span className="text-gray-500 text-[10px]">
                    {api.description}
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  {api.connected ? (
                    <>
                      <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />
                      <span className="text-green-600 font-medium">Connected</span>
                    </>
                  ) : (
                    <>
                      <XCircle className="h-3.5 w-3.5 text-red-500" />
                      <span className="text-red-600 font-medium">Missing</span>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </HoverCardContent>
    </HoverCard>
  );
}
