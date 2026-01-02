import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  ArrowRight, 
  Sparkles, 
  Brain, 
  Zap, 
  Target, 
  BarChart3, 
  Palette,
  MessageSquare,
  Check,
  Star,
} from "lucide-react";
import { Link } from "react-router-dom";
import { ThemeToggle } from "@/components/ThemeToggle";
import { useAuthStore } from "@/stores/authStore";

const features = [
  { icon: Brain, title: "5 AI Agents", description: "Validator, Strategist, Writer, Optimizer, and Quality Checker work together." },
  { icon: Zap, title: "60-Second Generation", description: "From idea to polished post in under a minute." },
  { icon: Target, title: "Brand Voice Match", description: "AI learns your unique voice and maintains consistency." },
  { icon: Palette, title: "Multi-Format Support", description: "Text posts, carousels, and video scripts." },
  { icon: BarChart3, title: "Performance Predictions", description: "AI predicts engagement before you post." },
  { icon: MessageSquare, title: "Hook Variations", description: "Get 3 unique hook options for every post." },
];

const steps = [
  { step: 1, title: "Enter Your Idea", description: "Share your rough idea, story, or topic." },
  { step: 2, title: "Answer Quick Questions", description: "Our AI asks 2-3 clarifying questions." },
  { step: 3, title: "Get Viral Content", description: "Receive polished posts with hook options." },
];

const testimonials = [
  { name: "Sarah Chen", role: "Founder & CEO", quote: "GhostWriter AI transformed my LinkedIn presence. I went from 100 to 10,000 impressions per post." },
  { name: "Marcus Johnson", role: "Content Creator", quote: "The hook variations are incredible. Every post feels fresh and engaging." },
  { name: "Elena Rodriguez", role: "Marketing Director", quote: "We use GhostWriter AI for our entire team. The brand voice consistency is unmatched." },
];

export default function LandingPage() {
  const { isAuthenticated } = useAuthStore();

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-background/95 backdrop-blur-sm border-b border-border">
        <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <span className="font-semibold text-lg">GhostWriter AI</span>
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Features</a>
            <a href="#how-it-works" className="text-sm text-muted-foreground hover:text-foreground transition-colors">How it Works</a>
            <a href="#pricing" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Pricing</a>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle variant="icon" />
            {isAuthenticated ? (
              <Button size="sm" asChild>
                <Link to="/app/dashboard">Dashboard</Link>
              </Button>
            ) : (
              <>
                <Button variant="ghost" size="sm" asChild>
                  <Link to="/login">Log In</Link>
                </Button>
                <Button size="sm" asChild>
                  <Link to="/signup">Get Started</Link>
                </Button>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <Badge variant="secondary" className="mb-6">
            <Sparkles className="h-3 w-3 mr-1" />
            Powered by 5 AI Agents
          </Badge>
          
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
            Transform Ideas into{' '}
            <span className="text-primary">Viral LinkedIn Posts</span>
          </h1>
          
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            5 AI agents work together to craft scroll-stopping content 
            that sounds like you, performs like the top 1%.
          </p>
          
          <div className="flex flex-wrap justify-center gap-4 mb-12">
            <Button size="lg" asChild>
              <Link to="/signup">
                Start Free <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button variant="outline" size="lg">
              Watch Demo
            </Button>
          </div>
          
          {/* Social proof */}
          <div className="flex items-center justify-center gap-4 text-sm text-muted-foreground">
            <div className="flex -space-x-2">
              {[1,2,3,4,5].map((i) => (
                <div key={i} className="h-8 w-8 rounded-full bg-primary/20 border-2 border-background" />
              ))}
            </div>
            <span>Trusted by <strong className="text-foreground">10,000+</strong> creators</span>
          </div>
        </div>
      </section>

      {/* Stats Bar */}
      <section className="py-12 border-y border-border bg-muted/30">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[
              { value: "50K+", label: "Posts Generated" },
              { value: "10M+", label: "Total Impressions" },
              { value: "4.8%", label: "Avg Engagement Rate" },
              { value: "10K+", label: "Active Users" },
            ].map((stat) => (
              <div key={stat.label}>
                <p className="text-2xl sm:text-3xl font-bold">{stat.value}</p>
                <p className="text-sm text-muted-foreground mt-1">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <Badge variant="secondary" className="mb-4">Features</Badge>
            <h2 className="text-3xl font-bold mb-4">Everything You Need to Go Viral</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Our AI agents work together to create content that captures attention and drives engagement.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature) => (
              <Card key={feature.title}>
                <CardContent className="p-6">
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                    <feature.icon className="h-5 w-5 text-primary" />
                  </div>
                  <h3 className="font-semibold mb-2">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 px-6 bg-muted/30">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <Badge variant="secondary" className="mb-4">How It Works</Badge>
            <h2 className="text-3xl font-bold mb-4">3 Simple Steps to Viral Content</h2>
            <p className="text-muted-foreground">Our streamlined process makes content creation effortless.</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {steps.map((item) => (
              <div key={item.step} className="relative">
                <div className="text-6xl font-bold text-primary/10 absolute -top-4 -left-2">
                  {item.step}
                </div>
                <Card className="relative mt-6">
                  <CardContent className="p-6">
                    <h3 className="font-semibold mb-2">{item.title}</h3>
                    <p className="text-sm text-muted-foreground">{item.description}</p>
                  </CardContent>
                </Card>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <Badge variant="secondary" className="mb-4">Pricing</Badge>
            <h2 className="text-3xl font-bold mb-4">Simple, Transparent Pricing</h2>
            <p className="text-muted-foreground">Start free, upgrade when you're ready.</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Free */}
            <Card>
              <CardContent className="p-6">
                <h3 className="font-semibold text-lg">Free</h3>
                <div className="mt-4 mb-6">
                  <span className="text-3xl font-bold">$0</span>
                  <span className="text-muted-foreground">/month</span>
                </div>
                <ul className="space-y-3 mb-6">
                  {["5 posts per month", "Basic hooks", "Text format only", "Community support"].map((f) => (
                    <li key={f} className="flex items-center gap-2 text-sm">
                      <Check className="h-4 w-4 text-success" />
                      {f}
                    </li>
                  ))}
                </ul>
                <Button variant="outline" className="w-full">Get Started</Button>
              </CardContent>
            </Card>

            {/* Pro */}
            <Card className="border-primary relative">
              <Badge className="absolute -top-3 left-1/2 -translate-x-1/2">Most Popular</Badge>
              <CardContent className="p-6">
                <h3 className="font-semibold text-lg">Pro</h3>
                <div className="mt-4 mb-6">
                  <span className="text-3xl font-bold">$29</span>
                  <span className="text-muted-foreground">/month</span>
                </div>
                <ul className="space-y-3 mb-6">
                  {["Unlimited posts", "All hook variations", "All formats", "Performance predictions", "Priority support", "Brand voice training"].map((f) => (
                    <li key={f} className="flex items-center gap-2 text-sm">
                      <Check className="h-4 w-4 text-success" />
                      {f}
                    </li>
                  ))}
                </ul>
                <Button className="w-full">Start Free Trial</Button>
              </CardContent>
            </Card>

            {/* Enterprise */}
            <Card>
              <CardContent className="p-6">
                <h3 className="font-semibold text-lg">Enterprise</h3>
                <div className="mt-4 mb-6">
                  <span className="text-3xl font-bold">Custom</span>
                </div>
                <ul className="space-y-3 mb-6">
                  {["Everything in Pro", "Team collaboration", "API access", "Custom integrations", "Dedicated support", "SLA guarantee"].map((f) => (
                    <li key={f} className="flex items-center gap-2 text-sm">
                      <Check className="h-4 w-4 text-success" />
                      {f}
                    </li>
                  ))}
                </ul>
                <Button variant="outline" className="w-full">Contact Sales</Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 px-6 bg-muted/30">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <Badge variant="secondary" className="mb-4">Testimonials</Badge>
            <h2 className="text-3xl font-bold mb-4">Loved by Content Creators</h2>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6">
            {testimonials.map((t) => (
              <Card key={t.name}>
                <CardContent className="p-6">
                  <div className="flex items-center gap-1 mb-4">
                    {[1,2,3,4,5].map((star) => (
                      <Star key={star} className="h-4 w-4 fill-warning text-warning" />
                    ))}
                  </div>
                  <p className="text-sm mb-4">"{t.quote}"</p>
                  <div className="flex items-center gap-3">
                    <div className="h-9 w-9 rounded-full bg-primary/20 flex items-center justify-center text-xs font-medium">
                      {t.name.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div>
                      <p className="text-sm font-medium">{t.name}</p>
                      <p className="text-xs text-muted-foreground">{t.role}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Create Viral Content?</h2>
          <p className="text-muted-foreground mb-8">
            Join 10,000+ creators who are already using GhostWriter AI to grow their LinkedIn presence.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Button size="lg" asChild>
              <Link to="/signup">
                Get Started Free <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-border bg-muted/10">
        <div className="max-w-6xl mx-auto flex flex-col items-center justify-center gap-4 text-center px-6">
            <span className="font-semibold text-lg">GhostWriter AI</span>
            <div className="space-y-1">
                <p className="text-sm text-muted-foreground">© 2026 GhostWriter AI. All rights reserved.</p>
                <p className="text-xs text-muted-foreground/60">Created by Partha Saradhi 2026</p>
            </div>
        </div>
      </footer>
    </div>
  );
}
