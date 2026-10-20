import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import {
  Rocket,
  Target,
  Mail,
  MessageSquare,
  Users,
  Sparkles,
  CheckCircle2,
  ArrowRight,
  Settings,
  FileText,
  Database,
  Cpu
} from "lucide-react";

interface DocsModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const DocsModal = ({ open, onOpenChange }: DocsModalProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl max-h-[90vh] bg-brand-ocean-blue/95 backdrop-blur-sm border-brand-container-rust/40">
        <DialogHeader>
          <DialogTitle className="text-2xl flex items-center gap-3 text-brand-hull-white">
            <div className="bg-brand-hull-white/10 p-2 rounded-lg backdrop-blur-sm border border-brand-hull-white/20">
              <img src="/logos/icon-white.svg" alt="Waypoint" className="h-6 w-6" />
            </div>
            Prospector Documentation
          </DialogTitle>
        </DialogHeader>

        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-4 bg-brand-anchor-black/40 border border-brand-container-rust/30">
            <TabsTrigger value="overview" className="data-[state=active]:bg-brand-container-rust data-[state=active]:text-brand-anchor-black text-brand-hull-white">Overview</TabsTrigger>
            <TabsTrigger value="pipeline" className="data-[state=active]:bg-brand-container-rust data-[state=active]:text-brand-anchor-black text-brand-hull-white">Pipeline Phases</TabsTrigger>
            <TabsTrigger value="templates" className="data-[state=active]:bg-brand-container-rust data-[state=active]:text-brand-anchor-black text-brand-hull-white">Templates</TabsTrigger>
            <TabsTrigger value="variables" className="data-[state=active]:bg-brand-container-rust data-[state=active]:text-brand-anchor-black text-brand-hull-white">Variables</TabsTrigger>
          </TabsList>

          <ScrollArea className="h-[600px] pr-4">
            {/* OVERVIEW TAB */}
            <TabsContent value="overview" className="space-y-6 mt-4">
              <div>
                <h2 className="text-xl font-semibold mb-3 flex items-center gap-2 text-brand-hull-white">
                  <Rocket className="h-5 w-5 text-brand-container-rust" />
                  What is Prospector?
                </h2>
                <p className="text-brand-cargo-khaki leading-relaxed">
                  Prospector is an end-to-end AI-powered B2B lead generation system designed specifically
                  for outbound sales to logistics and supply chain companies. It automates the entire prospecting
                  workflow - from finding decision-makers to generating personalized multi-step outreach sequences.
                </p>
              </div>

              <Card className="p-6 bg-brand-anchor-black/40 border-brand-container-rust/30">
                <h3 className="font-semibold mb-3 flex items-center gap-2 text-brand-hull-white">
                  <Target className="h-5 w-5 text-brand-container-rust" />
                  Who Is This For?
                </h3>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 text-brand-deck-green mt-0.5" />
                    <span className="text-brand-cargo-khaki"><strong className="text-brand-hull-white">Sales Teams:</strong> Generate qualified prospect lists with ready-to-send messages</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 text-brand-deck-green mt-0.5" />
                    <span className="text-brand-cargo-khaki"><strong className="text-brand-hull-white">SDRs/BDRs:</strong> Save hours on research and message writing</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 text-brand-deck-green mt-0.5" />
                    <span className="text-brand-cargo-khaki"><strong className="text-brand-hull-white">Marketing Teams:</strong> Create highly targeted campaigns at scale</span>
                  </li>
                </ul>
              </Card>

              <div>
                <h3 className="font-semibold mb-3 text-brand-hull-white">System Architecture: 3-Phase Pipeline</h3>
                <div className="space-y-3">
                  <Card className="p-4 bg-brand-anchor-black/40 border-purple-400/30">
                    <div className="flex items-start gap-3">
                      <div className="bg-purple-500/20 p-2 rounded-lg border border-purple-400/30">
                        <Database className="h-5 w-5 text-purple-300" />
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold text-brand-hull-white">Phase 1: Apollo Scraping & Lead Scoring</h4>
                        <p className="text-sm text-brand-cargo-khaki mt-1">
                          Finds Director+ contacts from target companies, scores them by role fit (1-10),
                          and ranks the best prospects.
                        </p>
                        <Badge variant="outline" className="mt-2 border-purple-400/50 text-purple-300">~2 min for 50 contacts</Badge>
                      </div>
                    </div>
                  </Card>

                  <Card className="p-4 bg-brand-anchor-black/40 border-brand-deck-green/30">
                    <div className="flex items-start gap-3">
                      <div className="bg-brand-deck-green/20 p-2 rounded-lg border border-brand-deck-green/30">
                        <Sparkles className="h-5 w-5 text-brand-deck-green" />
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold text-brand-hull-white">Phase 2: Enrichment & Research</h4>
                        <p className="text-sm text-brand-cargo-khaki mt-1">
                          Unlocks verified emails, scrapes LinkedIn profiles (work history, education, posts),
                          and researches company operations using AI.
                        </p>
                        <Badge variant="outline" className="mt-2 border-brand-deck-green/50 text-brand-deck-green">~3-5 min for 50 contacts</Badge>
                      </div>
                    </div>
                  </Card>

                  <Card className="p-4 bg-brand-anchor-black/40 border-brand-buoy-yellow/30">
                    <div className="flex items-start gap-3">
                      <div className="bg-brand-buoy-yellow/20 p-2 rounded-lg border border-brand-buoy-yellow/30">
                        <Cpu className="h-5 w-5 text-brand-buoy-yellow" />
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold text-brand-hull-white">Phase 3: AI Message Generation</h4>
                        <p className="text-sm text-brand-cargo-khaki mt-1">
                          Generates personalized 4-step sequences (email OR LinkedIn) using dual AI
                          (Claude Sonnet 4.5 + OpenAI GPT-4o) in parallel.
                        </p>
                        <Badge variant="outline" className="mt-2 border-brand-buoy-yellow/50 text-brand-buoy-yellow">~2 sec per contact</Badge>
                      </div>
                    </div>
                  </Card>
                </div>
              </div>

              <Card className="p-6 bg-brand-deck-green/20 border-brand-deck-green/40">
                <h3 className="font-semibold mb-3 flex items-center gap-2 text-brand-hull-white">
                  <CheckCircle2 className="h-5 w-5 text-brand-deck-green" />
                  What You Get
                </h3>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <ArrowRight className="h-4 w-4 text-brand-deck-green" />
                    <span className="text-brand-cargo-khaki">Verified email addresses from Apollo</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <ArrowRight className="h-4 w-4 text-brand-deck-green" />
                    <span className="text-brand-cargo-khaki">Rich LinkedIn profile data (work history, skills, posts)</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <ArrowRight className="h-4 w-4 text-brand-deck-green" />
                    <span className="text-brand-cargo-khaki">AI-researched company intelligence</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <ArrowRight className="h-4 w-4 text-brand-deck-green" />
                    <span className="text-brand-cargo-khaki">4-step personalized outreach sequences</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <ArrowRight className="h-4 w-4 text-brand-deck-green" />
                    <span className="text-brand-cargo-khaki">CSV ready for Instantly.ai, Hey Reach, or LinkedIn automation</span>
                  </li>
                </ul>
              </Card>
            </TabsContent>

            {/* PIPELINE PHASES TAB */}
            <TabsContent value="pipeline" className="space-y-6 mt-4">
              <div>
                <h2 className="text-xl font-semibold mb-4 text-brand-hull-white">Understanding the 3-Phase Pipeline</h2>
                <p className="text-brand-cargo-khaki mb-6">
                  Each phase builds on the previous one, progressively enriching your data and creating
                  personalized outreach sequences.
                </p>
              </div>

              {/* Phase 1 */}
              <Card className="p-6 bg-brand-anchor-black/40 border-purple-400/40">
                <div className="flex items-center gap-2 mb-4">
                  <Badge className="bg-purple-500 text-white border-0">Phase 1</Badge>
                  <h3 className="text-lg font-semibold text-brand-hull-white">Apollo Scraping & Lead Scoring</h3>
                </div>

                <div className="space-y-4">
                  <div>
                    <h4 className="font-semibold text-sm mb-2 text-brand-hull-white">What Happens:</h4>
                    <ol className="space-y-2 text-sm text-brand-cargo-khaki list-decimal list-inside">
                      <li>Connects to Apollo.io API with your target company domains</li>
                      <li>Searches for Director+ level contacts at those companies</li>
                      <li>Scrapes the first ~2,000 contacts that appear on Apollo for each company</li>
                      <li>Filters by seniority (Director, VP, C-Level)</li>
                      <li>Scores each contact 1-10 based on job title relevance</li>
                      <li>Ranks contacts by fit score and exports top N from the scored list</li>
                    </ol>
                  </div>

                  <div>
                    <h4 className="font-semibold text-sm mb-2 text-brand-hull-white">Intelligent Scoring System:</h4>
                    <div className="bg-brand-ocean-blue/30 p-3 rounded-lg text-sm space-y-1 text-brand-cargo-khaki border border-brand-ocean-blue/50">
                      <div><strong className="text-brand-hull-white">8-10 points:</strong> AI, Innovation, Transformation, Operations, Supply Chain roles</div>
                      <div><strong className="text-brand-hull-white">6-8 points:</strong> Strategy, Product, Engineering, IT roles</div>
                      <div><strong className="text-brand-hull-white">3-5 points:</strong> Finance, HR, Legal, Admin roles</div>
                      <div><strong className="text-brand-hull-white">Bonus:</strong> +2 for Chief/CXO titles, +1 for VP/Head</div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold text-sm mb-2 text-brand-hull-white">Output:</h4>
                    <p className="text-sm text-brand-cargo-khaki">
                      CSV with ranked contacts including: name, title, LinkedIn URL, company info, and fit score.
                      Emails show as <code className="bg-brand-anchor-black/60 px-1 rounded text-brand-buoy-yellow">verified</code> but display placeholder
                      (unlocked in Phase 2).
                    </p>
                    <p className="text-sm text-brand-cargo-khaki mt-2">
                      <strong className="text-brand-hull-white">Note:</strong> The system scrapes up to ~2,000 contacts per company from Apollo,
                      then filters and scores them to find the best matches. This ensures comprehensive coverage while focusing on top prospects.
                    </p>
                  </div>

                  <div className="bg-brand-deck-green/20 border border-brand-deck-green/40 p-3 rounded-lg">
                    <p className="text-sm text-brand-cargo-khaki"><strong className="text-brand-hull-white">Cost:</strong> Free! Apollo person search doesn't consume email credits.</p>
                  </div>
                </div>
              </Card>

              {/* Phase 2 */}
              <Card className="p-6 bg-brand-anchor-black/40 border-brand-deck-green/40">
                <div className="flex items-center gap-2 mb-4">
                  <Badge className="bg-brand-deck-green text-brand-anchor-black border-0">Phase 2</Badge>
                  <h3 className="text-lg font-semibold text-brand-hull-white">Enrichment & Research</h3>
                </div>

                <div className="space-y-4">
                  <div>
                    <h4 className="font-semibold text-sm mb-2 text-brand-hull-white">What Happens:</h4>
                    <ol className="space-y-2 text-sm text-brand-cargo-khaki list-decimal list-inside">
                      <li><strong className="text-brand-hull-white">Email Enrichment:</strong> Unlocks real verified emails from Apollo (optional, costs credits)</li>
                      <li><strong className="text-brand-hull-white">Email Verification:</strong> Double-verifies emails with Instantly.ai to filter out invalid/risky addresses (optional, reduces bounce rates)</li>
                      <li><strong className="text-brand-hull-white">LinkedIn Profile Scraping:</strong> Uses Apify to get full profile data (headline, about, experience, education, skills)</li>
                      <li><strong className="text-brand-hull-white">LinkedIn Posts Scraping:</strong> Grabs up to 5 recent posts for personalization hooks</li>
                      <li><strong className="text-brand-hull-white">Company Research:</strong> Uses Perplexity AI to research company operations, tech stack, innovation initiatives</li>
                      <li><strong className="text-brand-hull-white">Personal Research Synthesis:</strong> Combines profile + posts into coherent summary</li>
                    </ol>
                  </div>

                  <div>
                    <h4 className="font-semibold text-sm mb-2 text-brand-hull-white">What You Get Per Contact:</h4>
                    <div className="bg-brand-ocean-blue/30 p-3 rounded-lg text-sm space-y-2 text-brand-cargo-khaki border border-brand-ocean-blue/50">
                      <div><strong className="text-brand-hull-white">Real Email:</strong> Verified email address from Apollo</div>
                      <div><strong className="text-brand-hull-white">Email Verification Status:</strong> <code className="bg-brand-anchor-black/60 px-1 rounded text-brand-buoy-yellow">instantly_verified</code> column shows "verified" for deliverable emails or "not_verified" if verification was skipped</div>
                      <div><strong className="text-brand-hull-white">LinkedIn Phone:</strong> Phone number extracted from profile (when available)</div>
                      <div><strong className="text-brand-hull-white">Work Experience:</strong> Full employment history with roles, companies, tenure</div>
                      <div><strong className="text-brand-hull-white">Education:</strong> Schools, degrees, certifications</div>
                      <div><strong className="text-brand-hull-white">Skills:</strong> Top skills with endorsement counts</div>
                      <div><strong className="text-brand-hull-white">Influence Metrics:</strong> Connections & followers counts</div>
                      <div><strong className="text-brand-hull-white">Recent Activity:</strong> Up to 5 recent LinkedIn posts</div>
                      <div><strong className="text-brand-hull-white">Company Research:</strong> AI-generated summary of company operations</div>
                      <div><strong className="text-brand-hull-white">Profile Quality Score:</strong> 1-10 rating based on data completeness</div>
                    </div>
                  </div>

                  <div className="bg-blue-500/20 border border-blue-400/40 p-4 rounded-lg">
                    <h4 className="font-semibold text-sm mb-2 flex items-center gap-2 text-brand-hull-white">
                      <CheckCircle2 className="h-4 w-4 text-blue-300" />
                      Why Instantly.ai Verification?
                    </h4>
                    <p className="text-sm text-brand-cargo-khaki mb-2">
                      While Apollo provides verified emails, Instantly.ai adds a second layer of real-time validation to ensure deliverability:
                    </p>
                    <ul className="text-sm text-brand-cargo-khaki space-y-1 ml-4">
                      <li>• Filters out invalid emails (non-existent addresses)</li>
                      <li>• Removes risky emails (catch-all domains, disposable addresses)</li>
                      <li>• Blocks role-based emails (info@, support@, etc.)</li>
                      <li>• Protects your sender reputation and reduces bounce rates</li>
                    </ul>
                    <p className="text-xs text-blue-300 mt-2">💡 Only contacts with verified emails remain in your final CSV - invalid/risky emails are automatically filtered out.</p>
                  </div>

                  <div>
                    <h4 className="font-semibold text-sm mb-2 text-brand-hull-white">Cost Controls:</h4>
                    <ul className="text-sm text-brand-cargo-khaki space-y-1">
                      <li>• <code className="bg-brand-anchor-black/60 px-1 rounded text-brand-buoy-yellow">--enrich-emails</code> flag: Only unlock emails when needed</li>
                      <li>• <code className="bg-brand-anchor-black/60 px-1 rounded text-brand-buoy-yellow">--min-score</code> filter: Only enrich high-fit contacts (e.g., score ≥ 7)</li>
                      <li>• Max 5 posts per contact (prevents cost overruns)</li>
                      <li>• Company research shared across all contacts from same company</li>
                    </ul>
                  </div>

                  <div className="bg-brand-deck-green/20 border border-brand-deck-green/40 p-3 rounded-lg">
                    <p className="text-sm text-brand-cargo-khaki"><strong className="text-brand-hull-white">Cost:</strong> ~$0.02-0.05 per contact (Apollo + Apify + Perplexity)</p>
                  </div>
                </div>
              </Card>

              {/* Phase 3 */}
              <Card className="p-6 bg-brand-anchor-black/40 border-brand-buoy-yellow/40">
                <div className="flex items-center gap-2 mb-4">
                  <Badge className="bg-brand-buoy-yellow text-brand-anchor-black border-0">Phase 3</Badge>
                  <h3 className="text-lg font-semibold text-brand-hull-white">AI Message Generation</h3>
                </div>

                <div className="space-y-4">
                  <div>
                    <h4 className="font-semibold text-sm mb-2 text-brand-hull-white">Dual AI System:</h4>
                    <p className="text-sm text-brand-cargo-khaki mb-2">
                      Uses two cutting-edge AI models in parallel for speed and variation:
                    </p>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="bg-purple-500/20 border border-purple-400/40 p-3 rounded-lg">
                        <p className="font-semibold text-sm text-brand-hull-white">Claude Sonnet 4.5</p>
                        <p className="text-xs text-purple-300 mt-1">3 parallel workers</p>
                      </div>
                      <div className="bg-orange-500/20 border border-orange-400/40 p-3 rounded-lg">
                        <p className="font-semibold text-sm text-brand-hull-white">OpenAI GPT-4o</p>
                        <p className="text-xs text-orange-300 mt-1">3 parallel workers</p>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold text-sm mb-2 text-brand-hull-white">How It Works:</h4>
                    <ol className="space-y-2 text-sm text-brand-cargo-khaki list-decimal list-inside">
                      <li>Detects company type (carrier, broker, 3PL, etc.) from research</li>
                      <li>Selects most relevant use cases based on contact's title</li>
                      <li>Selects value propositions matched to their role</li>
                      <li>Generates all 4 messages in a single API call (batch generation)</li>
                      <li>Formats output for email (HTML) or LinkedIn (plain text)</li>
                      <li>Tracks which AI model generated each contact's messages</li>
                    </ol>
                  </div>

                  <div>
                    <h4 className="font-semibold text-sm mb-2 text-brand-hull-white">4-Step Message Strategy:</h4>
                    <div className="space-y-2">
                      <div className="bg-brand-ocean-blue/30 p-3 rounded-lg text-sm text-brand-cargo-khaki border border-brand-ocean-blue/50">
                        <strong className="text-brand-hull-white">Message 1:</strong> Personalized opener referencing their LinkedIn profile/posts,
                        brief intro to Waypoint with 2 relevant use cases, strong CTA
                      </div>
                      <div className="bg-brand-ocean-blue/30 p-3 rounded-lg text-sm text-brand-cargo-khaki border border-brand-ocean-blue/50">
                        <strong className="text-brand-hull-white">Message 2:</strong> Short bump, re-surface value, simple CTA
                      </div>
                      <div className="bg-brand-ocean-blue/30 p-3 rounded-lg text-sm text-brand-cargo-khaki border border-brand-ocean-blue/50">
                        <strong className="text-brand-hull-white">Message 3:</strong> Social proof, detailed explanation
                        with 4 use cases and 3 value props, deeper value proposition
                      </div>
                      <div className="bg-brand-ocean-blue/30 p-3 rounded-lg text-sm text-brand-cargo-khaki border border-brand-ocean-blue/50">
                        <strong className="text-brand-hull-white">Message 4:</strong> Final touch, acknowledge busy inbox, specific pain point,
                        graceful exit
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold text-sm mb-2 text-brand-hull-white">Performance:</h4>
                    <div className="grid grid-cols-3 gap-3">
                      <div className="bg-brand-deck-green/20 border border-brand-deck-green/40 p-3 rounded-lg text-center">
                        <p className="text-2xl font-bold text-brand-deck-green">2.0s</p>
                        <p className="text-xs text-brand-cargo-khaki mt-1">Per contact</p>
                      </div>
                      <div className="bg-brand-deck-green/20 border border-brand-deck-green/40 p-3 rounded-lg text-center">
                        <p className="text-2xl font-bold text-brand-deck-green">99.6%</p>
                        <p className="text-xs text-brand-cargo-khaki mt-1">Success rate</p>
                      </div>
                      <div className="bg-brand-deck-green/20 border border-brand-deck-green/40 p-3 rounded-lg text-center">
                        <p className="text-2xl font-bold text-brand-deck-green">$0.03</p>
                        <p className="text-xs text-brand-cargo-khaki mt-1">Cost per contact</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-brand-buoy-yellow/20 border border-brand-buoy-yellow/40 p-3 rounded-lg">
                    <p className="text-sm text-brand-cargo-khaki"><strong className="text-brand-hull-white">Output Format:</strong> Messages formatted with HTML
                    (email mode) or plain text (LinkedIn mode), ready for import to sending tools.</p>
                  </div>
                </div>
              </Card>
            </TabsContent>

            {/* TEMPLATES TAB */}
            <TabsContent value="templates" className="space-y-6 mt-4">
              <div>
                <h2 className="text-xl font-semibold mb-3 text-brand-hull-white">Understanding Message Templates</h2>
                <p className="text-brand-cargo-khaki">
                  Templates control how your AI-generated messages are structured. You can customize every
                  aspect - from the tone and style to specific CTAs and signatures.
                </p>
              </div>

              <Card className="p-6 bg-brand-anchor-black/40 border-brand-container-rust/30">
                <h3 className="font-semibold mb-3 text-brand-hull-white">Template Components</h3>
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-semibold mb-2 text-brand-hull-white">1. System Prompt</h4>
                    <p className="text-sm text-brand-cargo-khaki">
                      Defines the AI's writing style, tone, and rules. This is where you set voice
                      (professional, casual, technical), forbidden phrases, and formatting guidelines.
                    </p>
                  </div>

                  <div>
                    <h4 className="text-sm font-semibold mb-2 text-brand-hull-white">2. Message Templates</h4>
                    <p className="text-sm text-brand-cargo-khaki">
                      The actual structure of each message (1-4). Uses placeholders like <code className="bg-brand-anchor-black/60 px-1 rounded text-brand-buoy-yellow">{`{first_name}`}</code>
                      and <code className="bg-brand-anchor-black/60 px-1 rounded text-brand-buoy-yellow">{`{use_cases_short}`}</code> that get replaced with real data.
                    </p>
                  </div>

                  <div>
                    <h4 className="text-sm font-semibold mb-2 text-brand-hull-white">3. Personalization Instructions</h4>
                    <p className="text-sm text-brand-cargo-khaki">
                      Guides the AI on what to write in <code className="bg-brand-anchor-black/60 px-1 rounded text-brand-buoy-yellow">{`{personalization}`}</code> placeholders.
                      For example: "Reference their LinkedIn post" or "Mention their recent role change."
                    </p>
                  </div>

                  <div>
                    <h4 className="text-sm font-semibold mb-2 text-brand-hull-white">4. CTA Options</h4>
                    <p className="text-sm text-brand-cargo-khaki">
                      Pool of call-to-action phrases that get randomly selected for variation. Each message
                      can have its own CTA pool.
                    </p>
                  </div>

                  <div>
                    <h4 className="text-sm font-semibold mb-2 text-brand-hull-white">5. Signature Options</h4>
                    <p className="text-sm text-brand-cargo-khaki">
                      Different sign-off variations (e.g., "Best, Zarek" vs "Cheers, Zarek") for natural variety.
                    </p>
                  </div>
                </div>
              </Card>

              <Card className="p-6 bg-brand-buoy-yellow/20 border-brand-buoy-yellow/40">
                <h3 className="font-semibold mb-3 flex items-center gap-2 text-brand-hull-white">
                  <Settings className="h-5 w-5 text-brand-buoy-yellow" />
                  Template Library
                </h3>
                <div className="space-y-3 text-sm text-brand-cargo-khaki">
                  <p>You can save custom templates and reuse them across pipeline runs:</p>
                  <ul className="space-y-1 ml-4">
                    <li>• <strong className="text-brand-hull-white">Default Templates:</strong> Pre-built email & LinkedIn templates optimized for logistics outreach</li>
                    <li>• <strong className="text-brand-hull-white">Custom Templates:</strong> Save your own variations with custom tone, CTAs, etc.</li>
                    <li>• <strong className="text-brand-hull-white">Per-Run:</strong> Changes only apply to your next pipeline run (doesn't persist)</li>
                  </ul>
                </div>
              </Card>

              <Card className="p-6 bg-brand-anchor-black/40 border-brand-container-rust/30">
                <h3 className="font-semibold mb-3 text-brand-hull-white">Email vs LinkedIn Templates</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-blue-500/20 border border-blue-400/40 p-4 rounded-lg">
                    <h4 className="font-semibold mb-2 flex items-center gap-2 text-brand-hull-white">
                      <Mail className="h-4 w-4 text-blue-300" />
                      Email Mode
                    </h4>
                    <ul className="text-sm space-y-1 text-brand-cargo-khaki">
                      <li>• HTML formatting with <code className="bg-brand-anchor-black/60 px-1 rounded text-brand-buoy-yellow">&lt;br&gt;</code> tags</li>
                      <li>• Threading-compatible for Instantly.ai</li>
                      <li>• Works in Gmail, Outlook, etc.</li>
                      <li>• Longer, more detailed messages</li>
                    </ul>
                  </div>
                  <div className="bg-purple-500/20 border border-purple-400/40 p-4 rounded-lg">
                    <h4 className="font-semibold mb-2 flex items-center gap-2 text-brand-hull-white">
                      <MessageSquare className="h-4 w-4 text-purple-300" />
                      LinkedIn Mode
                    </h4>
                    <ul className="text-sm space-y-1 text-brand-cargo-khaki">
                      <li>• Plain text with natural line breaks</li>
                      <li>• Optimized for LinkedIn character limits</li>
                      <li>• More casual, conversational tone</li>
                      <li>• Shorter, punchier messages</li>
                    </ul>
                  </div>
                </div>
              </Card>
            </TabsContent>

            {/* VARIABLES TAB */}
            <TabsContent value="variables" className="space-y-6 mt-4">
              <div>
                <h2 className="text-xl font-semibold mb-3 text-brand-hull-white">Template Variables Reference</h2>
                <p className="text-brand-cargo-khaki">
                  Variables are placeholders in your templates that get replaced with intelligent,
                  personalized content. All variables are automatically populated based on the contact's
                  job title, company type, and LinkedIn research.
                </p>
              </div>

              <Card className="p-6 bg-brand-anchor-black/40 border-purple-400/40">
                <h3 className="font-semibold mb-4 flex items-center gap-2 text-brand-hull-white">
                  <Badge className="bg-purple-500 text-white border-0">NEW</Badge>
                  Use Case Variables (What Waypoint Does)
                </h3>
                <div className="space-y-3">
                  <div className="bg-purple-500/20 border border-purple-400/40 p-4 rounded-lg">
                    <code className="font-semibold text-purple-300">{`{use_cases_short}`}</code>
                    <p className="text-sm text-brand-cargo-khaki mt-2">
                      <strong className="text-brand-hull-white">2 use cases</strong> - Concise list for introductory messages
                    </p>
                    <div className="bg-brand-anchor-black/60 p-2 rounded mt-2 text-sm font-mono text-brand-buoy-yellow border border-brand-ocean-blue/50">
                      Example: "driver recruiting and customer support"
                    </div>
                    <Badge variant="outline" className="mt-2 border-purple-400/50 text-purple-300">Best for: Message 1</Badge>
                  </div>

                  <div className="bg-purple-500/20 border border-purple-400/40 p-4 rounded-lg">
                    <code className="font-semibold text-purple-300">{`{use_cases_long}`}</code>
                    <p className="text-sm text-brand-cargo-khaki mt-2">
                      <strong className="text-brand-hull-white">4 use cases</strong> - Comprehensive list for detailed messages
                    </p>
                    <div className="bg-brand-anchor-black/60 p-2 rounded mt-2 text-sm font-mono text-brand-buoy-yellow border border-brand-ocean-blue/50">
                      Example: "driver recruiting, customer support, appointment scheduling, and tracking updates"
                    </div>
                    <Badge variant="outline" className="mt-2 border-purple-400/50 text-purple-300">Best for: Message 3</Badge>
                  </div>
                </div>
              </Card>

              <Card className="p-6 bg-brand-anchor-black/40 border-brand-deck-green/40">
                <h3 className="font-semibold mb-4 flex items-center gap-2 text-brand-hull-white">
                  <Badge className="bg-brand-deck-green text-brand-anchor-black border-0">NEW</Badge>
                  Value Prop Variables (Business Outcomes)
                </h3>
                <div className="space-y-3">
                  <div className="bg-brand-deck-green/20 border border-brand-deck-green/40 p-4 rounded-lg">
                    <code className="font-semibold text-brand-deck-green">{`{value_prop_short}`}</code>
                    <p className="text-sm text-brand-cargo-khaki mt-2">
                      <strong className="text-brand-hull-white">1 value prop</strong> - Single, focused outcome
                    </p>
                    <div className="bg-brand-anchor-black/60 p-2 rounded mt-2 text-sm font-mono text-brand-buoy-yellow border border-brand-ocean-blue/50">
                      Example: "scaling ops without adding headcount"
                    </div>
                    <Badge variant="outline" className="mt-2 border-brand-deck-green/50 text-brand-deck-green">Best for: Messages 1-2</Badge>
                  </div>

                  <div className="bg-brand-deck-green/20 border border-brand-deck-green/40 p-4 rounded-lg">
                    <code className="font-semibold text-brand-deck-green">{`{value_prop_long}`}</code>
                    <p className="text-sm text-brand-cargo-khaki mt-2">
                      <strong className="text-brand-hull-white">3 value props</strong> - Multiple outcomes with natural "and" connectors
                    </p>
                    <div className="bg-brand-anchor-black/60 p-2 rounded mt-2 text-sm font-mono text-brand-buoy-yellow border border-brand-ocean-blue/50">
                      Example: "scaling ops without adding headcount, improving visibility, and tightening handoffs between teams"
                    </div>
                    <Badge variant="outline" className="mt-2 border-brand-deck-green/50 text-brand-deck-green">Best for: Message 3</Badge>
                  </div>
                </div>
              </Card>

              <Card className="p-6 bg-brand-anchor-black/40 border-brand-container-rust/30">
                <h3 className="font-semibold mb-4 text-brand-hull-white">Other Available Variables</h3>
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-brand-ocean-blue/30 p-3 rounded-lg border border-brand-ocean-blue/50">
                    <code className="text-sm font-semibold text-brand-container-rust">{`{first_name}`}</code>
                    <p className="text-xs text-brand-cargo-khaki mt-1">Contact's first name</p>
                  </div>
                  <div className="bg-brand-ocean-blue/30 p-3 rounded-lg border border-brand-ocean-blue/50">
                    <code className="text-sm font-semibold text-brand-container-rust">{`{company_name_short}`}</code>
                    <p className="text-xs text-brand-cargo-khaki mt-1">Shortened company name</p>
                  </div>
                  <div className="bg-brand-ocean-blue/30 p-3 rounded-lg border border-brand-ocean-blue/50">
                    <code className="text-sm font-semibold text-brand-container-rust">{`{cta}`}</code>
                    <p className="text-xs text-brand-cargo-khaki mt-1">Randomized call-to-action</p>
                  </div>
                  <div className="bg-brand-ocean-blue/30 p-3 rounded-lg border border-brand-ocean-blue/50">
                    <code className="text-sm font-semibold text-brand-container-rust">{`{signature}`}</code>
                    <p className="text-xs text-brand-cargo-khaki mt-1">Randomized signature</p>
                  </div>
                  <div className="bg-brand-ocean-blue/30 p-3 rounded-lg border border-brand-ocean-blue/50">
                    <code className="text-sm font-semibold text-brand-container-rust">{`{personalization}`}</code>
                    <p className="text-xs text-brand-cargo-khaki mt-1">AI-generated personalization</p>
                  </div>
                  <div className="bg-brand-ocean-blue/30 p-3 rounded-lg border border-brand-ocean-blue/50">
                    <code className="text-sm font-semibold text-brand-container-rust">{`{graceful_exit}`}</code>
                    <p className="text-xs text-brand-cargo-khaki mt-1">Final message exit line</p>
                  </div>
                </div>
              </Card>

              <Card className="p-6 bg-brand-buoy-yellow/20 border-brand-buoy-yellow/40">
                <h3 className="font-semibold mb-3 text-brand-hull-white">💡 Smart Variable Selection</h3>
                <p className="text-sm text-brand-cargo-khaki mb-3">
                  All use case and value prop variables are <strong className="text-brand-hull-white">title-aware</strong> and <strong className="text-brand-hull-white">industry-aware</strong>:
                </p>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 text-brand-deck-green mt-0.5" />
                    <span className="text-brand-cargo-khaki"><strong className="text-brand-hull-white">Company Type Detection:</strong> Automatically identifies if prospect is a carrier, broker, 3PL, etc.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 text-brand-deck-green mt-0.5" />
                    <span className="text-brand-cargo-khaki"><strong className="text-brand-hull-white">Title Matching:</strong> Selects use cases and value props most relevant to their role (e.g., Operations sees appointment scheduling, Sales sees inbound sales)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 text-brand-deck-green mt-0.5" />
                    <span className="text-brand-cargo-khaki"><strong className="text-brand-hull-white">Conversational Formatting:</strong> Uses natural "and" connectors instead of clinical slashes</span>
                  </li>
                </ul>
              </Card>
            </TabsContent>
          </ScrollArea>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

export default DocsModal;
