import { BarChart3, DollarSign, Clock, StopCircle, Pause, Play } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

interface Metrics {
  stage: string;
  companies_total: number;
  companies_done: number;
  contacts_scraped: number;
  contacts_scraped_total: number;
  contacts_enriched: number;
  contacts_enriched_total: number;
  messages_generated: number;
  messages_generated_total: number;
  cost_estimated: number;
  cost_actual: number;
  time_elapsed_seconds: number;
  time_remaining_seconds: number;
}

interface MetricsDashboardProps {
  metrics: Metrics | null;
  status?: "idle" | "running" | "paused" | "complete" | "error";
  onCancel?: () => void;
  onPause?: () => void;
  onResume?: () => void;
}

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs}s`;
};

const formatStage = (stage: string) => {
  const stageMap: Record<string, string> = {
    phase1_scraping: "Phase 1 - Scraping Contacts",
    phase2_enrichment: "Phase 2 - Enrichment & Research",
    phase3_messaging: "Phase 3 - Message Generation",
    complete: "Complete",
  };
  return stageMap[stage] || stage;
};

const MetricRow = ({ label, current, total }: { label: string; current: number; total: number }) => {
  const percentage = total > 0 ? Math.round((current / total) * 100) : 0;

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-brand-cargo-khaki">{label}:</span>
        <span className="font-medium text-brand-hull-white">
          {current}/{total} ({percentage}%)
        </span>
      </div>
      <Progress value={percentage} className="h-2 bg-brand-ocean-blue/50" />
    </div>
  );
};

const MetricsDashboard = ({ metrics, status, onCancel, onPause, onResume }: MetricsDashboardProps) => {
  if (!metrics) return null;

  return (
    <Card className="p-6 bg-brand-ocean-blue/70 backdrop-blur-sm border-brand-container-rust/40 shadow-xl">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-brand-buoy-yellow" />
          <h2 className="text-lg font-semibold text-brand-hull-white">Pipeline Progress</h2>
          {status === "paused" && (
            <span className="px-2 py-1 text-xs font-medium bg-brand-buoy-yellow/20 text-brand-buoy-yellow rounded">
              PAUSED
            </span>
          )}
        </div>

        {/* Control buttons */}
        <div className="flex gap-2">
          {/* Pause button - only show when running */}
          {status === "running" && onPause && (
            <Button
              variant="outline"
              size="sm"
              className="gap-2 border-brand-buoy-yellow text-brand-buoy-yellow hover:bg-brand-buoy-yellow/20"
              onClick={onPause}
            >
              <Pause className="h-4 w-4" />
              Pause
            </Button>
          )}

          {/* Resume button - only show when paused */}
          {status === "paused" && onResume && (
            <Button
              variant="outline"
              size="sm"
              className="gap-2 border-brand-deck-green text-brand-deck-green hover:bg-brand-deck-green/20"
              onClick={onResume}
            >
              <Play className="h-4 w-4" />
              Resume
            </Button>
          )}

          {/* Cancel button - show when running or paused */}
          {(status === "running" || status === "paused") && onCancel && (
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="destructive" size="sm" className="gap-2">
                  <StopCircle className="h-4 w-4" />
                  Cancel
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Cancel Pipeline?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This will stop the pipeline immediately. Progress has been saved to a checkpoint.
                    You can restart the pipeline later to resume from the checkpoint.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Keep Running</AlertDialogCancel>
                  <AlertDialogAction
                    onClick={onCancel}
                    className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                  >
                    Yes, Cancel Pipeline
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          )}
        </div>
      </div>

      <div className="space-y-6">
        <div>
          <div className="text-sm font-medium text-brand-cargo-khaki mb-3">
            Stage: <span className="text-brand-container-rust font-semibold">{formatStage(metrics.stage)}</span>
          </div>
          <div className="space-y-4">
            <MetricRow
              label="Companies"
              current={metrics.companies_done}
              total={metrics.companies_total}
            />
            {metrics.contacts_scraped_total > 0 && (
              <MetricRow
                label="Contacts Scraped"
                current={metrics.contacts_scraped}
                total={metrics.contacts_scraped_total}
              />
            )}
            {metrics.contacts_enriched_total > 0 && (
              <MetricRow
                label="Contacts Enriched"
                current={metrics.contacts_enriched}
                total={metrics.contacts_enriched_total}
              />
            )}
            {metrics.messages_generated_total > 0 && (
              <MetricRow
                label="Messages Generated"
                current={metrics.messages_generated}
                total={metrics.messages_generated_total}
              />
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-brand-container-rust/20">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <DollarSign className="h-4 w-4 text-brand-deck-green" />
              <span className="text-sm font-medium text-brand-hull-white">Cost</span>
            </div>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-brand-cargo-khaki">Estimated:</span>
                <span className="font-medium text-brand-hull-white">${metrics.cost_estimated.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-brand-cargo-khaki">Actual:</span>
                <span className="font-medium text-brand-deck-green">
                  ${metrics.cost_actual.toFixed(2)}
                </span>
              </div>
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-2">
              <Clock className="h-4 w-4 text-brand-buoy-yellow" />
              <span className="text-sm font-medium text-brand-hull-white">Time</span>
            </div>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-brand-cargo-khaki">Elapsed:</span>
                <span className="font-medium text-brand-hull-white">{formatTime(metrics.time_elapsed_seconds)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-brand-cargo-khaki">Remaining:</span>
                <span className="font-medium text-brand-buoy-yellow">
                  {formatTime(metrics.time_remaining_seconds)}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default MetricsDashboard;
