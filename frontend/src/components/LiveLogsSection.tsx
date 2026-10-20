import { useEffect, useRef, useState } from "react";
import { ScrollText, CheckCircle2, Info, AlertTriangle, XCircle } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

interface LogEntry {
  timestamp: string;
  level: "info" | "success" | "warning" | "error";
  message: string;
}

interface LiveLogsSectionProps {
  logs: LogEntry[];
}

const getLogIcon = (level: string) => {
  switch (level) {
    case "success":
      return <CheckCircle2 className="h-4 w-4 text-brand-deck-green" />;
    case "warning":
      return <AlertTriangle className="h-4 w-4 text-brand-buoy-yellow" />;
    case "error":
      return <XCircle className="h-4 w-4 text-destructive" />;
    default:
      return <Info className="h-4 w-4 text-brand-container-rust" />;
  }
};

const getLogColor = (level: string) => {
  switch (level) {
    case "success":
      return "text-brand-deck-green";
    case "warning":
      return "text-brand-buoy-yellow";
    case "error":
      return "text-destructive";
    default:
      return "text-brand-hull-white";
  }
};

const LiveLogsSection = ({ logs }: LiveLogsSectionProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);

  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  return (
    <Card className="p-6 bg-brand-ocean-blue/70 backdrop-blur-sm border-brand-container-rust/40 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <ScrollText className="h-5 w-5 text-brand-container-rust" />
          <h2 className="text-lg font-semibold text-brand-hull-white">Pipeline Logs</h2>
        </div>
        <div className="flex items-center gap-2">
          <Switch
            id="auto-scroll"
            checked={autoScroll}
            onCheckedChange={setAutoScroll}
          />
          <Label htmlFor="auto-scroll" className="text-sm cursor-pointer text-brand-hull-white">
            Auto-scroll
          </Label>
        </div>
      </div>

      <div
        ref={scrollRef}
        className="bg-brand-anchor-black/60 rounded-lg p-4 max-h-[400px] overflow-y-auto border border-brand-ocean-blue/50 font-mono text-xs space-y-2"
      >
        {logs.length === 0 ? (
          <div className="text-brand-cargo-khaki text-center py-8">
            Logs will appear here when the pipeline starts...
          </div>
        ) : (
          logs.map((log, index) => (
            <div key={index} className="flex items-start gap-2 py-1">
              <span className="text-brand-cargo-khaki shrink-0">
                [{new Date(log.timestamp).toLocaleTimeString()}]
              </span>
              <span className="shrink-0">{getLogIcon(log.level)}</span>
              <span className={getLogColor(log.level)}>{log.message}</span>
            </div>
          ))
        )}
      </div>
    </Card>
  );
};

export default LiveLogsSection;
