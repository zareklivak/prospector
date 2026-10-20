import { Info, Copy, Check } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Card } from "@/components/ui/card";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";

/**
 * VariableReference Component
 *
 * Displays available template variables with examples and usage guidance.
 * Helps users understand what variables they can use when creating custom message templates.
 */

interface VariableInfo {
  name: string;
  description: string;
  example: string;
  bestUsedIn?: string;
}

const VariableReference = () => {
  const { toast } = useToast();
  const [copiedVariable, setCopiedVariable] = useState<string>("");

  const copyToClipboard = (variable: string) => {
    navigator.clipboard.writeText(`{${variable}}`);
    setCopiedVariable(variable);
    toast({
      title: "Copied!",
      description: `{${variable}} copied to clipboard`,
    });
    setTimeout(() => setCopiedVariable(""), 2000);
  };

  const useCaseVariables: VariableInfo[] = [
    {
      name: "use_cases_short",
      description: "2 use cases - Concise, punchy list",
      example: "driver recruiting and customer support",
      bestUsedIn: "Message 1 (intro)",
    },
    {
      name: "use_cases_long",
      description: "4 use cases - Comprehensive list",
      example: "driver recruiting, customer support, appointment scheduling, and tracking updates",
      bestUsedIn: "Message 3 (deep dive)",
    },
  ];

  const valuePropsVariables: VariableInfo[] = [
    {
      name: "value_prop_short",
      description: "1 value prop - Single, focused outcome",
      example: "scaling ops without adding headcount",
      bestUsedIn: "Messages 1-2 (concise)",
    },
    {
      name: "value_prop_long",
      description: "3 value props - Multiple outcomes",
      example: "scaling ops, improving visibility, and tightening handoffs",
      bestUsedIn: "Message 3 (detailed)",
    },
  ];

  const contactVariables: VariableInfo[] = [
    {
      name: "first_name",
      description: "Contact's first name",
      example: "John",
    },
    {
      name: "company_name_short",
      description: "Shortened company name",
      example: "Werner (from Werner Enterprises)",
    },
  ];

  const templateVariables: VariableInfo[] = [
    {
      name: "cta",
      description: "Call-to-action (randomized)",
      example: "Open to sending over more details?",
    },
    {
      name: "signature",
      description: "Email signature (randomized)",
      example: "Best,\\nZarek Livak",
    },
    {
      name: "personalization",
      description: "LLM-generated personalization",
      example: "I saw your post about AI in supply chain...",
    },
    {
      name: "graceful_exit",
      description: "Final message exit line",
      example: "Either way, good luck with the transformation...",
    },
  ];

  const renderVariableCard = (variable: VariableInfo) => (
    <div
      key={variable.name}
      className="mb-3 p-3 rounded-lg border border-brand-container-rust/30 hover:border-brand-container-rust hover:bg-brand-ocean-blue/30 transition-all cursor-pointer bg-brand-anchor-black/20"
      onClick={() => copyToClipboard(variable.name)}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <code className="text-sm font-semibold text-brand-container-rust">
              {`{${variable.name}}`}
            </code>
            {copiedVariable === variable.name ? (
              <Check className="h-3 w-3 text-brand-deck-green" />
            ) : (
              <Copy className="h-3 w-3 text-brand-cargo-khaki" />
            )}
          </div>
          <p className="text-xs text-brand-cargo-khaki mb-2">{variable.description}</p>
          <div className="text-xs bg-brand-anchor-black/40 p-2 rounded border border-brand-ocean-blue/50 font-mono text-brand-hull-white">
            {variable.example}
          </div>
          {variable.bestUsedIn && (
            <p className="text-xs text-brand-buoy-yellow mt-2 font-medium">
              💡 Best for: {variable.bestUsedIn}
            </p>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <Card className="p-4 max-h-[800px] overflow-y-auto bg-brand-ocean-blue/70 backdrop-blur-sm border-brand-container-rust/40">
      <div className="flex items-center gap-2 mb-4">
        <Info className="h-5 w-5 text-brand-container-rust" />
        <h3 className="font-semibold text-lg text-brand-hull-white">Available Variables</h3>
      </div>

      <Alert className="mb-4 bg-brand-anchor-black/30 border-brand-ocean-blue/50">
        <AlertDescription className="text-sm text-brand-cargo-khaki">
          Click any variable to copy it. All variables are automatically populated with relevant content based on the contact's industry and title.
        </AlertDescription>
      </Alert>

      {/* Use Case Variables */}
      <div className="mb-6">
        <h4 className="font-semibold text-sm mb-3 text-brand-hull-white flex items-center gap-2">
          <span className="bg-purple-100 text-purple-700 px-2 py-1 rounded text-xs">
            USE CASES
          </span>
          <span className="text-xs font-normal text-brand-cargo-khaki">
            What Waypoint does
          </span>
        </h4>
        {useCaseVariables.map(renderVariableCard)}
      </div>

      {/* Value Prop Variables */}
      <div className="mb-6">
        <h4 className="font-semibold text-sm mb-3 text-brand-hull-white flex items-center gap-2">
          <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-xs">
            VALUE PROPS
          </span>
          <span className="text-xs font-normal text-brand-cargo-khaki">
            Business outcomes
          </span>
        </h4>
        {valuePropsVariables.map(renderVariableCard)}
      </div>

      {/* Contact Variables */}
      <div className="mb-6">
        <h4 className="font-semibold text-sm mb-3 text-brand-hull-white flex items-center gap-2">
          <span className="bg-yellow-100 text-yellow-700 px-2 py-1 rounded text-xs">
            CONTACT
          </span>
          <span className="text-xs font-normal text-brand-cargo-khaki">
            Personalization
          </span>
        </h4>
        {contactVariables.map(renderVariableCard)}
      </div>

      {/* Template Variables */}
      <div className="mb-6">
        <h4 className="font-semibold text-sm mb-3 text-brand-hull-white flex items-center gap-2">
          <span className="bg-orange-100 text-orange-700 px-2 py-1 rounded text-xs">
            TEMPLATE
          </span>
          <span className="text-xs font-normal text-brand-cargo-khaki">
            Randomized content
          </span>
        </h4>
        {templateVariables.map(renderVariableCard)}
      </div>

      {/* Usage Tips */}
      <div className="mt-6 p-4 bg-brand-anchor-black/30 rounded-lg border border-brand-container-rust/30">
        <h4 className="font-semibold text-sm mb-3 text-brand-hull-white">
          💡 Usage Tips
        </h4>
        <ul className="text-xs text-brand-hull-white space-y-2">
          <li className="flex items-start gap-2">
            <span className="text-brand-container-rust">•</span>
            <span>
              <strong>Message 1:</strong> Use <code className="bg-brand-anchor-black/60 px-1 rounded text-brand-buoy-yellow">{`{use_cases_short}`}</code> + <code className="bg-brand-anchor-black/60 px-1 rounded text-brand-buoy-yellow">{`{value_prop_short}`}</code> for concise intro
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-brand-container-rust">•</span>
            <span>
              <strong>Message 3:</strong> Use <code className="bg-brand-anchor-black/60 px-1 rounded text-brand-buoy-yellow">{`{use_cases_long}`}</code> + <code className="bg-brand-anchor-black/60 px-1 rounded text-brand-buoy-yellow">{`{value_prop_long}`}</code> for comprehensive deep dive
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-brand-container-rust">•</span>
            <span>
              All variables use natural language formatting - no clinical slashes or bullet points!
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-brand-container-rust">•</span>
            <span>
              Variables are title-aware - they automatically select the most relevant content for each contact's role
            </span>
          </li>
        </ul>
      </div>

      {/* Quick Reference */}
      <div className="mt-4 p-3 bg-brand-anchor-black/30 rounded-lg border border-brand-container-rust/30">
        <h4 className="font-semibold text-xs mb-2 text-brand-hull-white">
          📝 Quick Reference
        </h4>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div>
            <span className="font-semibold text-brand-cargo-khaki">Concise:</span>
            <div className="mt-1 space-y-1">
              <div className="font-mono text-brand-buoy-yellow">{`{use_cases_short}`}</div>
              <div className="font-mono text-brand-buoy-yellow">{`{value_prop_short}`}</div>
            </div>
          </div>
          <div>
            <span className="font-semibold text-brand-cargo-khaki">Detailed:</span>
            <div className="mt-1 space-y-1">
              <div className="font-mono text-brand-buoy-yellow">{`{use_cases_long}`}</div>
              <div className="font-mono text-brand-buoy-yellow">{`{value_prop_long}`}</div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default VariableReference;
