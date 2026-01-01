import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import {
  User,
  Briefcase,
  Target,
  Mic,
  Palette,
  Plus,
  X,
  GripVertical,
  Save,
  Edit,
  Camera,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { toast } from "sonner";
import { 
  getBrandProfile, 
  updateBrandProfile, 
  addContentPillar,
  removeContentPillar,
  BrandProfile,
  ContentPillar,
  VoiceTone,
} from "@/services/brandProfile";
import { useAuthStore } from "@/stores/authStore";

const pillarColors = ["#4F46E5", "#0077b5", "#059669", "#D97706", "#DC2626", "#DB2777"];

const defaultProfile = {
  name: "Your Name",
  title: "",
  bio: "",
  content_pillars: [] as ContentPillar[],
  target_audience: "",
  voice_tone: {
    formality: 50,
    humor: 50,
    emotion: 50,
    technicality: 50,
  } as VoiceTone,
  brand_colors: [] as string[],
};

export default function BrandProfilePage() {
  const [isEditing, setIsEditing] = useState(false);
  const [profile, setProfile] = useState(defaultProfile);
  const [newPillar, setNewPillar] = useState({ name: "", description: "", color: pillarColors[0] });
  const [showAddPillar, setShowAddPillar] = useState(false);
  const queryClient = useQueryClient();
  const { user } = useAuthStore();

  // Fetch brand profile
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['brandProfile'],
    queryFn: getBrandProfile,
    retry: false,
  });

  // Update profile when data loads
  useEffect(() => {
    if (data) {
      setProfile({
        name: data.name || user?.name || "Your Name",
        title: data.title || "",
        bio: data.bio || "",
        content_pillars: data.content_pillars || [],
        target_audience: data.target_audience || "",
        voice_tone: data.voice_tone || defaultProfile.voice_tone,
        brand_colors: data.brand_colors || [],
      });
    } else if (user) {
      setProfile(prev => ({ ...prev, name: user.name }));
    }
  }, [data, user]);

  // Save mutation
  const saveMutation = useMutation({
    mutationFn: updateBrandProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brandProfile'] });
      setIsEditing(false);
      toast.success("Brand profile saved successfully!");
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to save profile");
    },
  });

  const handleSave = () => {
    saveMutation.mutate({
      name: profile.name,
      title: profile.title,
      bio: profile.bio,
      content_pillars: profile.content_pillars,
      target_audience: profile.target_audience,
      voice_tone: profile.voice_tone,
      brand_colors: profile.brand_colors,
    });
  };

  const addPillar = () => {
    if (!newPillar.name.trim()) {
      toast.error("Please enter a pillar name");
      return;
    }
    const pillar: ContentPillar = {
      id: Date.now().toString(),
      name: newPillar.name,
      description: newPillar.description,
      color: newPillar.color,
    };
    setProfile({
      ...profile,
      content_pillars: [...profile.content_pillars, pillar],
    });
    setNewPillar({ name: "", description: "", color: pillarColors[0] });
    setShowAddPillar(false);
    toast.success("Content pillar added!");
  };

  const removePillar = (id: string) => {
    setProfile({
      ...profile,
      content_pillars: profile.content_pillars.filter((p) => p.id !== id),
    });
    toast.success("Content pillar removed");
  };

  const updateVoiceTone = (key: keyof VoiceTone, value: number[]) => {
    setProfile({
      ...profile,
      voice_tone: { ...profile.voice_tone, [key]: value[0] },
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Brand Profile</h1>
          <p className="text-muted-foreground mt-1">Define your brand voice and content strategy</p>
        </div>
        {isEditing ? (
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setIsEditing(false)}>Cancel</Button>
            <Button onClick={handleSave}>
              <Save className="mr-2 h-4 w-4" /> Save Changes
            </Button>
          </div>
        ) : (
          <Button variant="outline" onClick={() => setIsEditing(true)}>
            <Edit className="mr-2 h-4 w-4" /> Edit Profile
          </Button>
        )}
      </div>

      {/* Profile Header */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-start gap-6">
              <div className="relative group">
                <div className="h-20 w-20 rounded-xl bg-primary flex items-center justify-center text-2xl font-bold text-primary-foreground">
                  {profile.name.charAt(0)}
                </div>
                {isEditing && (
                  <button className="absolute inset-0 bg-black/50 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white">
                    <Camera className="h-5 w-5" />
                  </button>
                )}
              </div>
              <div className="flex-1 space-y-3">
                {isEditing ? (
                  <>
                    <Input value={profile.name} onChange={(e) => setProfile({ ...profile, name: e.target.value })} placeholder="Your Name" className="text-lg font-semibold" />
                    <Input value={profile.title} onChange={(e) => setProfile({ ...profile, title: e.target.value })} placeholder="Your Title" />
                  </>
                ) : (
                  <>
                    <h2 className="text-xl font-semibold">{profile.name}</h2>
                    <p className="text-muted-foreground">{profile.title}</p>
                  </>
                )}
              </div>
            </div>
            <div className="mt-6">
              <Label className="text-sm text-muted-foreground mb-2 flex items-center gap-2">
                <User className="h-4 w-4" /> Bio
              </Label>
              {isEditing ? (
                <Textarea value={profile.bio} onChange={(e) => setProfile({ ...profile, bio: e.target.value })} placeholder="Tell us about yourself..." className="min-h-[100px] mt-2" />
              ) : (
                <p className="text-foreground mt-2">{profile.bio}</p>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Content Pillars */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Palette className="h-5 w-5 text-muted-foreground" />
                <h3 className="text-lg font-semibold">Content Pillars</h3>
              </div>
              {isEditing && (
                <Button variant="outline" size="sm" onClick={() => setShowAddPillar(true)}>
                  <Plus className="mr-2 h-4 w-4" /> Add Pillar
                </Button>
              )}
            </div>
            <p className="text-muted-foreground text-sm mb-4">Define the main topics you consistently create content about.</p>
            <div className="space-y-3">
              {profile.content_pillars.map((pillar, index) => (
                <motion.div key={pillar.id} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.03 }} className="flex items-center gap-3 p-4 rounded-lg bg-muted/50 group">
                  {isEditing && <GripVertical className="h-4 w-4 text-muted-foreground cursor-grab" />}
                  <div className="h-4 w-4 rounded-full flex-shrink-0" style={{ backgroundColor: pillar.color }} />
                  <div className="flex-1">
                    <h4 className="font-medium">{pillar.name}</h4>
                    <p className="text-sm text-muted-foreground">{pillar.description}</p>
                  </div>
                  {isEditing && (
                    <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100 transition-opacity" onClick={() => removePillar(pillar.id)}>
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </motion.div>
              ))}
            </div>
            {showAddPillar && (
              <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} className="mt-4 p-4 rounded-lg border border-border space-y-3">
                <Input placeholder="Pillar name (e.g., Product Strategy)" value={newPillar.name} onChange={(e) => setNewPillar({ ...newPillar, name: e.target.value })} />
                <Input placeholder="Description" value={newPillar.description} onChange={(e) => setNewPillar({ ...newPillar, description: e.target.value })} />
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">Color:</span>
                  {pillarColors.map((color) => (
                    <button key={color} className={`h-6 w-6 rounded-full transition-transform ${newPillar.color === color ? "ring-2 ring-offset-2 ring-primary scale-110" : ""}`} style={{ backgroundColor: color }} onClick={() => setNewPillar({ ...newPillar, color })} />
                  ))}
                </div>
                <div className="flex gap-2">
                  <Button size="sm" onClick={addPillar}>Add Pillar</Button>
                  <Button size="sm" variant="ghost" onClick={() => setShowAddPillar(false)}>Cancel</Button>
                </div>
              </motion.div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Target Audience */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <Target className="h-5 w-5 text-muted-foreground" />
              <h3 className="text-lg font-semibold">Target Audience</h3>
            </div>
            <p className="text-muted-foreground text-sm mb-4">Describe who you're creating content for.</p>
            {isEditing ? (
              <Textarea value={profile.target_audience} onChange={(e) => setProfile({ ...profile, target_audience: e.target.value })} placeholder="Describe your ideal audience..." className="min-h-[100px]" />
            ) : (
              <p className="text-foreground">{profile.target_audience}</p>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Voice Settings */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <Mic className="h-5 w-5 text-muted-foreground" />
              <h3 className="text-lg font-semibold">Brand Voice</h3>
            </div>
            <p className="text-muted-foreground text-sm mb-6">Adjust these sliders to define your unique writing style.</p>
            <div className="space-y-8">
              {[
                { key: "formality", left: "Casual", right: "Professional" },
                { key: "humor", left: "Serious", right: "Playful" },
                { key: "emotion", left: "Analytical", right: "Empathetic" },
                { key: "technicality", left: "Simple", right: "Technical" },
              ].map(({ key, left, right }) => (
                <div key={key} className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">{left}</span>
                    <span className="font-medium capitalize">{key}</span>
                    <span className="text-muted-foreground">{right}</span>
                  </div>
                  <Slider value={[profile.voice_tone[key as keyof typeof profile.voice_tone]]} onValueChange={(v) => updateVoiceTone(key as keyof typeof profile.voice_tone, v)} max={100} step={1} disabled={!isEditing} />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Sample Posts */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Briefcase className="h-5 w-5 text-muted-foreground" />
                <h3 className="text-lg font-semibold">Sample Posts</h3>
              </div>
              {isEditing && (
                <Button variant="outline" size="sm">
                  <Plus className="mr-2 h-4 w-4" /> Add Sample
                </Button>
              )}
            </div>
            <p className="text-muted-foreground text-sm mb-4">Add examples of your best-performing posts to help AI learn your style.</p>
            <div className="text-center py-8">
              <div className="h-12 w-12 mx-auto rounded-xl bg-muted flex items-center justify-center mb-4">
                <Briefcase className="h-6 w-6 text-muted-foreground" />
              </div>
              <p className="text-muted-foreground mb-4">No sample posts added yet</p>
              {isEditing && (
                <Button variant="outline">
                  <Plus className="mr-2 h-4 w-4" /> Add Your First Sample
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
