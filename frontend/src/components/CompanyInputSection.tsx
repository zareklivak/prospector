import { ClipboardList, Rocket } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface RoleLevels {
  c_suite: boolean;
  vp: boolean;
  director: boolean;
  manager: boolean;
}

interface CompanyInputSectionProps {
  domains: string;
  setDomains: (value: string) => void;
  contactsPerCompany: number;
  setContactsPerCompany: (value: number) => void;
  messageMode: "email" | "linkedin";
  setMessageMode: (value: "email" | "linkedin") => void;
  enrichEmails: boolean;
  setEnrichEmails: (value: boolean) => void;
  waterfallEnrichment: boolean;
  setWaterfallEnrichment: (value: boolean) => void;
  verifyCurrentEmployment: boolean;
  setVerifyCurrentEmployment: (value: boolean) => void;
  skipLinkedIn: boolean;
  setSkipLinkedIn: (value: boolean) => void;
  prospectOnly: boolean;
  setProspectOnly: (value: boolean) => void;
  includeUnverifiedContacts: boolean;
  setIncludeUnverifiedContacts: (value: boolean) => void;
  minScore: number;
  setMinScore: (value: number) => void;
  minProfileQuality: number;
  setMinProfileQuality: (value: number) => void;
  companyType: string;
  setCompanyType: (value: string) => void;
  roleLevels: RoleLevels;
  setRoleLevels: (value: RoleLevels) => void;
  maxInitialScrape: number;
  setMaxInitialScrape: (value: number) => void;
  onRunPipeline: () => void;
  isRunning: boolean;
}

const CompanyInputSection = ({
  domains,
  setDomains,
  contactsPerCompany,
  setContactsPerCompany,
  messageMode,
  setMessageMode,
  enrichEmails,
  setEnrichEmails,
  waterfallEnrichment,
  setWaterfallEnrichment,
  verifyCurrentEmployment,
  setVerifyCurrentEmployment,
  skipLinkedIn,
  setSkipLinkedIn,
  prospectOnly,
  setProspectOnly,
  includeUnverifiedContacts,
  setIncludeUnverifiedContacts,
  minScore,
  setMinScore,
  minProfileQuality,
  setMinProfileQuality,
  companyType,
  setCompanyType,
  roleLevels,
  setRoleLevels,
  maxInitialScrape,
  setMaxInitialScrape,
  onRunPipeline,
  isRunning,
}: CompanyInputSectionProps) => {
  const handleRoleLevelChange = (level: keyof RoleLevels, checked: boolean) => {
    setRoleLevels({ ...roleLevels, [level]: checked });
  };
  return (
    <Card className="p-6 bg-brand-ocean-blue/70 backdrop-blur-sm border-brand-container-rust/40 shadow-xl">
      <div className="flex items-center gap-2 mb-6">
        <ClipboardList className="h-5 w-5 text-brand-container-rust" />
        <h2 className="text-lg font-semibold text-brand-hull-white">Company Input</h2>
      </div>

      <div className="space-y-6">
        <div>
          <Label htmlFor="domains" className="mb-2 block text-brand-hull-white font-medium">
            Enter company domains (one per line):
          </Label>
          <Textarea
            id="domains"
            placeholder="fedex.com&#10;ups.com&#10;dhl.com"
            value={domains}
            onChange={(e) => setDomains(e.target.value)}
            className="min-h-[120px] font-mono text-sm"
            disabled={isRunning}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <Label htmlFor="contacts" className="mb-2 block text-brand-hull-white font-medium">
              Contacts per company (to export):
            </Label>
            <Input
              id="contacts"
              type="number"
              min="1"
              max="1000"
              value={contactsPerCompany}
              onChange={(e) => setContactsPerCompany(Number(e.target.value))}
              disabled={isRunning}
              placeholder="50"
            />
          </div>

          <div>
            <Label htmlFor="maxInitialScrape" className="mb-2 block text-brand-hull-white font-medium">
              Max contacts to scrape (before scoring):
            </Label>
            <Input
              id="maxInitialScrape"
              type="number"
              min="100"
              max="10000"
              value={maxInitialScrape}
              onChange={(e) => setMaxInitialScrape(Number(e.target.value))}
              disabled={isRunning}
              placeholder="2000"
            />
            <p className="text-xs text-brand-cargo-khaki mt-1">
              Increase when including Managers to capture more titles
            </p>
          </div>
        </div>

        {/* Role Level Filters */}
        <div>
          <Label className="mb-3 block text-brand-hull-white font-medium">Role levels to scrape:</Label>
          <div className="flex flex-wrap gap-6">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="role_c_suite"
                checked={roleLevels.c_suite}
                onCheckedChange={(checked) => handleRoleLevelChange('c_suite', checked as boolean)}
                disabled={isRunning}
                className="h-5 w-5"
              />
              <Label htmlFor="role_c_suite" className="cursor-pointer text-brand-hull-white">
                C-Suite/Head
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="role_vp"
                checked={roleLevels.vp}
                onCheckedChange={(checked) => handleRoleLevelChange('vp', checked as boolean)}
                disabled={isRunning}
                className="h-5 w-5"
              />
              <Label htmlFor="role_vp" className="cursor-pointer text-brand-hull-white">
                VP
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="role_director"
                checked={roleLevels.director}
                onCheckedChange={(checked) => handleRoleLevelChange('director', checked as boolean)}
                disabled={isRunning}
                className="h-5 w-5"
              />
              <Label htmlFor="role_director" className="cursor-pointer text-brand-hull-white">
                Director
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="role_manager"
                checked={roleLevels.manager}
                onCheckedChange={(checked) => handleRoleLevelChange('manager', checked as boolean)}
                disabled={isRunning}
                className="h-5 w-5"
              />
              <Label htmlFor="role_manager" className="cursor-pointer text-brand-hull-white">
                Manager
              </Label>
            </div>
          </div>
          <p className="text-xs text-brand-cargo-khaki mt-2">
            Select which seniority levels to include from Apollo. By default, Director+ levels are selected.
            Enable <strong>Manager</strong> to include manager-level titles (consider increasing max scrape above).
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <Label htmlFor="minScore" className="mb-2 block text-brand-hull-white font-medium">
              Minimum ICP fit score (1-10):
            </Label>
            <Input
              id="minScore"
              type="number"
              min="1"
              max="10"
              value={minScore}
              onChange={(e) => setMinScore(Number(e.target.value))}
              disabled={isRunning}
              placeholder="1"
            />
          </div>

          <div>
            <Label htmlFor="minProfileQuality" className="mb-2 block text-brand-hull-white font-medium">
              Minimum Profile Quality Score (1-10):
            </Label>
            <Input
              id="minProfileQuality"
              type="number"
              min="1"
              max="10"
              value={minProfileQuality}
              onChange={(e) => setMinProfileQuality(Number(e.target.value))}
              disabled={isRunning}
              placeholder="1"
            />
            <p className="text-xs text-brand-cargo-khaki mt-2">
              Filter contacts by LinkedIn profile completeness: <strong>1</strong> = No filtering (all profiles),
              <strong> 5</strong> = Medium quality, <strong> 10</strong> = Excellent (complete profiles with rich data)
            </p>
          </div>
        </div>

        <div>
          <Label className="mb-3 block text-brand-hull-white font-medium">Message mode:</Label>
          <RadioGroup
            value={messageMode}
            onValueChange={(value) => {
              setMessageMode(value as "email" | "linkedin");
              // If switching to email mode, uncheck include unverified contacts
              if (value === "email") {
                setIncludeUnverifiedContacts(false);
              }
            }}
            disabled={isRunning}
            className="flex gap-6"
          >
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="email" id="email" />
              <Label htmlFor="email" className="cursor-pointer text-brand-hull-white">
                Email
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="linkedin" id="linkedin" />
              <Label htmlFor="linkedin" className="cursor-pointer text-brand-hull-white">
                LinkedIn
              </Label>
            </div>
          </RadioGroup>
          <p className="text-xs text-brand-cargo-khaki mt-2">
            Controls output format: <strong>Email</strong> generates HTML for Instantly.ai (threading compatible),
            <strong> LinkedIn</strong> generates plain text for LinkedIn automation tools.
          </p>
        </div>

        <div>
          <Label htmlFor="companyType" className="mb-2 block text-brand-hull-white font-medium">
            Target Industry/Vertical:
          </Label>
          <Select value={companyType} onValueChange={setCompanyType} disabled={isRunning}>
            <SelectTrigger id="companyType">
              <SelectValue placeholder="Auto-detect from company research" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="auto">Auto-detect from company research</SelectItem>
              <SelectItem value="carrier">Carrier (Trucking - FTL/LTL)</SelectItem>
              <SelectItem value="freight_broker">Freight Broker</SelectItem>
              <SelectItem value="3pl">3PL/4PL/Forwarder</SelectItem>
              <SelectItem value="ocean_carrier">Ocean Carrier</SelectItem>
              <SelectItem value="air_freight">Air Freight & Commercial Airlines</SelectItem>
              <SelectItem value="food_distributor">Food Distributor</SelectItem>
              <SelectItem value="shipper">Shipper/Manufacturer</SelectItem>
              <SelectItem value="warehousing">Warehousing/Distribution Center</SelectItem>
              <SelectItem value="customs_broker">Customs Broker</SelectItem>
            </SelectContent>
          </Select>
          <p className="text-xs text-brand-cargo-khaki mt-2">
            <strong>Affects template variables:</strong> This controls <code>{`{use_cases_short}`}</code>, <code>{`{use_cases_long}`}</code>, <code>{`{value_prop_short}`}</code>, and <code>{`{value_prop_long}`}</code> in your message templates.
            <br />
            • <strong>Use cases</strong> are intelligently selected based on the person's job title and LinkedIn research (e.g., Operations → appointment scheduling, Sales → inbound sales)
            <br />
            • <strong>Value props</strong> are also intelligently selected based on the person's job title and role (e.g., COO sees operational efficiency, CFO sees cost reduction)
            <br />
            Choose the industry matching your targets, or use <strong>Auto-detect</strong> to let AI determine it from company research.
          </p>
        </div>

        {/* Email Enrichment Section */}
        <div className="bg-brand-anchor-black/30 rounded-lg p-4 space-y-3">
          <h3 className="text-brand-hull-white font-semibold text-sm uppercase tracking-wide mb-3">Email Enrichment</h3>

          <div className="flex items-center space-x-3">
            <Checkbox
              id="enrich"
              checked={enrichEmails}
              onCheckedChange={(checked) => setEnrichEmails(checked as boolean)}
              disabled={isRunning}
              className="h-5 w-5"
            />
            <Label htmlFor="enrich" className="cursor-pointer text-brand-hull-white font-medium text-base">
              Enrich & verify emails
            </Label>
          </div>

          {/* Fast/Thorough mode selection - only show when enrichEmails is enabled */}
          {enrichEmails && (
            <div className="ml-8 mt-2">
              <RadioGroup
                value={waterfallEnrichment ? "thorough" : "fast"}
                onValueChange={(value) => setWaterfallEnrichment(value === "thorough")}
                disabled={isRunning}
                className="space-y-2"
              >
                <div className="flex items-start space-x-2">
                  <RadioGroupItem value="fast" id="enrichFast" className="mt-0.5" />
                  <div>
                    <Label htmlFor="enrichFast" className="cursor-pointer text-brand-hull-white font-medium">
                      Fast (Apollo only)
                    </Label>
                    <p className="text-xs text-brand-cargo-khaki">
                      Uses Apollo + Instantly.ai verification. ~3x faster, ~$0.02 per contact.
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-2">
                  <RadioGroupItem value="thorough" id="enrichThorough" className="mt-0.5" />
                  <div>
                    <Label htmlFor="enrichThorough" className="cursor-pointer text-brand-hull-white font-medium">
                      Thorough (Apollo → Hunter → Findymail)
                    </Label>
                    <p className="text-xs text-brand-cargo-khaki">
                      Tries all providers until verified email found. Catches ~3% more emails, ~$0.02-0.06 per contact.
                    </p>
                  </div>
                </div>
              </RadioGroup>
            </div>
          )}
        </div>

        {/* Pipeline Options Section */}
        <div className="bg-brand-anchor-black/30 rounded-lg p-4 space-y-3">
          <h3 className="text-brand-hull-white font-semibold text-sm uppercase tracking-wide mb-3">Pipeline Options</h3>

          <div className="flex items-center space-x-3">
            <Checkbox
              id="prospectOnly"
              checked={prospectOnly}
              onCheckedChange={(checked) => {
                setProspectOnly(checked as boolean);
                // If enabling prospect-only, disable verify current employment (requires LinkedIn scrape)
                if (checked) {
                  setVerifyCurrentEmployment(false);
                }
              }}
              disabled={isRunning}
              className="h-5 w-5"
            />
            <Label htmlFor="prospectOnly" className="cursor-pointer text-brand-hull-white font-medium text-base">
              Prospect-only mode
            </Label>
          </div>
          <p className="text-xs text-brand-cargo-khaki ml-8">
            Only runs Phase 1 (Apollo scrape + scoring). Skips LinkedIn enrichment and message generation.
            Use this to quickly build prospect lists with emails.
          </p>

          <div className="flex items-center space-x-3">
            <Checkbox
              id="skipLinkedIn"
              checked={skipLinkedIn}
              onCheckedChange={(checked) => {
                setSkipLinkedIn(checked as boolean);
                // If enabling skip LinkedIn, disable verify current employment (requires LinkedIn data)
                if (checked) {
                  setVerifyCurrentEmployment(false);
                }
              }}
              disabled={isRunning || prospectOnly}
              className="h-5 w-5"
            />
            <Label
              htmlFor="skipLinkedIn"
              className={`cursor-pointer font-medium text-base ${prospectOnly ? 'text-brand-cargo-khaki/50' : 'text-brand-hull-white'}`}
            >
              Skip LinkedIn scraping
            </Label>
          </div>
          <p className="text-xs text-brand-cargo-khaki ml-8">
            Saves ~$0.10 per contact by skipping LinkedIn profile/posts scraping.
            Messages will be generated from company research only.
          </p>

          <div className="flex items-center space-x-3 ml-6">
            <Checkbox
              id="verifyEmployment"
              checked={verifyCurrentEmployment}
              onCheckedChange={(checked) => setVerifyCurrentEmployment(checked as boolean)}
              disabled={isRunning || prospectOnly || skipLinkedIn}
              className="h-5 w-5"
            />
            <Label
              htmlFor="verifyEmployment"
              className={`cursor-pointer font-medium text-base ${(prospectOnly || skipLinkedIn) ? 'text-brand-cargo-khaki/50' : 'text-brand-hull-white'}`}
            >
              Verify current employment
            </Label>
          </div>
          <p className="text-xs text-brand-cargo-khaki ml-14">
            Cross-checks LinkedIn "Current Position" against target company. Filters out contacts who have moved.
            Requires LinkedIn scraping to be enabled.
          </p>

          {/* Include unverified contacts checkbox - only visible in LinkedIn mode */}
          {messageMode === "linkedin" && (
            <>
              <div className="flex items-center space-x-3">
                <Checkbox
                  id="includeUnverified"
                  checked={includeUnverifiedContacts}
                  onCheckedChange={(checked) => setIncludeUnverifiedContacts(checked as boolean)}
                  disabled={isRunning}
                  className="h-5 w-5"
                />
                <Label
                  htmlFor="includeUnverified"
                  className="cursor-pointer font-medium text-base text-brand-hull-white"
                >
                  Include contacts without verified emails
                </Label>
              </div>
              <p className="text-xs text-brand-cargo-khaki ml-8">
                For LinkedIn-only outreach. Includes contacts even if they don't have a verified email.
              </p>
            </>
          )}
        </div>

        <Button
          onClick={onRunPipeline}
          disabled={isRunning || !domains.trim()}
          className="w-full bg-brand-container-rust hover:bg-brand-container-rust/80 text-brand-anchor-black font-semibold shadow-lg transition-all"
          size="lg"
        >
          <Rocket className="h-5 w-5 mr-2" />
          {isRunning ? "Pipeline Running..." : "Run Pipeline"}
        </Button>
      </div>
    </Card>
  );
};

export default CompanyInputSection;
