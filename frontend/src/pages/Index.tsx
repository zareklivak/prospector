import { useState, useEffect } from "react";
import Header from "@/components/Header";
import CompanyInputSection from "@/components/CompanyInputSection";
import MetricsDashboard from "@/components/MetricsDashboard";
import LiveLogsSection from "@/components/LiveLogsSection";
import DownloadSection from "@/components/DownloadSection";
import TemplateEditor, { SubjectLineConfig } from "@/components/TemplateEditor";
import { useToast } from "@/hooks/use-toast";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface LogEntry {
  timestamp: string;
  level: "info" | "success" | "warning" | "error";
  message: string;
}

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

const API_BASE = "http://localhost:8001";
const WS_BASE = "ws://localhost:8001";

const Index = () => {
  const { toast } = useToast();

  // Form state
  const [domains, setDomains] = useState("");
  const [contactsPerCompany, setContactsPerCompany] = useState(50);
  const [messageMode, setMessageMode] = useState<"email" | "linkedin">("email");
  const [enrichEmails, setEnrichEmails] = useState(true);
  const [waterfallEnrichment, setWaterfallEnrichment] = useState(false); // Fast mode (Apollo only) by default
  const [verifyCurrentEmployment, setVerifyCurrentEmployment] = useState(false);
  const [skipLinkedIn, setSkipLinkedIn] = useState(false);
  const [prospectOnly, setProspectOnly] = useState(false);
  const [includeUnverifiedContacts, setIncludeUnverifiedContacts] = useState(false);
  const [minScore, setMinScore] = useState(1);
  const [minProfileQuality, setMinProfileQuality] = useState(1);
  const [companyType, setCompanyType] = useState<string>("auto");

  // Role level filters (default: Director+ without Manager)
  const [roleLevels, setRoleLevels] = useState({
    c_suite: true,
    vp: true,
    director: true,
    manager: false,
  });
  const [maxInitialScrape, setMaxInitialScrape] = useState(2000);

  // Custom template state (per-run) - lifted from TemplateEditor to persist across tab switches
  const [customTemplate, setCustomTemplate] = useState<any | null>(null);
  const [customTemplateMode, setCustomTemplateMode] = useState<"email" | "linkedin">("email");
  const [editorTemplate, setEditorTemplate] = useState<any | null>(null); // Current template being edited
  const [editorMode, setEditorMode] = useState<"email" | "linkedin">("email"); // Current mode in editor
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>(""); // Currently selected saved template ID
  const [hasUnsavedTemplateChanges, setHasUnsavedTemplateChanges] = useState(false); // Track if template changes need to be applied

  // Subject line configuration (for email mode)
  const [subjectLineConfig, setSubjectLineConfig] = useState<SubjectLineConfig | null>(null);

  // Pipeline state
  const [status, setStatus] = useState<"idle" | "running" | "paused" | "complete" | "error">("idle");
  const [jobId, setJobId] = useState<string | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [logQueue, setLogQueue] = useState<LogEntry[]>([]); // Queue for rate-limited log display
  const [metrics, setMetrics] = useState<Metrics | null>(null);

  // WebSocket connection
  useEffect(() => {
    if (!jobId || (status !== "running" && status !== "paused")) return;

    const ws = new WebSocket(`${WS_BASE}/ws/${jobId}`);

    ws.onopen = () => {
      console.log("WebSocket connected");
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === "log") {
          // Add to queue instead of directly to logs for smooth display
          setLogQueue((prev) => [
            ...prev,
            {
              timestamp: data.timestamp,
              level: data.level,
              message: data.message,
            },
          ]);
        }

        if (data.type === "metrics") {
          setMetrics(data.data);
        }

        if (data.type === "complete") {
          setStatus("complete");
          toast({
            title: "Pipeline Complete!",
            description: "Your contacts are ready for download.",
          });
        }

        if (data.type === "error") {
          setStatus("error");
          toast({
            title: "Pipeline Error",
            description: data.message || "An error occurred during processing.",
            variant: "destructive",
          });
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      setStatus("error");
      toast({
        title: "Connection Error",
        description: "Lost connection to the backend.",
        variant: "destructive",
      });
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected");
    };

    return () => {
      ws.close();
    };
  }, [jobId, status, toast]);

  // Rate-limited log display - drain queue gradually for smooth flow
  useEffect(() => {
    if (logQueue.length === 0) return;

    const timer = setInterval(() => {
      setLogQueue((queue) => {
        if (queue.length === 0) return queue;

        // Take the first log from the queue
        const [nextLog, ...rest] = queue;

        // Add it to the display logs
        setLogs((prevLogs) => [...prevLogs, nextLog]);

        // Return the rest of the queue
        return rest;
      });
    }, 150); // Display one log every 150ms for smooth, consistent flow

    return () => clearInterval(timer);
  }, [logQueue.length]); // Re-run when queue length changes

  const handleTemplateChange = (template: any | null, mode: "email" | "linkedin") => {
    // DEBUG: Log what we're receiving from template editor
    console.log("🔧 DEBUG handleTemplateChange called:");
    console.log("  Template:", template);
    console.log("  Mode:", mode);
    console.log("  Template name:", template?.name);
    console.log("  Has message_1:", !!template?.message_1);
    console.log("  Has message_2:", !!template?.message_2);

    setCustomTemplate(template);
    setCustomTemplateMode(mode);
    setHasUnsavedTemplateChanges(false); // Reset flag when template is applied

    // DEBUG: Verify state was set (will log on next render)
    console.log("  State update triggered");
  };

  const handleEditorTemplateChange = (template: any | null, mode: "email" | "linkedin", templateId?: string, hasUnsavedChanges?: boolean) => {
    // Update the editor's current template state (persists across tab switches)
    setEditorTemplate(template);
    setEditorMode(mode);
    if (templateId !== undefined) {
      setSelectedTemplateId(templateId);
    }
    if (hasUnsavedChanges !== undefined) {
      setHasUnsavedTemplateChanges(hasUnsavedChanges);
    }
  };

  const handleSubjectLineChange = (config: SubjectLineConfig | null) => {
    console.log("🔧 DEBUG handleSubjectLineChange:", config);
    setSubjectLineConfig(config);
  };

  const handleRunPipeline = async () => {
    const domainList = domains
      .split("\n")
      .map((d) => d.trim())
      .filter((d) => d);

    if (domainList.length === 0) {
      toast({
        title: "Invalid Input",
        description: "Please enter at least one company domain.",
        variant: "destructive",
      });
      return;
    }

    try {
      setStatus("running");
      setLogs([]);
      setLogQueue([]); // Clear the queue for new run
      setMetrics(null);

      // DEBUG: Log what we're sending to pipeline
      console.log("🔧 DEBUG handleRunPipeline:");
      console.log("  Current customTemplate state:", customTemplate);
      console.log("  customTemplate is null:", customTemplate === null);
      console.log("  customTemplate is undefined:", customTemplate === undefined);
      console.log("  messageMode:", messageMode);
      console.log("  customTemplateMode:", customTemplateMode);
      if (customTemplate) {
        console.log("  Template name:", customTemplate.name);
        console.log("  Template mode:", customTemplate.mode);
      }

      const response = await fetch(`${API_BASE}/api/run-pipeline`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          company_domains: domainList,
          contacts_per_company: contactsPerCompany,
          message_mode: messageMode,
          enrich_emails: enrichEmails,
          waterfall_enrichment: waterfallEnrichment,
          verify_current_employment: verifyCurrentEmployment,
          skip_linkedin: skipLinkedIn,
          prospect_only: prospectOnly,
          min_score: minScore,
          min_profile_quality: minProfileQuality,
          custom_template: customTemplate,
          subject_line_config: messageMode === "email" ? subjectLineConfig : null,
          company_type_override: companyType === "auto" ? null : companyType,
          role_levels: roleLevels,
          max_initial_scrape: maxInitialScrape,
          include_unverified_contacts: includeUnverifiedContacts,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to start pipeline");
      }

      const data = await response.json();
      setJobId(data.job_id);

      toast({
        title: "Pipeline Started",
        description: `Job ID: ${data.job_id}`,
      });
    } catch (error) {
      console.error("Error starting pipeline:", error);
      setStatus("error");
      toast({
        title: "Connection Error",
        description: "Could not connect to backend. Make sure it's running on localhost:8000.",
        variant: "destructive",
      });
    }
  };

  const handleDownload = async () => {
    if (!jobId) return;

    try {
      const response = await fetch(`${API_BASE}/api/download-csv/${jobId}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `prospector_output_${jobId}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      toast({
        title: "Download Started",
        description: "Your CSV file is being downloaded.",
      });
    } catch (error) {
      console.error("Download error:", error);
      toast({
        title: "Download Failed",
        description: "Could not download the CSV file.",
        variant: "destructive",
      });
    }
  };

  const handleCancelPipeline = async () => {
    if (!jobId) return;

    try {
      const response = await fetch(`${API_BASE}/api/cancel-pipeline/${jobId}`, {
        method: "POST",
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to cancel pipeline");
      }

      toast({
        title: "Pipeline Cancelled",
        description: "The pipeline is being stopped.",
        variant: "default",
      });

      // Update status to reflect cancellation
      setStatus("error"); // We'll treat cancelled as error state for UI purposes
    } catch (error: any) {
      console.error("Cancel error:", error);
      toast({
        title: "Cancellation Failed",
        description: error.message || "Could not cancel the pipeline.",
        variant: "destructive",
      });
    }
  };

  const handlePausePipeline = async () => {
    if (!jobId) return;

    try {
      const response = await fetch(`${API_BASE}/api/pause-pipeline/${jobId}`, {
        method: "POST",
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to pause pipeline");
      }

      setStatus("paused");
      toast({
        title: "Pipeline Paused",
        description: "Progress has been saved. You can resume anytime.",
      });
    } catch (error: any) {
      console.error("Pause error:", error);
      toast({
        title: "Pause Failed",
        description: error.message || "Could not pause the pipeline.",
        variant: "destructive",
      });
    }
  };

  const handleResumePipeline = async () => {
    if (!jobId) return;

    try {
      const response = await fetch(`${API_BASE}/api/resume-pipeline/${jobId}`, {
        method: "POST",
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to resume pipeline");
      }

      setStatus("running");
      toast({
        title: "Pipeline Resumed",
        description: "Continuing from checkpoint...",
      });
    } catch (error: any) {
      console.error("Resume error:", error);
      toast({
        title: "Resume Failed",
        description: error.message || "Could not resume the pipeline.",
        variant: "destructive",
      });
    }
  };

  const handleReset = () => {
    setStatus("idle");
    setJobId(null);
    setLogs([]);
    setLogQueue([]); // Clear the queue as well
    setMetrics(null);
    setDomains("");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-anchor-black via-brand-ocean-blue/30 to-brand-anchor-black relative overflow-hidden">
      {/* Soft background glow */}
      <div
        className="absolute inset-0 opacity-30 pointer-events-none"
        style={{
          backgroundImage:
            "radial-gradient(ellipse at 20% 10%, rgba(213,149,102,0.25), transparent 50%), radial-gradient(ellipse at 85% 80%, rgba(169,197,157,0.18), transparent 55%)",
        }}
      />

      <Header />

      <main className="container mx-auto px-6 py-8 max-w-5xl relative z-10">
        <div className="space-y-6">
          {/* Tabs for Configuration and Templates */}
          <Tabs defaultValue="configuration" className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-6 bg-brand-ocean-blue/70 backdrop-blur-sm border border-brand-container-rust/40">
              <TabsTrigger
                value="configuration"
                className="data-[state=active]:bg-brand-container-rust data-[state=active]:text-brand-anchor-black text-brand-hull-white"
              >
                Pipeline Configuration
              </TabsTrigger>
              <TabsTrigger
                value="templates"
                className="data-[state=active]:bg-brand-container-rust data-[state=active]:text-brand-anchor-black text-brand-hull-white"
              >
                Message Templates
              </TabsTrigger>
            </TabsList>

            <TabsContent value="configuration" className="space-y-6">
              {/* Company Input */}
              <CompanyInputSection
                domains={domains}
                setDomains={setDomains}
                contactsPerCompany={contactsPerCompany}
                setContactsPerCompany={setContactsPerCompany}
                messageMode={messageMode}
                setMessageMode={setMessageMode}
                enrichEmails={enrichEmails}
                setEnrichEmails={setEnrichEmails}
                waterfallEnrichment={waterfallEnrichment}
                setWaterfallEnrichment={setWaterfallEnrichment}
                verifyCurrentEmployment={verifyCurrentEmployment}
                setVerifyCurrentEmployment={setVerifyCurrentEmployment}
                skipLinkedIn={skipLinkedIn}
                setSkipLinkedIn={setSkipLinkedIn}
                prospectOnly={prospectOnly}
                setProspectOnly={setProspectOnly}
                includeUnverifiedContacts={includeUnverifiedContacts}
                setIncludeUnverifiedContacts={setIncludeUnverifiedContacts}
                minScore={minScore}
                setMinScore={setMinScore}
                minProfileQuality={minProfileQuality}
                setMinProfileQuality={setMinProfileQuality}
                companyType={companyType}
                setCompanyType={setCompanyType}
                roleLevels={roleLevels}
                setRoleLevels={setRoleLevels}
                maxInitialScrape={maxInitialScrape}
                setMaxInitialScrape={setMaxInitialScrape}
                onRunPipeline={handleRunPipeline}
                isRunning={status === "running"}
              />
            </TabsContent>

            <TabsContent value="templates" className="space-y-6">
              <TemplateEditor
                onTemplateChange={handleTemplateChange}
                onEditorStateChange={handleEditorTemplateChange}
                onSubjectLineChange={handleSubjectLineChange}
                initialTemplate={editorTemplate}
                initialMode={editorMode}
                initialSelectedTemplateId={selectedTemplateId}
                initialHasUnsavedChanges={hasUnsavedTemplateChanges}
                initialSubjectLineConfig={subjectLineConfig}
              />
            </TabsContent>
          </Tabs>

          {/* Metrics Dashboard */}
          {(status === "running" || status === "paused" || status === "complete") && (
            <MetricsDashboard
              metrics={metrics}
              status={status}
              onCancel={handleCancelPipeline}
              onPause={handlePausePipeline}
              onResume={handleResumePipeline}
            />
          )}

          {/* Live Logs */}
          {(status === "running" || status === "paused") && <LiveLogsSection logs={logs} />}

          {/* Download Section */}
          {status === "complete" && metrics && (
            <DownloadSection
              jobId={jobId}
              totalContacts={metrics.contacts_enriched}
              totalCost={metrics.cost_actual}
              totalTime={metrics.time_elapsed_seconds}
              onDownload={handleDownload}
              onReset={handleReset}
            />
          )}
        </div>
      </main>
    </div>
  );
};

export default Index;
