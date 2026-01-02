import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  User,
  Briefcase,
  Target,
  Mic,
  Palette,
  Plus,
  X,
  Save,
  Loader2,
  Sparkles,
  Trophy,
  MessageSquare,
  Lightbulb,
  TrendingUp,
} from "lucide-react";
import { toast } from "sonner";
import { 
  getBrandProfile, 
  updateBrandProfile, 
  BrandProfile,
  ContentPillar,
  VoiceTone,
  BrandProfileInput,
} from "@/services/brandProfile";

const pillarColors = ["#4F46E5", "#0077b5", "#059669", "#D97706", "#DC2626", "#DB2777", "#7C3AED", "#0891B2"];

const industries = [
  "Technology/SaaS", "Healthcare", "Finance/FinTech", "E-commerce", "Education/EdTech",
  "Marketing/Advertising", "Consulting", "Real Estate", "Manufacturing", "Non-profit", "Other"
];

const writingStyles = [
  { value: "story-driven", label: "Story-driven", desc: "Personal narratives and experiences" },
  { value: "data-focused", label: "Data-focused", desc: "Numbers, research, and evidence" },
  { value: "contrarian", label: "Contrarian", desc: "Challenge conventional wisdom" },
  { value: "educational", label: "Educational", desc: "Teach and explain concepts" },
  { value: "inspirational", label: "Inspirational", desc: "Motivate and uplift" },
];

const primaryGoals = [
  { value: "thought_leadership", label: "Thought Leadership", desc: "Establish expertise" },
  { value: "lead_generation", label: "Lead Generation", desc: "Attract potential customers" },
  { value: "brand_awareness", label: "Brand Awareness", desc: "Increase visibility" },
  { value: "hiring", label: "Hiring/Recruiting", desc: "Attract talent" },
  { value: "networking", label: "Networking", desc: "Build connections" },
];

const postingFrequencies = [
  { value: "daily", label: "Daily" },
  { value: "3x_week", label: "3x per week" },
  { value: "weekly", label: "Weekly" },
  { value: "bi_weekly", label: "Bi-weekly" },
];

const engagementTypes = [
  { value: "comments", label: "Comments" },
  { value: "shares", label: "Shares" },
  { value: "dms", label: "Direct Messages" },
  { value: "profile_views", label: "Profile Views" },
];

interface FormState {
  // Professional Context
  professional_title: string;
  industry: string;
  years_of_experience: number | null;
  company_name: string;
  linkedin_profile_url: string;
  
  // Content Strategy
  content_pillars: ContentPillar[];
  target_audience: string;
  audience_pain_points: string[];
  desired_outcome: string;
  expertise_areas: string[];
  
  // Voice & Personality
  brand_voice: string;
  writing_style: string;
  personality_traits: string[];
  words_to_use: string[];
  words_to_avoid: string[];
  sample_posts: string[];
  voice_tone: VoiceTone;
  
  // Goals & Metrics
  primary_goal: string;
  posting_frequency: string;
  ideal_engagement_type: string;
  
  // Differentiators
  unique_positioning: string;
  unique_story: string;
  unique_perspective: string;
  achievements: string[];
  personal_experiences: string[];
  
  // Visual
  brand_colors: string[];
}

const defaultFormState: FormState = {
  professional_title: "",
  industry: "",
  years_of_experience: null,
  company_name: "",
  linkedin_profile_url: "",
  content_pillars: [],
  target_audience: "",
  audience_pain_points: [],
  desired_outcome: "",
  expertise_areas: [],
  brand_voice: "",
  writing_style: "",
  personality_traits: [],
  words_to_use: [],
  words_to_avoid: [],
  sample_posts: [],
  voice_tone: { formality: 50, humor: 30, emotion: 50, technicality: 50 },
  primary_goal: "",
  posting_frequency: "",
  ideal_engagement_type: "",
  unique_positioning: "",
  unique_story: "",
  unique_perspective: "",
  achievements: [],
  personal_experiences: [],
  brand_colors: [],
};

function TagInput({ 
  value, 
  onChange, 
  placeholder,
  maxTags = 10,
}: { 
  value: string[]; 
  onChange: (value: string[]) => void;
  placeholder: string;
  maxTags?: number;
}) {
  const [inputValue, setInputValue] = useState("");

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && inputValue.trim() && value.length < maxTags) {
      e.preventDefault();
      if (!value.includes(inputValue.trim())) {
        onChange([...value, inputValue.trim()]);
      }
      setInputValue("");
    }
  };

  const removeTag = (index: number) => {
    onChange(value.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2">
        {value.map((tag, index) => (
          <Badge key={index} variant="secondary" className="gap-1 pr-1">
            {tag}
            <button onClick={() => removeTag(index)} className="ml-1 hover:text-destructive">
              <X className="h-3 w-3" />
            </button>
          </Badge>
        ))}
      </div>
      <Input
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={value.length >= maxTags ? "Max tags reached" : placeholder}
        disabled={value.length >= maxTags}
      />
      <p className="text-xs text-muted-foreground">Press Enter to add. {value.length}/{maxTags} tags.</p>
    </div>
  );
}

export default function BrandProfilePage() {
  const [form, setForm] = useState<FormState>(defaultFormState);
  const [newPillar, setNewPillar] = useState({ name: "", description: "", color: pillarColors[0] });
  const [showAddPillar, setShowAddPillar] = useState(false);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['brandProfile'],
    queryFn: getBrandProfile,
    retry: false,
  });

  useEffect(() => {
    if (data) {
      setForm({
        professional_title: data.professional_title || "",
        industry: data.industry || "",
        years_of_experience: data.years_of_experience || null,
        company_name: data.company_name || "",
        linkedin_profile_url: data.linkedin_profile_url || "",
        content_pillars: data.content_pillars || [],
        target_audience: data.target_audience || "",
        audience_pain_points: data.audience_pain_points || [],
        desired_outcome: data.desired_outcome || "",
        expertise_areas: data.expertise_areas || [],
        brand_voice: data.brand_voice || "",
        writing_style: data.writing_style || "",
        personality_traits: data.personality_traits || [],
        words_to_use: data.words_to_use || [],
        words_to_avoid: data.words_to_avoid || [],
        sample_posts: data.sample_posts || [],
        voice_tone: data.voice_tone || defaultFormState.voice_tone,
        primary_goal: data.primary_goal || "",
        posting_frequency: data.posting_frequency || "",
        ideal_engagement_type: data.ideal_engagement_type || "",
        unique_positioning: data.unique_positioning || "",
        unique_story: data.unique_story || "",
        unique_perspective: data.unique_perspective || "",
        achievements: data.achievements || [],
        personal_experiences: data.personal_experiences || [],
        brand_colors: data.brand_colors || [],
      });
    }
  }, [data]);

  const saveMutation = useMutation({
    mutationFn: (data: BrandProfileInput) => updateBrandProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brandProfile'] });
      toast.success("Brand profile saved successfully!");
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to save profile");
    },
  });

  const handleSave = () => {
    saveMutation.mutate({
      ...form,
      years_of_experience: form.years_of_experience || undefined,
    });
  };

  const addPillar = () => {
    if (newPillar.name && form.content_pillars.length < 6) {
      const pillar: ContentPillar = {
        id: crypto.randomUUID(),
        name: newPillar.name,
        description: newPillar.description,
        color: newPillar.color,
      };
      setForm({ ...form, content_pillars: [...form.content_pillars, pillar] });
      setNewPillar({ name: "", description: "", color: pillarColors[(form.content_pillars.length + 1) % pillarColors.length] });
      setShowAddPillar(false);
    }
  };

  const removePillar = (id: string) => {
    setForm({ ...form, content_pillars: form.content_pillars.filter(p => p.id !== id) });
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-96" />
        <Skeleton className="h-[600px] w-full rounded-lg" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-10">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Brand Profile</h1>
          <p className="text-muted-foreground mt-1">Define your personal brand to generate more personalized content</p>
        </div>
        <Button onClick={handleSave} disabled={saveMutation.isPending}>
          {saveMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
          Save Profile
        </Button>
      </div>

      <Tabs defaultValue="professional" className="space-y-6">
        <TabsList className="grid grid-cols-5 lg:w-fit">
          <TabsTrigger value="professional" className="gap-2">
            <Briefcase className="h-4 w-4" />
            <span className="hidden sm:inline">Professional</span>
          </TabsTrigger>
          <TabsTrigger value="content" className="gap-2">
            <Target className="h-4 w-4" />
            <span className="hidden sm:inline">Content</span>
          </TabsTrigger>
          <TabsTrigger value="voice" className="gap-2">
            <Mic className="h-4 w-4" />
            <span className="hidden sm:inline">Voice</span>
          </TabsTrigger>
          <TabsTrigger value="goals" className="gap-2">
            <TrendingUp className="h-4 w-4" />
            <span className="hidden sm:inline">Goals</span>
          </TabsTrigger>
          <TabsTrigger value="differentiators" className="gap-2">
            <Sparkles className="h-4 w-4" />
            <span className="hidden sm:inline">Unique</span>
          </TabsTrigger>
        </TabsList>

        {/* Professional Context Tab */}
        <TabsContent value="professional">
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Briefcase className="h-5 w-5" />
                  Professional Context
                </CardTitle>
                <CardDescription>Tell us about your professional background</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Professional Title</Label>
                    <Input 
                      placeholder="e.g., Founder & CEO, Marketing Director"
                      value={form.professional_title}
                      onChange={(e) => setForm({ ...form, professional_title: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Company Name</Label>
                    <Input 
                      placeholder="Your company or organization"
                      value={form.company_name}
                      onChange={(e) => setForm({ ...form, company_name: e.target.value })}
                    />
                  </div>
                </div>
                
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Industry</Label>
                    <Select value={form.industry} onValueChange={(v) => setForm({ ...form, industry: v })}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select your industry" />
                      </SelectTrigger>
                      <SelectContent>
                        {industries.map((industry) => (
                          <SelectItem key={industry} value={industry}>{industry}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Years of Experience</Label>
                    <Input 
                      type="number"
                      min={0}
                      max={50}
                      placeholder="e.g., 10"
                      value={form.years_of_experience || ""}
                      onChange={(e) => setForm({ ...form, years_of_experience: e.target.value ? parseInt(e.target.value) : null })}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>LinkedIn Profile URL</Label>
                  <Input 
                    placeholder="https://linkedin.com/in/yourprofile"
                    value={form.linkedin_profile_url}
                    onChange={(e) => setForm({ ...form, linkedin_profile_url: e.target.value })}
                  />
                  <p className="text-xs text-muted-foreground">Optional: We can analyze your profile for style insights</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        {/* Content Strategy Tab */}
        <TabsContent value="content">
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
            {/* Content Pillars */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  Content Pillars
                </CardTitle>
                <CardDescription>The main topics you post about (max 6)</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {form.content_pillars.map((pillar) => (
                    <div
                      key={pillar.id}
                      className="p-3 rounded-lg border group relative"
                      style={{ borderLeftWidth: 4, borderLeftColor: pillar.color }}
                    >
                      <button 
                        onClick={() => removePillar(pillar.id)}
                        className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <X className="h-4 w-4 text-muted-foreground hover:text-destructive" />
                      </button>
                      <p className="font-medium text-sm">{pillar.name}</p>
                      <p className="text-xs text-muted-foreground mt-1">{pillar.description}</p>
                    </div>
                  ))}
                  
                  {form.content_pillars.length < 6 && (
                    showAddPillar ? (
                      <div className="p-3 rounded-lg border border-dashed space-y-2">
                        <Input 
                          placeholder="Pillar name"
                          value={newPillar.name}
                          onChange={(e) => setNewPillar({ ...newPillar, name: e.target.value })}
                          className="h-8"
                        />
                        <Input 
                          placeholder="Brief description"
                          value={newPillar.description}
                          onChange={(e) => setNewPillar({ ...newPillar, description: e.target.value })}
                          className="h-8"
                        />
                        <div className="flex gap-2">
                          {pillarColors.map((color) => (
                            <button
                              key={color}
                              className={`h-5 w-5 rounded-full ${newPillar.color === color ? 'ring-2 ring-offset-2' : ''}`}
                              style={{ backgroundColor: color }}
                              onClick={() => setNewPillar({ ...newPillar, color })}
                            />
                          ))}
                        </div>
                        <div className="flex gap-2 pt-1">
                          <Button size="sm" className="h-7" onClick={addPillar}>Add</Button>
                          <Button size="sm" variant="ghost" className="h-7" onClick={() => setShowAddPillar(false)}>Cancel</Button>
                        </div>
                      </div>
                    ) : (
                      <button
                        onClick={() => setShowAddPillar(true)}
                        className="p-3 rounded-lg border border-dashed flex items-center justify-center gap-2 text-muted-foreground hover:text-foreground hover:border-foreground transition-colors"
                      >
                        <Plus className="h-4 w-4" />
                        Add Pillar
                      </button>
                    )
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Target Audience & Pain Points */}
            <Card>
              <CardHeader>
                <CardTitle>Target Audience</CardTitle>
                <CardDescription>Who are you trying to reach?</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Target Audience Description</Label>
                  <Textarea 
                    placeholder="e.g., B2B SaaS founders, early-stage startup CEOs, marketing leaders at tech companies"
                    value={form.target_audience}
                    onChange={(e) => setForm({ ...form, target_audience: e.target.value })}
                    rows={3}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label>Audience Pain Points</Label>
                  <TagInput 
                    value={form.audience_pain_points}
                    onChange={(v) => setForm({ ...form, audience_pain_points: v })}
                    placeholder="e.g., scaling, hiring, fundraising"
                    maxTags={8}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Desired Outcome</Label>
                  <Textarea 
                    placeholder="What action do you want readers to take? e.g., Visit my website, Book a call, Try my product"
                    value={form.desired_outcome}
                    onChange={(e) => setForm({ ...form, desired_outcome: e.target.value })}
                    rows={2}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Your Expertise Areas</Label>
                  <TagInput 
                    value={form.expertise_areas}
                    onChange={(v) => setForm({ ...form, expertise_areas: v })}
                    placeholder="e.g., growth hacking, product management, AI"
                    maxTags={10}
                  />
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        {/* Voice & Personality Tab */}
        <TabsContent value="voice">
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Mic className="h-5 w-5" />
                  Writing Style & Voice
                </CardTitle>
                <CardDescription>How should your content sound?</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label>Brand Voice Description</Label>
                  <Textarea 
                    placeholder="Describe your writing voice, e.g., Conversational yet professional, data-driven but accessible, witty and insightful"
                    value={form.brand_voice}
                    onChange={(e) => setForm({ ...form, brand_voice: e.target.value })}
                    rows={3}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Primary Writing Style</Label>
                  <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {writingStyles.map((style) => (
                      <button
                        key={style.value}
                        onClick={() => setForm({ ...form, writing_style: style.value })}
                        className={`p-3 rounded-lg border text-left transition-all ${
                          form.writing_style === style.value 
                            ? 'border-primary bg-primary/5 ring-1 ring-primary' 
                            : 'hover:border-primary/50'
                        }`}
                      >
                        <p className="font-medium text-sm">{style.label}</p>
                        <p className="text-xs text-muted-foreground">{style.desc}</p>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Personality Traits</Label>
                  <TagInput 
                    value={form.personality_traits}
                    onChange={(v) => setForm({ ...form, personality_traits: v })}
                    placeholder="e.g., witty, empathetic, direct, curious"
                    maxTags={6}
                  />
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label>Words/Phrases to Use</Label>
                    <TagInput 
                      value={form.words_to_use}
                      onChange={(v) => setForm({ ...form, words_to_use: v })}
                      placeholder="e.g., Here's the truth, Let me share"
                      maxTags={10}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Words/Phrases to Avoid</Label>
                    <TagInput 
                      value={form.words_to_avoid}
                      onChange={(v) => setForm({ ...form, words_to_avoid: v })}
                      placeholder="e.g., synergy, leverage, guru"
                      maxTags={10}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Voice Tone Sliders */}
            <Card>
              <CardHeader>
                <CardTitle>Voice Tone Settings</CardTitle>
                <CardDescription>Fine-tune your content personality</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {[
                  { key: 'formality' as const, label: 'Formality', left: 'Casual', right: 'Formal' },
                  { key: 'humor' as const, label: 'Humor', left: 'Serious', right: 'Playful' },
                  { key: 'emotion' as const, label: 'Emotion', left: 'Analytical', right: 'Emotional' },
                  { key: 'technicality' as const, label: 'Technicality', left: 'Simple', right: 'Technical' },
                ].map((item) => (
                  <div key={item.key} className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">{item.left}</span>
                      <span className="font-medium">{item.label}</span>
                      <span className="text-muted-foreground">{item.right}</span>
                    </div>
                    <Slider
                      value={[form.voice_tone[item.key]]}
                      onValueChange={([value]) => setForm({ 
                        ...form, 
                        voice_tone: { ...form.voice_tone, [item.key]: value } 
                      })}
                      max={100}
                      step={1}
                    />
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        {/* Goals Tab */}
        <TabsContent value="goals">
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Goals & Metrics
                </CardTitle>
                <CardDescription>What do you want to achieve with your LinkedIn presence?</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label>Primary Goal</Label>
                  <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {primaryGoals.map((goal) => (
                      <button
                        key={goal.value}
                        onClick={() => setForm({ ...form, primary_goal: goal.value })}
                        className={`p-3 rounded-lg border text-left transition-all ${
                          form.primary_goal === goal.value 
                            ? 'border-primary bg-primary/5 ring-1 ring-primary' 
                            : 'hover:border-primary/50'
                        }`}
                      >
                        <p className="font-medium text-sm">{goal.label}</p>
                        <p className="text-xs text-muted-foreground">{goal.desc}</p>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Posting Frequency</Label>
                    <Select value={form.posting_frequency} onValueChange={(v) => setForm({ ...form, posting_frequency: v })}>
                      <SelectTrigger>
                        <SelectValue placeholder="How often do you post?" />
                      </SelectTrigger>
                      <SelectContent>
                        {postingFrequencies.map((freq) => (
                          <SelectItem key={freq.value} value={freq.value}>{freq.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Ideal Engagement Type</Label>
                    <Select value={form.ideal_engagement_type} onValueChange={(v) => setForm({ ...form, ideal_engagement_type: v })}>
                      <SelectTrigger>
                        <SelectValue placeholder="What engagement matters most?" />
                      </SelectTrigger>
                      <SelectContent>
                        {engagementTypes.map((type) => (
                          <SelectItem key={type.value} value={type.value}>{type.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        {/* Differentiators Tab */}
        <TabsContent value="differentiators">
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="h-5 w-5" />
                  Your Unique Positioning
                </CardTitle>
                <CardDescription>What makes you different from others in your space?</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Unique Positioning Statement</Label>
                  <Textarea 
                    placeholder="I help [target audience] achieve [outcome] through [unique approach]"
                    value={form.unique_positioning}
                    onChange={(e) => setForm({ ...form, unique_positioning: e.target.value })}
                    rows={2}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Unique Perspective</Label>
                  <Textarea 
                    placeholder="What contrarian or unique viewpoints do you hold in your industry?"
                    value={form.unique_perspective}
                    onChange={(e) => setForm({ ...form, unique_perspective: e.target.value })}
                    rows={3}
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5" />
                  Your Story
                </CardTitle>
                <CardDescription>Share your journey and background</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Your Origin Story</Label>
                  <Textarea 
                    placeholder="How did you get to where you are today? Share your journey, pivotal moments, and lessons learned..."
                    value={form.unique_story}
                    onChange={(e) => setForm({ ...form, unique_story: e.target.value })}
                    rows={4}
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Trophy className="h-5 w-5" />
                  Achievements & Experiences
                </CardTitle>
                <CardDescription>Accomplishments and stories to reference in content</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Key Achievements</Label>
                  <TagInput 
                    value={form.achievements}
                    onChange={(v) => setForm({ ...form, achievements: v })}
                    placeholder="e.g., Grew startup to $1M ARR, Built 10k newsletter"
                    maxTags={10}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Personal Experiences (Story Hooks)</Label>
                  <TagInput 
                    value={form.personal_experiences}
                    onChange={(v) => setForm({ ...form, personal_experiences: v })}
                    placeholder="e.g., Failed first startup, Bootstrapped to acquisition"
                    maxTags={10}
                  />
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>
      </Tabs>

      {/* Floating Save Button */}
      <div className="fixed bottom-6 right-6 z-50">
        <Button size="lg" onClick={handleSave} disabled={saveMutation.isPending} className="shadow-lg">
          {saveMutation.isPending ? <Loader2 className="mr-2 h-5 w-5 animate-spin" /> : <Save className="mr-2 h-5 w-5" />}
          Save Profile
        </Button>
      </div>
    </div>
  );
}
