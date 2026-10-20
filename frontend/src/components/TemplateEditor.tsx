import { useState, useEffect } from "react";
import { FileEdit, Play, Loader2, Info, Save, FolderOpen, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { Alert, AlertDescription } from "@/components/ui/alert";
import VariableReference from "./VariableReference";

const API_BASE = "http://localhost:8001";

interface UnifiedTemplate {
  name: string;
  version: string;
  mode: string;
  system_prompt: string;
  message_1: MessageTemplate;
  message_2: MessageTemplate;
  message_3: MessageTemplate;
  message_4: MessageTemplate;
  use_cases: Record<string, string[]>;
  value_props: string[];
}

interface MessageTemplate {
  template: string;
  personalization_instruction?: string;
  cta_options?: string[];
  signature_options?: string[];
  acknowledgment_options?: string[];
  graceful_exit_instruction?: string;
}

interface TestResult {
  prospect: {
    first_name: string;
    last_name: string;
    title: string;
    company_name: string;
  };
  messages: {
    message_1: string;
    message_2: string;
    message_3: string;
    message_4: string;
  };
}

interface SubjectLineConfig {
  style: "question" | "direct" | "curiosity" | "value" | "custom";
  customPrompt?: string;
}

interface TemplateEditorProps {
  onTemplateChange?: (template: UnifiedTemplate | null, mode: "email" | "linkedin") => void;
  onEditorStateChange?: (template: UnifiedTemplate | null, mode: "email" | "linkedin", templateId?: string, hasUnsavedChanges?: boolean) => void;
  onSubjectLineChange?: (config: SubjectLineConfig | null) => void;
  initialTemplate?: UnifiedTemplate | null;
  initialMode?: "email" | "linkedin";
  initialSelectedTemplateId?: string;
  initialHasUnsavedChanges?: boolean;
  initialSubjectLineConfig?: SubjectLineConfig | null;
}

const TemplateEditor = ({
  onTemplateChange,
  onEditorStateChange,
  onSubjectLineChange,
  initialTemplate,
  initialMode = "email",
  initialSelectedTemplateId = "",
  initialHasUnsavedChanges = false,
  initialSubjectLineConfig = null
}: TemplateEditorProps) => {
  const { toast } = useToast();
  const [mode, setMode] = useState<"email" | "linkedin">(initialMode);
  const [template, setTemplate] = useState<UnifiedTemplate | null>(initialTemplate);
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [testLogs, setTestLogs] = useState<string[]>([]);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(initialHasUnsavedChanges);
  const [testIndustry, setTestIndustry] = useState<string>("auto-detect");

  // Subject line state
  const [subjectLineStyle, setSubjectLineStyle] = useState<SubjectLineConfig["style"]>(
    initialSubjectLineConfig?.style || "question"
  );
  const [subjectLineCustomPrompt, setSubjectLineCustomPrompt] = useState<string>(
    initialSubjectLineConfig?.customPrompt || ""
  );

  // Template management state
  const [savedTemplates, setSavedTemplates] = useState<Array<{id: string, name: string, mode: string, created_at: string}>>([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>(initialSelectedTemplateId);
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [newTemplateName, setNewTemplateName] = useState("");

  // Sync parent state whenever local template/mode/selectedTemplateId/hasUnsavedChanges changes
  useEffect(() => {
    if (template && onEditorStateChange) {
      onEditorStateChange(template, mode, selectedTemplateId, hasUnsavedChanges);
    }
  }, [template, mode, selectedTemplateId, hasUnsavedChanges]);

  // Fetch default template on mount (only if no initial template provided)
  useEffect(() => {
    if (!initialTemplate) {
      // Load default email template on first mount
      loadDefaultTemplate("email");
      setSelectedTemplateId("default_email");
    }
  }, []);

  // Fetch saved templates list on mount
  useEffect(() => {
    fetchSavedTemplates();
  }, []);

  const fetchSavedTemplates = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/saved-templates`);
      if (response.ok) {
        const data = await response.json();
        setSavedTemplates(data.templates || []);
      }
    } catch (error) {
      console.error("Failed to fetch saved templates:", error);
    }
  };

  const loadSavedTemplate = async (templateId: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/saved-templates/${templateId}`);
      if (!response.ok) throw new Error("Failed to load template");
      const data = await response.json();
      setTemplate(data);
      setMode(data.mode || "email");
      setSelectedTemplateId(templateId);
      setHasUnsavedChanges(true); // Mark as unsaved - user must click "Apply Changes"
      toast({
        title: "Template Loaded",
        description: `Loaded "${data.name}" - Click "Apply Changes" to use in pipeline`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load template",
        variant: "destructive",
      });
    }
  };

  const saveTemplate = async () => {
    if (!newTemplateName.trim()) {
      toast({
        title: "Error",
        description: "Please enter a template name",
        variant: "destructive",
      });
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/saved-templates`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: newTemplateName.trim(),
          template: template,
        }),
      });

      if (!response.ok) throw new Error("Failed to save template");

      const data = await response.json();

      toast({
        title: "Template Saved",
        description: `Saved as "${data.name}"`,
      });

      setSaveDialogOpen(false);
      setNewTemplateName("");
      fetchSavedTemplates(); // Refresh list
      setSelectedTemplateId(data.id);
      setHasUnsavedChanges(false);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save template",
        variant: "destructive",
      });
    }
  };

  const updateCurrentTemplate = async () => {
    // Only allow updating saved templates (not default ones)
    if (!selectedTemplateId || selectedTemplateId.startsWith("default_")) {
      toast({
        title: "Error",
        description: "Cannot update default templates. Use 'Save As New' instead.",
        variant: "destructive",
      });
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/saved-templates/${selectedTemplateId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          template: template,
        }),
      });

      if (!response.ok) throw new Error("Failed to update template");

      const data = await response.json();

      toast({
        title: "Template Saved",
        description: `Updated "${data.name}"`,
      });

      setHasUnsavedChanges(false);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update template",
        variant: "destructive",
      });
    }
  };

  const deleteSavedTemplate = async (templateId: string) => {
    if (!confirm("Are you sure you want to delete this template?")) return;

    try {
      const response = await fetch(`${API_BASE}/api/saved-templates/${templateId}`, {
        method: "DELETE",
      });

      if (!response.ok) throw new Error("Failed to delete template");

      toast({
        title: "Template Deleted",
        description: "Template removed successfully",
      });

      fetchSavedTemplates(); // Refresh list
      if (selectedTemplateId === templateId) {
        setSelectedTemplateId("");
        fetchTemplate(); // Load default template
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete template",
        variant: "destructive",
      });
    }
  };

  const fetchTemplate = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/unified-templates/${mode}`);
      if (!response.ok) throw new Error("Failed to fetch template");
      const data = await response.json();
      setTemplate(data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load template",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadDefaultTemplate = async (templateMode: "email" | "linkedin") => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/unified-templates/${templateMode}`);
      if (!response.ok) throw new Error("Failed to fetch template");
      const data = await response.json();
      setTemplate(data);
      setMode(templateMode); // Update mode to match template
      setHasUnsavedChanges(true); // Mark as unsaved - user must click "Apply Changes"
      toast({
        title: "Template Loaded",
        description: `Loaded "Default ${templateMode.charAt(0).toUpperCase() + templateMode.slice(1)} Template" - Click "Apply Changes" to use in pipeline`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load template",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const testTemplate = async () => {
    setTesting(true);
    setTestResults([]);
    setTestLogs([]);

    const addLog = (message: string) => {
      setTestLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] ${message}`]);
    };

    try {
      addLog("🚀 Starting template test...");

      // Determine how many contacts will be tested based on industry filter
      const contactCount = testIndustry && testIndustry !== "auto-detect" ? 2 : 2;
      const industryText = testIndustry && testIndustry !== "auto-detect"
        ? `${testIndustry} industry`
        : "diverse industries (broker + carrier)";

      addLog(`📋 Testing with ${contactCount} contacts from ${industryText}...`);
      addLog("");
      addLog(`🤖 Generating messages using ${mode} templates...`);
      addLog("");

      const startTime = Date.now();

      // DEBUG: Log what we're sending to test endpoint
      console.log("🔧 DEBUG testTemplate:");
      console.log("  Mode:", mode);
      console.log("  Sending custom template:", !!template);
      console.log("  Industry override:", testIndustry === "auto-detect" ? "auto-detect" : testIndustry);
      if (template) {
        console.log("  Template name:", template.name);
        console.log("  Message 1 template:", template.message_1?.template?.substring(0, 100));
        console.log("  Message 3 CTA options:", template.message_3?.cta_options);
        console.log("  Message 3 signature options:", template.message_3?.signature_options);
      }

      const response = await fetch(`${API_BASE}/api/test-templates`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message_mode: mode,
          custom_template: template,  // Send the full template
          company_type_override: testIndustry === "auto-detect" ? null : testIndustry,  // Send null for auto-detect
        }),
      });

      if (!response.ok) throw new Error("Failed to test template");

      const data = await response.json();
      const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(1);

      addLog(`✅ Generated ${data.prospects.length} sequences in ${data.generation_time}s`);
      addLog(`⚡ Average: ${(data.generation_time / data.prospects.length).toFixed(1)}s per contact`);
      addLog("");

      // Show which contacts were tested
      addLog("📝 Tested contacts:");
      data.prospects.forEach((result: any, idx: number) => {
        const p = result.prospect;
        addLog(`   ${idx + 1}. ${p.first_name} ${p.last_name} - ${p.title} at ${p.company_name}`);
      });
      addLog("");

      addLog("✨ Test complete! Scroll down to view results.");

      setTestResults(data.prospects);

      toast({
        title: "Test Complete",
        description: `Generated ${data.prospects.length} test sequences in ${data.generation_time}s`,
      });
    } catch (error) {
      addLog(`❌ Error: ${error instanceof Error ? error.message : "Test failed"}`);
      toast({
        title: "Error",
        description: "Failed to test template",
        variant: "destructive",
      });
    } finally {
      setTesting(false);
    }
  };

  const updateSystemPrompt = (value: string) => {
    if (!template) return;
    setTemplate({ ...template, system_prompt: value });
    setHasUnsavedChanges(true);
  };

  const updateMessageTemplate = (
    messageNum: 1 | 2 | 3 | 4,
    field: keyof MessageTemplate,
    value: string | string[]
  ) => {
    if (!template) return;
    const messageKey = `message_${messageNum}` as keyof UnifiedTemplate;
    const message = template[messageKey] as MessageTemplate;

    setTemplate({
      ...template,
      [messageKey]: {
        ...message,
        [field]: value,
      },
    });
    setHasUnsavedChanges(true);
  };

  const applyChanges = () => {
    if (onTemplateChange && template) {
      // Clean up empty lines from arrays before saving
      const cleanTemplate = { ...template };

      for (let i = 1; i <= 4; i++) {
        const messageKey = `message_${i}` as keyof UnifiedTemplate;
        const message = cleanTemplate[messageKey] as MessageTemplate;

        if (message) {
          // Clean CTAs, signatures, and acknowledgments by removing empty strings
          if (message.cta_options) {
            message.cta_options = message.cta_options.filter(line => line.trim());
          }
          if (message.signature_options) {
            message.signature_options = message.signature_options.filter(line => line.trim());
          }
          if (message.acknowledgment_options) {
            message.acknowledgment_options = message.acknowledgment_options.filter(line => line.trim());
          }
        }
      }

      // DEBUG: Log what we're sending
      console.log("🔧 DEBUG TemplateEditor applyChanges:");
      console.log("  Template name:", cleanTemplate.name);
      console.log("  Has system_prompt:", !!cleanTemplate.system_prompt);
      console.log("  Has message_1:", !!cleanTemplate.message_1);
      console.log("  Has message_2:", !!cleanTemplate.message_2);
      console.log("  Has message_3:", !!cleanTemplate.message_3);
      console.log("  Has message_4:", !!cleanTemplate.message_4);
      console.log("  Message 2 template:", cleanTemplate.message_2?.template?.substring(0, 100));
      console.log("  Full template keys:", Object.keys(cleanTemplate));

      onTemplateChange(cleanTemplate, mode);

      // Also pass subject line config if in email mode
      if (onSubjectLineChange && mode === "email") {
        const subjectConfig: SubjectLineConfig = {
          style: subjectLineStyle,
          customPrompt: subjectLineStyle === "custom" ? subjectLineCustomPrompt : undefined
        };
        onSubjectLineChange(subjectConfig);
        console.log("  Subject line config:", subjectConfig);
      }

      setHasUnsavedChanges(false);
      toast({
        title: "Changes Applied",
        description: "Your template changes will be used for the next pipeline run.",
      });
    }
  };

  const updateArrayField = (
    messageNum: 1 | 2 | 3 | 4,
    field: "cta_options" | "signature_options" | "acknowledgment_options",
    value: string
  ) => {
    if (!template) return;

    let lines: string[];
    if (field === "signature_options") {
      // Signatures: split by blank lines (double newline)
      // This preserves multi-line signatures like "Best,\nZarek Livak"
      lines = value.split("\n\n");
    } else {
      // CTAs and acknowledgments: split by single newline
      // Preserve empty lines while editing - they'll be cleaned up on save
      lines = value.split("\n");
    }

    updateMessageTemplate(messageNum, field, lines);
  };

  if (loading) {
    return (
      <Card className="p-12 bg-brand-ocean-blue/70 backdrop-blur-sm border-brand-container-rust/40 shadow-xl">
        <div className="flex flex-col items-center justify-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-brand-container-rust" />
          <p className="text-brand-hull-white">Loading template...</p>
        </div>
      </Card>
    );
  }

  if (!template) {
    return (
      <Card className="p-12 bg-brand-ocean-blue/70 backdrop-blur-sm border-brand-container-rust/40 shadow-xl">
        <div className="text-center">
          <p className="text-brand-hull-white">Failed to load template</p>
          <Button onClick={fetchTemplate} className="mt-4 bg-brand-container-rust hover:bg-brand-container-rust/80 text-brand-anchor-black">
            Retry
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Per-Run Notice */}
      <Alert>
        <Info className="h-4 w-4" />
        <AlertDescription>
          <strong>Per-Run Customization:</strong> Any edits you make here will only apply to your next pipeline run.
          Templates will reset to defaults when you refresh the page or start a new session.
        </AlertDescription>
      </Alert>

      {/* Removed: Mode Toggle - now controlled by Pipeline Configuration tab only */}

      {/* Template Library Management */}
      <Card className="p-6 bg-brand-ocean-blue/70 backdrop-blur-sm border-brand-container-rust/40 shadow-xl">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FolderOpen className="h-5 w-5 text-brand-container-rust" />
              <h3 className="font-semibold text-brand-hull-white">Template Library</h3>
            </div>
          </div>

          <div className="flex gap-3">
            {/* Template Library Dropdown */}
            <div className="flex-1">
              <Select
                value={selectedTemplateId}
                onValueChange={(value) => {
                  if (value === "default_email") {
                    loadDefaultTemplate("email");
                    setSelectedTemplateId("default_email");
                  } else if (value === "default_linkedin") {
                    loadDefaultTemplate("linkedin");
                    setSelectedTemplateId("default_linkedin");
                  } else {
                    loadSavedTemplate(value);
                  }
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a template..." />
                </SelectTrigger>
                <SelectContent>
                  {/* Default Templates */}
                  <SelectItem value="default_email">Default Email Template</SelectItem>
                  <SelectItem value="default_linkedin">Default LinkedIn Template</SelectItem>

                  {/* Saved Custom Templates */}
                  {savedTemplates.length > 0 && (
                    <>
                      {savedTemplates.map((tmpl) => (
                        <SelectItem key={tmpl.id} value={tmpl.id}>
                          {tmpl.name}
                        </SelectItem>
                      ))}
                    </>
                  )}
                </SelectContent>
              </Select>
            </div>

            {/* Save Button (update existing) - only show for saved templates */}
            {selectedTemplateId && !selectedTemplateId.startsWith("default_") && (
              <Button
                variant="outline"
                className="gap-2"
                onClick={updateCurrentTemplate}
              >
                <Save className="h-4 w-4" />
                Save
              </Button>
            )}

            {/* Save As New Button */}
            <Dialog open={saveDialogOpen} onOpenChange={setSaveDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="outline" className="gap-2">
                  <Save className="h-4 w-4" />
                  Save As New
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Save As New Template</DialogTitle>
                  <DialogDescription>
                    Create a new template with your current settings.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="template-name">Template Name</Label>
                    <Input
                      id="template-name"
                      placeholder="e.g., Aggressive Sales, Soft Touch, Technical Deep Dive"
                      value={newTemplateName}
                      onChange={(e) => setNewTemplateName(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          saveTemplate();
                        }
                      }}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setSaveDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={saveTemplate}>Save Template</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            {/* Delete Template Button */}
            {selectedTemplateId && (
              <Button
                variant="outline"
                size="icon"
                onClick={() => deleteSavedTemplate(selectedTemplateId)}
                className="text-destructive hover:text-destructive"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </div>

          {selectedTemplateId && (
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                Currently editing: <strong>{savedTemplates.find(t => t.id === selectedTemplateId)?.name}</strong>
                {hasUnsavedChanges && <span className="ml-2 text-orange-600">• Click "Apply Changes" to use in pipeline</span>}
              </AlertDescription>
            </Alert>
          )}
        </div>
      </Card>

      {/* Subject Line Configuration (Email mode only) */}
      {mode === "email" && (
        <Card className="p-6 bg-brand-ocean-blue/70 backdrop-blur-sm border-brand-container-rust/40 shadow-xl">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <FileEdit className="h-5 w-5 text-brand-container-rust" />
              <h3 className="font-semibold text-brand-hull-white">Subject Line Generation</h3>
            </div>
            <p className="text-sm text-brand-cargo-khaki">
              Configure how subject lines are generated for each contact. Subject lines will be personalized using the contact's name, title, company, and research data.
            </p>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="subject-style" className="text-brand-hull-white">Subject Line Style</Label>
                <Select
                  value={subjectLineStyle}
                  onValueChange={(value: SubjectLineConfig["style"]) => {
                    setSubjectLineStyle(value);
                    setHasUnsavedChanges(true);
                  }}
                >
                  <SelectTrigger id="subject-style">
                    <SelectValue placeholder="Select a style..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="question">Question-based (e.g., "Quick question about ops at [company]")</SelectItem>
                    <SelectItem value="direct">Direct (e.g., "[first_name] - automation for [company]")</SelectItem>
                    <SelectItem value="curiosity">Curiosity (e.g., "Thought about [company]'s approach")</SelectItem>
                    <SelectItem value="value">Value-focused (e.g., "Reducing costs at [company]")</SelectItem>
                    <SelectItem value="custom">Custom Prompt</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {subjectLineStyle === "custom" && (
                <div className="space-y-2" onKeyDown={(e) => e.stopPropagation()}>
                  <Label htmlFor="subject-custom-prompt" className="text-brand-hull-white">Custom Prompt</Label>
                  <Textarea
                    id="subject-custom-prompt"
                    value={subjectLineCustomPrompt}
                    onChange={(e) => {
                      setSubjectLineCustomPrompt(e.target.value);
                      setHasUnsavedChanges(true);
                    }}
                    className="min-h-[100px]"
                    placeholder="Enter your custom prompt for generating subject lines. Available variables: first_name, company_name, title, personal_research, company_research"
                  />
                  <p className="text-xs text-muted-foreground">
                    Example: "Write a short, personalized subject line that references something specific from their LinkedIn profile or company research. Keep it under 50 characters."
                  </p>
                </div>
              )}

              <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                  Subject lines will be generated for each contact and added as a new column in the output CSV.
                </AlertDescription>
              </Alert>
            </div>
          </div>
        </Card>
      )}

      {/* System Prompt Editor */}
      <Card className="p-6 bg-brand-ocean-blue/70 backdrop-blur-sm border-brand-container-rust/40 shadow-xl">
        <div className="space-y-4" onKeyDown={(e) => e.stopPropagation()}>
          <Label htmlFor="system-prompt" className="text-base font-semibold text-brand-hull-white">
            System Prompt (AI Instructions)
          </Label>
          <Textarea
            id="system-prompt"
            value={template.system_prompt}
            onChange={(e) => updateSystemPrompt(e.target.value)}
            className="min-h-[300px] font-mono text-sm"
            placeholder="Enter the system prompt for the AI..."
          />
          <p className="text-xs text-muted-foreground">
            This defines how the AI should write messages, the tone, style, and rules to follow.
          </p>
        </div>
      </Card>

      {/* Message Templates */}
      <Card className="p-6 bg-brand-ocean-blue/70 backdrop-blur-sm border-brand-container-rust/40 shadow-xl">
        <h3 className="text-base font-semibold mb-4 text-brand-hull-white">Message Templates</h3>

        <Accordion type="single" collapsible className="w-full">
          {/* Message 1 */}
          <AccordionItem value="message-1">
            <AccordionTrigger className="text-base font-medium text-brand-hull-white">
              Message 1 (Initial Outreach)
            </AccordionTrigger>
            <AccordionContent className="space-y-4 pt-4">
              <div onKeyDown={(e) => e.stopPropagation()}>
                <Label htmlFor="msg1-template" className="text-brand-hull-white">Template</Label>
                <Textarea
                  id="msg1-template"
                  value={template.message_1.template}
                  onChange={(e) => updateMessageTemplate(1, "template", e.target.value)}
                  className="mt-2 min-h-[200px] font-mono text-sm"
                  placeholder="Message template with {placeholders}..."
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Use placeholders: {"{first_name}"}, {"{personalization}"}, {"{use_cases_short}"}, {"{use_cases_long}"}, {"{value_prop_short}"}, {"{value_prop_long}"}, {"{cta}"}, {"{signature}"}
                </p>
              </div>

              <div onKeyDown={(e) => e.stopPropagation()}>
                <Label htmlFor="msg1-personalization">Personalization Instruction (Optional)</Label>
                <Textarea
                  id="msg1-personalization"
                  value={template.message_1.personalization_instruction || ""}
                  onChange={(e) => updateMessageTemplate(1, "personalization_instruction", e.target.value)}
                  className="mt-2 min-h-[100px]"
                  placeholder="Leave empty to use default..."
                />
              </div>

              <div onKeyDown={(e) => e.stopPropagation()}>
                <Label htmlFor="msg1-personalization2">Personalization Instruction 2 (Optional)</Label>
                <Textarea
                  id="msg1-personalization2"
                  value={template.message_1.personalization_instruction_2 || ""}
                  onChange={(e) => updateMessageTemplate(1, "personalization_instruction_2", e.target.value)}
                  className="mt-2 min-h-[100px]"
                  placeholder="Leave empty to skip second personalization..."
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Use {"{personalization2}"} in your template to place this content separately from the first personalization.
                </p>
              </div>

              <div onKeyDown={(e) => e.stopPropagation()}>
                <Label htmlFor="msg1-ctas">CTA Options (one per line)</Label>
                <Textarea
                  id="msg1-ctas"
                  value={template.message_1.cta_options?.join("\n") || ""}
                  onChange={(e) => updateArrayField(1, "cta_options", e.target.value)}
                  className="mt-2 min-h-[100px]"
                  placeholder="Each CTA on a new line..."
                />
              </div>

              <div onKeyDown={(e) => e.stopPropagation()}>
                <Label htmlFor="msg1-signatures">Signature Options</Label>
                <Textarea
                  id="msg1-signatures"
                  value={template.message_1.signature_options?.join("\n\n") || ""}
                  onChange={(e) => updateArrayField(1, "signature_options", e.target.value)}
                  className="mt-2 min-h-[80px]"
                  placeholder="Best,&#10;Zarek Livak&#10;&#10;Best regards,&#10;Zarek Livak&#10;&#10;Cheers,&#10;Zarek"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Separate each signature with a blank line. Signatures can be multi-line (e.g., "Best,\nZarek Livak").
                </p>
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Message 2 */}
          <AccordionItem value="message-2">
            <AccordionTrigger className="text-base font-medium text-brand-hull-white">
              Message 2 (First Follow-up)
            </AccordionTrigger>
            <AccordionContent className="space-y-4 pt-4">
              <div onKeyDown={(e) => e.stopPropagation()}>
                <Label htmlFor="msg2-template">Template</Label>
                <Textarea
                  id="msg2-template"
                  value={template.message_2.template}
                  onChange={(e) => updateMessageTemplate(2, "template", e.target.value)}
                  className="mt-2 min-h-[150px] font-mono text-sm"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Use placeholders: {"{first_name}"}, {"{personalization}"}, {"{cta}"}, {"{signature}"}
                </p>
              </div>

              <div onKeyDown={(e) => e.stopPropagation()}>
                <Label htmlFor="msg2-personalization">Personalization Instruction (Optional)</Label>
                <Textarea
                  id="msg2-personalization"
                  value={template.message_2.personalization_instruction || ""}
                  onChange={(e) => updateMessageTemplate(2, "personalization_instruction", e.target.value)}
                  className="mt-2 min-h-[100px]"
                />
              </div>

              <div onKeyDown={(e) => e.stopPropagation()}>
                <Label htmlFor="msg2-personalization2">Personalization Instruction 2 (Optional)</Label>
                <Textarea
                  id="msg2-personalization2"
                  value={template.message_2.personalization_instruction_2 || ""}
                  onChange={(e) => updateMessageTemplate(2, "personalization_instruction_2", e.target.value)}
                  className="mt-2 min-h-[100px]"
                  placeholder="Leave empty to skip second personalization..."
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Use {"{personalization2}"} in your template to place this content separately from the first personalization.
                </p>
              </div>

              <div onKeyDown={(e) => e.stopPropagation()}>
                <Label htmlFor="msg2-ctas">CTA Options (one per line)</Label>
                <Textarea
                  id="msg2-ctas"
                  value={template.message_2.cta_options?.join("\n") || ""}
                  onChange={(e) => updateArrayField(2, "cta_options", e.target.value)}
                  className="mt-2 min-h-[80px]"
                />
              </div>

              <div onKeyDown={(e) => e.stopPropagation()}>
                <Label htmlFor="msg2-signatures">Signature Options</Label>
                <Textarea
                  id="msg2-signatures"
                  value={template.message_2.signature_options?.join("\n\n") || ""}
                  onChange={(e) => updateArrayField(2, "signature_options", e.target.value)}
                  className="mt-2 min-h-[80px]"
                  placeholder="Best,&#10;Zarek Livak&#10;&#10;Best regards,&#10;Zarek Livak&#10;&#10;Cheers,&#10;Zarek"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Separate each signature with a blank line. Signatures can be multi-line (e.g., "Best,\nZarek Livak").
                </p>
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Message 3 */}
          <AccordionItem value="message-3">
            <AccordionTrigger className="text-base font-medium text-brand-hull-white">
              Message 3 (Second Follow-up)
            </AccordionTrigger>
            <AccordionContent className="space-y-4 pt-4">
              <div onKeyDown={(e) => e.stopPropagation()}>
                <Label htmlFor="msg3-template">Template</Label>
                <Textarea
                  id="msg3-template"
                  value={template.message_3.template}
                  onChange={(e) => updateMessageTemplate(3, "template", e.target.value)}
                  className="mt-2 min-h-[200px] font-mono text-sm"
                />
              </div>

              <div onKeyDown={(e) => e.stopPropagation()}>
                <Label htmlFor="msg3-personalization">Personalization Instruction (Optional)</Label>
                <Textarea
                  id="msg3-personalization"
                  value={template.message_3.personalization_instruction || ""}
                  onChange={(e) => updateMessageTemplate(3, "personalization_instruction", e.target.value)}
                  className="mt-2 min-h-[100px]"
                />
              </div>

              <div onKeyDown={(e) => e.stopPropagation()}>
                <Label htmlFor="msg3-personalization2">Personalization Instruction 2 (Optional)</Label>
                <Textarea
                  id="msg3-personalization2"
                  value={template.message_3.personalization_instruction_2 || ""}
                  onChange={(e) => updateMessageTemplate(3, "personalization_instruction_2", e.target.value)}
                  className="mt-2 min-h-[100px]"
                  placeholder="Leave empty to skip second personalization..."
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Use {"{personalization2}"} in your template to place this content separately from the first personalization.
                </p>
              </div>

              <div onKeyDown={(e) => e.stopPropagation()}>
                <Label htmlFor="msg3-ctas">CTA Options (one per line)</Label>
                <Textarea
                  id="msg3-ctas"
                  value={template.message_3.cta_options?.join("\n") || ""}
                  onChange={(e) => updateArrayField(3, "cta_options", e.target.value)}
                  className="mt-2 min-h-[100px]"
                />
              </div>

              <div onKeyDown={(e) => e.stopPropagation()}>
                <Label htmlFor="msg3-signatures">Signature Options</Label>
                <Textarea
                  id="msg3-signatures"
                  value={template.message_3.signature_options?.join("\n\n") || ""}
                  onChange={(e) => updateArrayField(3, "signature_options", e.target.value)}
                  className="mt-2 min-h-[80px]"
                  placeholder="Best,&#10;Zarek Livak&#10;&#10;Best regards,&#10;Zarek Livak&#10;&#10;Cheers,&#10;Zarek"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Separate each signature with a blank line. Signatures can be multi-line (e.g., "Best,\nZarek Livak").
                </p>
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* Message 4 */}
          <AccordionItem value="message-4">
            <AccordionTrigger className="text-base font-medium text-brand-hull-white">
              Message 4 (Final Follow-up)
            </AccordionTrigger>
            <AccordionContent className="space-y-4 pt-4">
              <div onKeyDown={(e) => e.stopPropagation()}>
                <Label htmlFor="msg4-template">Template</Label>
                <Textarea
                  id="msg4-template"
                  value={template.message_4.template}
                  onChange={(e) => updateMessageTemplate(4, "template", e.target.value)}
                  className="mt-2 min-h-[180px] font-mono text-sm"
                />
              </div>

              <div onKeyDown={(e) => e.stopPropagation()}>
                <Label htmlFor="msg4-personalization">Personalization Instruction (Optional)</Label>
                <Textarea
                  id="msg4-personalization"
                  value={template.message_4.personalization_instruction || ""}
                  onChange={(e) => updateMessageTemplate(4, "personalization_instruction", e.target.value)}
                  className="mt-2 min-h-[100px]"
                />
              </div>

              <div onKeyDown={(e) => e.stopPropagation()}>
                <Label htmlFor="msg4-personalization2">Personalization Instruction 2 (Optional)</Label>
                <Textarea
                  id="msg4-personalization2"
                  value={template.message_4.personalization_instruction_2 || ""}
                  onChange={(e) => updateMessageTemplate(4, "personalization_instruction_2", e.target.value)}
                  className="mt-2 min-h-[100px]"
                  placeholder="Leave empty to skip second personalization..."
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Use {"{personalization2}"} in your template to place this content separately from the first personalization.
                </p>
              </div>

              <div onKeyDown={(e) => e.stopPropagation()}>
                <Label htmlFor="msg4-acknowledgments">Acknowledgment Options (one per line)</Label>
                <Textarea
                  id="msg4-acknowledgments"
                  value={template.message_4.acknowledgment_options?.join("\n") || ""}
                  onChange={(e) => updateArrayField(4, "acknowledgment_options", e.target.value)}
                  className="mt-2 min-h-[80px]"
                />
              </div>

              <div onKeyDown={(e) => e.stopPropagation()}>
                <Label htmlFor="msg4-graceful-exit">Graceful Exit Instruction (Optional)</Label>
                <Textarea
                  id="msg4-graceful-exit"
                  value={template.message_4.graceful_exit_instruction || ""}
                  onChange={(e) => updateMessageTemplate(4, "graceful_exit_instruction", e.target.value)}
                  className="mt-2 min-h-[100px]"
                />
              </div>

              <div onKeyDown={(e) => e.stopPropagation()}>
                <Label htmlFor="msg4-ctas">CTA Options (one per line)</Label>
                <Textarea
                  id="msg4-ctas"
                  value={template.message_4.cta_options?.join("\n") || ""}
                  onChange={(e) => updateArrayField(4, "cta_options", e.target.value)}
                  className="mt-2 min-h-[80px]"
                />
              </div>

              <div onKeyDown={(e) => e.stopPropagation()}>
                <Label htmlFor="msg4-signatures">Signature Options</Label>
                <Textarea
                  id="msg4-signatures"
                  value={template.message_4.signature_options?.join("\n\n") || ""}
                  onChange={(e) => updateArrayField(4, "signature_options", e.target.value)}
                  className="mt-2 min-h-[80px]"
                  placeholder="Best,&#10;Zarek Livak&#10;&#10;Best regards,&#10;Zarek Livak&#10;&#10;Cheers,&#10;Zarek"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Separate each signature with a blank line. Signatures can be multi-line (e.g., "Best,\nZarek Livak").
                </p>
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </Card>

      {/* Variable Reference Panel */}
      <Card className="p-6 bg-brand-ocean-blue/70 backdrop-blur-sm border-brand-container-rust/40 shadow-xl">
        <Accordion type="single" collapsible className="w-full">
          <AccordionItem value="variable-reference" className="border-none">
            <AccordionTrigger className="text-base font-semibold hover:no-underline text-brand-hull-white">
              <div className="flex items-center gap-2">
                <Info className="h-5 w-5 text-brand-container-rust" />
                <span>Available Template Variables</span>
              </div>
            </AccordionTrigger>
            <AccordionContent className="pt-4">
              <VariableReference />
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </Card>

      {/* Test Industry Selection */}
      <Card className="p-6 bg-brand-ocean-blue/70 backdrop-blur-sm border-brand-container-rust/40 shadow-xl">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="test-industry" className="text-base font-semibold text-brand-hull-white">
              Test with Specific Industry (Optional)
            </Label>
          </div>
          <Select value={testIndustry} onValueChange={setTestIndustry}>
            <SelectTrigger id="test-industry" className="w-full">
              <SelectValue placeholder="Auto-detect from research" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="auto-detect">Auto-detect from research</SelectItem>
              <SelectItem value="broker">Freight Broker</SelectItem>
              <SelectItem value="carrier">Carrier</SelectItem>
              <SelectItem value="3pl">3PL</SelectItem>
              <SelectItem value="ltl carrier">LTL Carrier</SelectItem>
              <SelectItem value="ocean carrier">Ocean Carrier</SelectItem>
              <SelectItem value="air freight">Air Freight (Cargo)</SelectItem>
              <SelectItem value="commercial airline">Commercial Airline (Passenger)</SelectItem>
              <SelectItem value="forwarder">Freight Forwarder</SelectItem>
              <SelectItem value="shipper">Shipper</SelectItem>
              <SelectItem value="manufacturer">Manufacturer</SelectItem>
            </SelectContent>
          </Select>
          <p className="text-xs text-muted-foreground">
            Select an industry to test how messages look with specific use cases. Leave as "Auto-detect" to use the detection logic based on company research.
          </p>
        </div>
      </Card>

      {/* Action Buttons */}
      <div className="flex flex-col gap-4">
        <div className="flex gap-3">
          <Button
            onClick={applyChanges}
            disabled={!hasUnsavedChanges}
            variant={hasUnsavedChanges ? "default" : "secondary"}
            size="lg"
            className={`flex-1 ${hasUnsavedChanges ? 'animate-pulse' : ''}`}
          >
            <FileEdit className="h-4 w-4 mr-2" />
            {hasUnsavedChanges ? "Apply Changes for Next Run" : "✓ No Changes to Apply"}
          </Button>
          <Button
            onClick={testTemplate}
            disabled={testing}
            variant="outline"
            size="lg"
            className="flex-1"
          >
            <Play className="h-4 w-4 mr-2" />
            {testing ? "Testing..." : "Test with 3 Contacts"}
          </Button>
        </div>
        <div className="text-xs text-center text-muted-foreground space-y-1">
          <p>
            {hasUnsavedChanges
              ? "⚠️ You have unsaved changes. Click 'Apply Changes' to use them in your next pipeline run."
              : "✓ Your changes are applied and will be used for the next pipeline run."}
          </p>
          <p>
            Switch to the "Pipeline Configuration" tab to run the pipeline with these custom templates.
          </p>
        </div>
      </div>

      {/* Test Logs */}
      {testLogs.length > 0 && (
        <Card className="p-6 bg-brand-ocean-blue/70 backdrop-blur-sm border-brand-container-rust/40 shadow-xl">
          <div className="space-y-2">
            <h3 className="text-sm font-semibold flex items-center gap-2 text-brand-hull-white">
              <span className="h-2 w-2 rounded-full bg-brand-deck-green animate-pulse" />
              Test Execution Log
            </h3>
            <div className="bg-brand-anchor-black/40 rounded-lg p-4 font-mono text-sm max-h-[300px] overflow-y-auto border border-brand-container-rust/30">
              {testLogs.map((log, idx) => (
                <div key={idx} className="text-brand-cargo-khaki">
                  {log}
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* Test Results */}
      {testResults.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-brand-hull-white">Test Results</h3>

          {testResults.map((result, idx) => (
            <Card key={idx} className="p-6 bg-brand-anchor-black/40 border-brand-container-rust/30">
              <div className="space-y-4">
                <div className="border-b border-brand-container-rust/30 pb-3">
                  <h4 className="font-semibold text-brand-hull-white">
                    {result.prospect.first_name} {result.prospect.last_name}
                  </h4>
                  <p className="text-sm text-brand-cargo-khaki">
                    {result.prospect.title} at {result.prospect.company_name}
                  </p>
                </div>

                <Accordion type="single" collapsible>
                  {[1, 2, 3, 4].map((num) => (
                    <AccordionItem key={num} value={`result-msg-${num}`} className="border-brand-container-rust/20">
                      <AccordionTrigger className="text-sm text-brand-hull-white hover:text-brand-container-rust">
                        Message {num}
                      </AccordionTrigger>
                      <AccordionContent>
                        <div
                          className="p-4 bg-brand-ocean-blue/30 rounded-md whitespace-pre-wrap text-sm font-mono text-brand-cargo-khaki border border-brand-ocean-blue/50"
                          dangerouslySetInnerHTML={{
                            __html: result.messages[`message_${num}` as keyof typeof result.messages]
                          }}
                        />
                      </AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default TemplateEditor;
export type { SubjectLineConfig };
