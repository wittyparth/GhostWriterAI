# LinkedIn AI Agent - Premium Frontend Blueprint

## 🎯 Executive Summary

This document provides a comprehensive, production-grade frontend specification for the LinkedIn AI Agent platform. The design aims for a **$100K+ enterprise-level application** with stunning UI/UX, smooth animations, and a premium feel that rivals tools like Jasper, Copy.ai, and Notion.

---

## 🏗️ Architecture Overview

### Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Framework** | React 18+ | Component-based UI |
| **Routing** | React Router v6 | Client-side routing |
| **Styling** | Tailwind CSS + Shadcn/UI | Utility-first + Premium components |
| **Animations** | Framer Motion | Smooth micro-interactions |
| **State** | Zustand + TanStack Query | Client + Server state |
| **Forms** | React Hook Form + Zod | Form handling + Validation |
| **Icons** | Lucide Icons | Modern icon set |
| **Auth** | Clerk or NextAuth | Authentication |
| **API** | Axios + TanStack Query | Data fetching + Caching |

### Design Philosophy

```
+------------------------------------------------------------------+
|                    DESIGN PRINCIPLES                              |
+------------------------------------------------------------------+
| 1. DARK MODE FIRST - Rich dark theme with vibrant accents        |
| 2. GLASSMORPHISM - Frosted glass effects for depth               |
| 3. MICRO-ANIMATIONS - Subtle motion for premium feel             |
| 4. WHITESPACE - Generous spacing for elegance                    |
| 5. HIERARCHY - Clear visual hierarchy with typography            |
| 6. FEEDBACK - Instant visual feedback on all interactions        |
+------------------------------------------------------------------+
```

---

## 🎨 Design System

### Color Palette

```javascript
// tailwind.config.js
const colors = {
  // Primary - LinkedIn Blue gradient
  primary: {
    50: '#e6f2ff',
    100: '#b3d9ff',
    200: '#80bfff',
    300: '#4da6ff',
    400: '#1a8cff',
    500: '#0077b5', // LinkedIn Blue
    600: '#005a8c',
    700: '#003d5c',
    800: '#002033',
    900: '#00141f',
  },
  
  // Accent - Vibrant Purple/Violet
  accent: {
    400: '#a855f7',
    500: '#8b5cf6',
    600: '#7c3aed',
  },
  
  // Success - Emerald
  success: {
    400: '#34d399',
    500: '#10b981',
    600: '#059669',
  },
  
  // Background - Deep Dark
  background: {
    primary: '#0a0a0f',      // Main background
    secondary: '#111118',    // Cards/Panels
    tertiary: '#1a1a24',     // Elevated elements
    glass: 'rgba(17, 17, 24, 0.8)', // Glassmorphism
  },
  
  // Text
  text: {
    primary: '#ffffff',
    secondary: '#a1a1aa',
    muted: '#71717a',
  },
  
  // Borders
  border: {
    default: 'rgba(255, 255, 255, 0.08)',
    hover: 'rgba(255, 255, 255, 0.15)',
    active: 'rgba(139, 92, 246, 0.5)',
  }
}
```

### Typography

```javascript
// Google Fonts: Inter + Space Grotesk
const typography = {
  fontFamily: {
    sans: ['Inter', 'system-ui', 'sans-serif'],
    display: ['Space Grotesk', 'Inter', 'sans-serif'],
    mono: ['JetBrains Mono', 'monospace'],
  },
  fontSize: {
    'display-xl': ['4.5rem', { lineHeight: '1.1', letterSpacing: '-0.03em' }],
    'display-lg': ['3.5rem', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
    'heading-1': ['2.5rem', { lineHeight: '1.2', letterSpacing: '-0.02em' }],
    'heading-2': ['2rem', { lineHeight: '1.3', letterSpacing: '-0.01em' }],
    'heading-3': ['1.5rem', { lineHeight: '1.4' }],
    'body-lg': ['1.125rem', { lineHeight: '1.6' }],
    'body': ['1rem', { lineHeight: '1.6' }],
    'caption': ['0.875rem', { lineHeight: '1.5' }],
  }
}
```

### Shadows & Effects

```css
/* Premium shadow system */
.shadow-glow-sm { box-shadow: 0 0 20px rgba(139, 92, 246, 0.15); }
.shadow-glow-md { box-shadow: 0 0 40px rgba(139, 92, 246, 0.2); }
.shadow-glow-lg { box-shadow: 0 0 60px rgba(139, 92, 246, 0.25); }

/* Glassmorphism */
.glass {
  background: rgba(17, 17, 24, 0.7);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

/* Gradient borders */
.gradient-border {
  border: 1px solid transparent;
  background: linear-gradient(#111118, #111118) padding-box,
              linear-gradient(135deg, #8b5cf6, #0077b5) border-box;
}
```

---

## 📁 Project Structure

```
src/
├── app/
│   ├── providers.tsx           # All context providers
│   └── router.tsx              # Route configuration
│
├── assets/
│   ├── fonts/                  # Custom fonts
│   ├── images/                 # Static images
│   └── icons/                  # Custom SVG icons
│
├── components/
│   ├── ui/                     # Shadcn UI components (extended)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   ├── dialog.tsx
│   │   └── ...
│   │
│   ├── layout/                 # Layout components
│   │   ├── Sidebar.tsx
│   │   ├── TopNavbar.tsx
│   │   ├── Footer.tsx
│   │   └── MainLayout.tsx
│   │
│   ├── features/               # Feature-specific components
│   │   ├── post-generator/
│   │   │   ├── IdeaInput.tsx
│   │   │   ├── QuestionFlow.tsx
│   │   │   ├── PostPreview.tsx
│   │   │   ├── HookSelector.tsx
│   │   │   └── GenerationProgress.tsx
│   │   │
│   │   ├── dashboard/
│   │   │   ├── StatsCards.tsx
│   │   │   ├── RecentPosts.tsx
│   │   │   ├── PerformanceChart.tsx
│   │   │   └── QuickActions.tsx
│   │   │
│   │   └── brand-profile/
│   │       ├── ProfileEditor.tsx
│   │       ├── PillarManager.tsx
│   │       └── VoiceSettings.tsx
│   │
│   └── shared/                 # Shared/common components
│       ├── Logo.tsx
│       ├── LoadingSpinner.tsx
│       ├── AnimatedCounter.tsx
│       └── Tooltip.tsx
│
├── hooks/                      # Custom React hooks
│   ├── useAuth.ts
│   ├── useApi.ts
│   ├── useToast.ts
│   ├── useLocalStorage.ts
│   └── useMediaQuery.ts
│
├── lib/                        # Utilities and configs
│   ├── api.ts                  # Axios instance
│   ├── utils.ts                # Helper functions
│   ├── constants.ts            # App constants
│   └── validations.ts          # Zod schemas
│
├── pages/                      # Page components
│   ├── Landing.tsx
│   ├── Login.tsx
│   ├── Signup.tsx
│   ├── Dashboard.tsx
│   ├── PostGenerator.tsx
│   ├── PostHistory.tsx
│   ├── BrandProfile.tsx
│   ├── Settings.tsx
│   └── NotFound.tsx
│
├── stores/                     # Zustand stores
│   ├── authStore.ts
│   ├── uiStore.ts
│   └── postStore.ts
│
├── styles/
│   ├── globals.css             # Global styles
│   └── animations.css          # Framer motion presets
│
└── types/
    ├── api.ts                  # API response types
    ├── models.ts               # Data models
    └── common.ts               # Common types
```

---

## 🛣️ Routing Structure

```typescript
// app/router.tsx
import { createBrowserRouter } from 'react-router-dom';

const router = createBrowserRouter([
  // Public Routes
  {
    path: '/',
    element: <LandingPage />,
  },
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/signup',
    element: <SignupPage />,
  },
  
  // Protected Routes (require authentication)
  {
    path: '/app',
    element: <AuthenticatedLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="/app/dashboard" />,
      },
      {
        path: 'dashboard',
        element: <DashboardPage />,
      },
      {
        path: 'generate',
        element: <PostGeneratorPage />,
      },
      {
        path: 'generate/:postId',
        element: <PostGeneratorPage />,  // Continue generation
      },
      {
        path: 'posts',
        element: <PostHistoryPage />,
      },
      {
        path: 'posts/:postId',
        element: <PostDetailPage />,
      },
      {
        path: 'brand-profile',
        element: <BrandProfilePage />,
      },
      {
        path: 'analytics',
        element: <AnalyticsPage />,
      },
      {
        path: 'settings',
        element: <SettingsPage />,
      },
    ],
  },
  
  // 404
  {
    path: '*',
    element: <NotFoundPage />,
  },
]);
```

---

## 📄 Page Specifications

### 1. Landing Page (`/`)

**Purpose:** Convert visitors into users with stunning visuals and clear value proposition.

**Sections:**
1. **Hero Section**
   - Animated headline with typewriter effect
   - "Transform Ideas into Viral LinkedIn Posts in 60 Seconds"
   - Floating UI mockup with parallax effect
   - CTA buttons with glow effects
   - Background: Animated gradient mesh + floating particles

2. **Social Proof Bar**
   - Logo carousel of companies using the product
   - "Trusted by 10,000+ LinkedIn creators"
   - Animated counters: Posts generated, Impressions earned

3. **How It Works**
   - 3-step process with animated icons
   - Step 1: Enter your idea → Step 2: Answer quick questions → Step 3: Get viral-ready content
   - Each step reveals on scroll with staggered animation

4. **Features Grid**
   - 6 feature cards with hover 3D tilt effect
   - Icons with gradient backgrounds
   - Features: AI Agents, Multi-format, Brand Voice, Analytics, etc.

5. **Demo Section**
   - Interactive demo of the post generator
   - Users can try without signing up (limited)
   - Show real-time generation with typing effect

6. **Testimonials**
   - Carousel of video/text testimonials
   - Real LinkedIn profiles with metrics
   - Before/after post comparison

7. **Pricing Section**
   - 3 tier cards with spotlight effect
   - Popular tier highlighted with gradient border
   - Toggle for monthly/annual with discount badge

8. **FAQ Accordion**
   - Smooth expand/collapse animations
   - Search functionality

9. **Final CTA**
   - Full-width gradient background
   - "Start Creating Viral Content Today"
   - Email capture form

10. **Footer**
    - Links, social icons, newsletter signup

**Design Details:**
```jsx
// Hero section example
<section className="relative min-h-screen flex items-center overflow-hidden">
  {/* Animated background */}
  <div className="absolute inset-0 bg-gradient-mesh animate-gradient" />
  <div className="absolute inset-0">
    <ParticleField count={50} />
  </div>
  
  {/* Content */}
  <div className="relative z-10 max-w-7xl mx-auto px-6">
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
    >
      <Badge className="mb-6">✨ Powered by AI Agents</Badge>
      
      <h1 className="font-display text-display-xl text-white">
        Transform Ideas into 
        <span className="bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent">
          {' '}Viral LinkedIn Posts
        </span>
      </h1>
      
      <p className="mt-6 text-xl text-text-secondary max-w-2xl">
        5 AI agents work together to craft scroll-stopping content 
        that sounds like you, performs like the top 1%.
      </p>
      
      <div className="mt-10 flex gap-4">
        <Button size="xl" className="shadow-glow-md">
          Start Free <ArrowRight className="ml-2" />
        </Button>
        <Button variant="outline" size="xl">
          Watch Demo <Play className="ml-2" />
        </Button>
      </div>
    </motion.div>
    
    {/* Floating UI Mockup */}
    <motion.div 
      className="absolute right-0 top-1/2 -translate-y-1/2"
      animate={{ y: [0, -10, 0] }}
      transition={{ duration: 4, repeat: Infinity }}
    >
      <AppMockup />
    </motion.div>
  </div>
</section>
```

---

### 2. Login/Signup Pages (`/login`, `/signup`)

**Design:**
- Split screen: Left = form, Right = animated visual
- Social login options (Google, LinkedIn)
- Magic link option
- Password strength indicator
- Success animations

**Components:**
```jsx
<div className="min-h-screen grid lg:grid-cols-2">
  {/* Left: Form */}
  <div className="flex items-center justify-center p-8">
    <div className="w-full max-w-md space-y-8">
      <Logo className="h-10" />
      <div>
        <h1 className="text-heading-1">Welcome back</h1>
        <p className="text-text-secondary">Sign in to continue creating</p>
      </div>
      
      {/* Social login */}
      <div className="space-y-3">
        <Button variant="outline" className="w-full">
          <GoogleIcon /> Continue with Google
        </Button>
        <Button variant="outline" className="w-full">
          <LinkedInIcon /> Continue with LinkedIn
        </Button>
      </div>
      
      <Divider>or</Divider>
      
      {/* Email form */}
      <form className="space-y-4">
        <Input label="Email" type="email" icon={<Mail />} />
        <Input label="Password" type="password" icon={<Lock />} />
        <Button className="w-full">Sign In</Button>
      </form>
    </div>
  </div>
  
  {/* Right: Visual */}
  <div className="hidden lg:block relative bg-gradient-to-br from-primary-600 to-accent-600">
    <AnimatedPattern />
    <div className="absolute inset-0 flex items-center justify-center">
      <FloatingCards />
    </div>
  </div>
</div>
```

---

### 3. Dashboard (`/app/dashboard`)

**Purpose:** Overview of user activity, quick actions, and insights.

**Layout:**
```
+------------------------------------------------------------------+
| SIDEBAR |                    MAIN CONTENT                        |
|         | +--------------------------------------------------+   |
|  Logo   | |              WELCOME HEADER                      |   |
|---------|--+--------------------------------------------------+   |
| 📊 Dash | | +----------+ +----------+ +----------+ +----------+  |
| ✨ New  | | | Posts    | | Views    | | Engage   | | Score    |  |
| 📝 Posts| | | 24       | | 125.4K   | | 4.8%     | | 8.5      |  |
| 👤 Brand| | +----------+ +----------+ +----------+ +----------+  |
| 📈 Stats| | +---------------------------------------------+     |
| ⚙️ Set  | | |         QUICK ACTIONS                       |     |
|         | | | [+ New Post] [View History] [Edit Profile]  |     |
|         | | +---------------------------------------------+     |
|         | | +---------------------+ +---------------------+     |
|         | | | RECENT POSTS        | | PERFORMANCE CHART   |     |
|         | | |                     | |                     |     |
|         | | |                     | |                     |     |
|         | | +---------------------+ +---------------------+     |
+------------------------------------------------------------------+
```

**Components:**

1. **Stats Cards** - Animated counters with sparkline mini-charts
2. **Quick Actions** - Large button cards with gradients
3. **Recent Posts** - Card list with status badges and actions
4. **Performance Chart** - Line chart with impressions over time
5. **AI Insights** - Suggestions from AI analysis

---

### 4. Post Generator (`/app/generate`) - THE HERO PAGE

**This is the most important page - the core product experience.**

**Flow:**
```
STEP 1: INPUT IDEA
       ↓
STEP 2: VALIDATION (animated loading, show agent working)
       ↓
STEP 3: STRATEGY & QUESTIONS
       ↓
STEP 4: ANSWER QUESTIONS (interactive form)
       ↓
STEP 5: GENERATION (show each agent's progress)
       ↓
STEP 6: REVIEW & SELECT (hooks, preview, edit)
       ↓
STEP 7: FINAL OUTPUT (copy, schedule, download)
```

**Design:**

```jsx
// Post Generator Page
<div className="min-h-screen bg-background-primary">
  {/* Progress indicator */}
  <div className="fixed top-0 left-0 right-0 z-50">
    <StepProgress currentStep={step} totalSteps={7} />
  </div>
  
  <div className="max-w-4xl mx-auto py-20 px-6">
    <AnimatePresence mode="wait">
      {step === 1 && <IdeaInputStep key="step1" onNext={handleNext} />}
      {step === 2 && <ValidationStep key="step2" />}
      {step === 3 && <StrategyStep key="step3" />}
      {step === 4 && <QuestionsStep key="step4" />}
      {step === 5 && <GenerationStep key="step5" />}
      {step === 6 && <ReviewStep key="step6" />}
      {step === 7 && <FinalOutputStep key="step7" />}
    </AnimatePresence>
  </div>
</div>
```

**Step 1: Idea Input**
```jsx
<motion.div
  initial={{ opacity: 0, scale: 0.95 }}
  animate={{ opacity: 1, scale: 1 }}
  className="text-center space-y-8"
>
  <div>
    <Sparkles className="h-16 w-16 mx-auto text-accent-400 mb-4" />
    <h1 className="text-heading-1">What do you want to share?</h1>
    <p className="text-text-secondary mt-2">
      Enter your idea and let our AI agents craft the perfect post
    </p>
  </div>
  
  <div className="relative">
    <Textarea
      value={idea}
      onChange={(e) => setIdea(e.target.value)}
      placeholder="e.g., 3 lessons from failing my first startup..."
      className="text-lg p-6 min-h-[200px] resize-none glass gradient-border"
    />
    <div className="absolute bottom-4 right-4 flex items-center gap-4">
      <span className="text-caption text-text-muted">
        {idea.length} / 5000
      </span>
      <Button 
        onClick={handleSubmit}
        disabled={idea.length < 10}
        className="shadow-glow-sm"
      >
        Generate <Sparkles className="ml-2 h-4 w-4" />
      </Button>
    </div>
  </div>
  
  {/* Suggestion chips */}
  <div className="flex flex-wrap gap-2 justify-center">
    {suggestions.map((s) => (
      <Chip key={s} onClick={() => setIdea(s)}>{s}</Chip>
    ))}
  </div>
</motion.div>
```

**Step 5: Generation Progress (THE WOW MOMENT)**
```jsx
<motion.div className="space-y-12">
  <div className="text-center">
    <h1 className="text-heading-1">Creating Your Post</h1>
    <p className="text-text-secondary">
      5 AI agents are working together to craft your content
    </p>
  </div>
  
  {/* Agent Progress */}
  <div className="space-y-6">
    {agents.map((agent, i) => (
      <AgentProgressCard
        key={agent.name}
        agent={agent}
        status={agentStatus[i]}
        isActive={currentAgent === i}
      />
    ))}
  </div>
</motion.div>

// Agent Progress Card
<motion.div 
  className={cn(
    "glass rounded-xl p-6 flex items-center gap-6",
    isActive && "ring-2 ring-accent-500 shadow-glow-md"
  )}
  animate={isActive ? { scale: 1.02 } : { scale: 1 }}
>
  <div className={cn(
    "h-14 w-14 rounded-full flex items-center justify-center",
    status === 'complete' ? "bg-success-500" : 
    status === 'active' ? "bg-accent-500 animate-pulse" : 
    "bg-background-tertiary"
  )}>
    {status === 'complete' ? <Check /> : <agent.icon />}
  </div>
  
  <div className="flex-1">
    <h3 className="font-semibold text-white">{agent.name}</h3>
    <p className="text-text-secondary text-sm">{agent.description}</p>
    {isActive && (
      <motion.div layout className="mt-2">
        <Progress value={progress} className="h-1" />
        <p className="text-caption text-accent-400 mt-1">{agent.status}</p>
      </motion.div>
    )}
  </div>
  
  <div className="text-right">
    {status === 'complete' && (
      <span className="text-success-400 text-sm">✓ Done</span>
    )}
    {status === 'active' && (
      <LoadingDots />
    )}
  </div>
</motion.div>
```

**Step 6: Hook Selection**
```jsx
<div className="space-y-8">
  <h2 className="text-heading-2 text-center">Choose Your Hook</h2>
  
  <div className="grid gap-4">
    {hooks.map((hook, i) => (
      <motion.div
        key={i}
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
        className={cn(
          "p-6 rounded-xl cursor-pointer transition-all",
          selectedHook === i 
            ? "gradient-border bg-background-tertiary shadow-glow-md" 
            : "glass hover:border-white/20"
        )}
        onClick={() => setSelectedHook(i)}
      >
        <div className="flex items-start gap-4">
          <div className={cn(
            "h-8 w-8 rounded-full flex items-center justify-center text-sm font-bold",
            selectedHook === i ? "bg-accent-500" : "bg-background-primary"
          )}>
            {i + 1}
          </div>
          <div className="flex-1">
            <p className="text-lg text-white">{hook.text}</p>
            <div className="mt-3 flex items-center gap-4 text-sm">
              <span className="text-text-muted">Type: {hook.type}</span>
              <span className="flex items-center gap-1">
                <Star className="h-4 w-4 text-yellow-400" />
                {hook.score}/10
              </span>
            </div>
          </div>
        </div>
      </motion.div>
    ))}
  </div>
</div>
```

**Step 7: Final Output**
```jsx
<div className="grid lg:grid-cols-2 gap-8">
  {/* Preview */}
  <div>
    <h3 className="text-heading-3 mb-4">Preview</h3>
    <div className="glass rounded-xl p-6">
      <LinkedInPostPreview post={generatedPost} />
    </div>
  </div>
  
  {/* Actions & Metrics */}
  <div className="space-y-6">
    <div className="glass rounded-xl p-6">
      <h3 className="font-semibold mb-4">Quality Analysis</h3>
      <div className="space-y-4">
        <QualityBar label="Overall Score" value={8.5} max={10} />
        <QualityBar label="Hook Strength" value={9.2} max={10} />
        <QualityBar label="Brand Alignment" value={8.0} max={10} />
      </div>
    </div>
    
    <div className="glass rounded-xl p-6">
      <h3 className="font-semibold mb-4">Predicted Performance</h3>
      <div className="grid grid-cols-2 gap-4">
        <Stat label="Impressions" value="5K - 15K" />
        <Stat label="Engagement" value="4.5%" />
      </div>
    </div>
    
    <div className="flex gap-4">
      <Button className="flex-1" onClick={copyToClipboard}>
        <Copy className="mr-2" /> Copy
      </Button>
      <Button variant="outline" className="flex-1">
        <Calendar className="mr-2" /> Schedule
      </Button>
      <Button variant="outline">
        <Download className="mr-2" />
      </Button>
    </div>
  </div>
</div>
```

---

### 5. Post History (`/app/posts`)

**Layout:**
- Filter bar (status, date, format)
- Search
- Grid/List view toggle
- Pagination
- Each card shows: idea, status, date, metrics, actions

**Card Design:**
```jsx
<motion.div 
  className="glass rounded-xl p-5 hover:shadow-glow-sm transition-all cursor-pointer group"
  whileHover={{ y: -2 }}
>
  <div className="flex items-start justify-between">
    <div className="flex-1">
      <Badge variant={post.status}>{post.status}</Badge>
      <h3 className="mt-2 font-medium text-white line-clamp-2">
        {post.raw_idea}
      </h3>
      <p className="mt-1 text-sm text-text-muted">
        {formatDate(post.created_at)}
      </p>
    </div>
    <DropdownMenu>
      <DropdownMenuTrigger>
        <MoreVertical className="opacity-0 group-hover:opacity-100 transition" />
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem>View</DropdownMenuItem>
        <DropdownMenuItem>Copy</DropdownMenuItem>
        <DropdownMenuItem>Delete</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  </div>
  
  {post.quality_score && (
    <div className="mt-4 flex items-center gap-4 text-sm">
      <span className="flex items-center gap-1">
        <Star className="h-4 w-4 text-yellow-400" />
        {post.quality_score}
      </span>
      <span className="text-text-muted">{post.format}</span>
    </div>
  )}
</motion.div>
```

---

### 6. Brand Profile (`/app/brand-profile`)

**Sections:**
1. Profile header with avatar/name
2. Content Pillars (drag-drop reorder, add/remove)
3. Target Audience editor
4. Brand Voice settings with tone sliders
5. Visual Guidelines
6. Sample posts for voice calibration

---

### 7. Settings (`/app/settings`)

**Tabs:**
- Account (name, email, avatar)
- Subscription (plan, billing)
- API Keys (for integrations)
- Notifications (email preferences)
- Privacy & Data
- Danger Zone (delete account)

---

## 🔄 State Management

### Zustand Stores

```typescript
// stores/authStore.ts
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

// stores/uiStore.ts
interface UIState {
  sidebarCollapsed: boolean;
  theme: 'dark' | 'light';
  toasts: Toast[];
  toggleSidebar: () => void;
  addToast: (toast: Toast) => void;
  removeToast: (id: string) => void;
}

// stores/postStore.ts
interface PostState {
  currentGeneration: GenerationState | null;
  recentPosts: Post[];
  setGeneration: (state: GenerationState) => void;
  clearGeneration: () => void;
}
```

### TanStack Query Setup

```typescript
// lib/queries.ts
export const postKeys = {
  all: ['posts'] as const,
  lists: () => [...postKeys.all, 'list'] as const,
  list: (filters: PostFilters) => [...postKeys.lists(), filters] as const,
  details: () => [...postKeys.all, 'detail'] as const,
  detail: (id: string) => [...postKeys.details(), id] as const,
};

export function useGeneratePost() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (idea: IdeaInput) => api.posts.generate(idea),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: postKeys.all });
    },
  });
}

export function usePosts(filters: PostFilters) {
  return useQuery({
    queryKey: postKeys.list(filters),
    queryFn: () => api.posts.list(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
```

---

## 🔌 API Integration

### Axios Setup

```typescript
// lib/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Error interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const apiClient = {
  posts: {
    generate: (input: IdeaInput) => api.post('/api/v1/posts/generate', input),
    submitAnswers: (postId: string, answers: Answer[]) => 
      api.post(`/api/v1/posts/${postId}/answers`, { answers }),
    getStatus: (postId: string) => api.get(`/api/v1/posts/${postId}/status`),
    get: (postId: string) => api.get(`/api/v1/posts/${postId}`),
    list: (params?: ListParams) => api.get('/api/v1/posts', { params }),
  },
  auth: {
    login: (creds: LoginCredentials) => api.post('/auth/login', creds),
    signup: (data: SignupData) => api.post('/auth/signup', data),
    me: () => api.get('/auth/me'),
  },
  brand: {
    get: () => api.get('/api/v1/brand-profile'),
    update: (data: BrandProfile) => api.put('/api/v1/brand-profile', data),
  },
};
```

---

## 🎭 Animation Presets

```typescript
// lib/animations.ts
import { Variants } from 'framer-motion';

export const fadeIn: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -10 },
};

export const slideInLeft: Variants = {
  initial: { opacity: 0, x: -50 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 50 },
};

export const scaleIn: Variants = {
  initial: { opacity: 0, scale: 0.9 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.9 },
};

export const staggerContainer: Variants = {
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

export const springConfig = {
  type: 'spring',
  stiffness: 400,
  damping: 30,
};

export const smoothTransition = {
  type: 'tween',
  ease: [0.4, 0, 0.2, 1],
  duration: 0.3,
};
```

---

## 🔐 Authentication Flow

```
1. User arrives → Check localStorage for token
2. If token exists → Validate with /auth/me
3. If valid → Set user in authStore → Redirect to /app/dashboard
4. If invalid → Clear token → Redirect to /login
5. Login → Store token → Redirect to /app/dashboard
6. Logout → Clear token + state → Redirect to /
```

---

## 📱 Responsive Breakpoints

```javascript
// tailwind.config.js
screens: {
  'sm': '640px',
  'md': '768px',
  'lg': '1024px',
  'xl': '1280px',
  '2xl': '1536px',
}

// Mobile-first approach
// Sidebar: Hidden on mobile, collapsible on larger screens
// Cards: Stack on mobile, grid on larger screens
// Navigation: Bottom tab bar on mobile
```

---

## 🚀 Build Checklist

### Phase 1: Setup & Foundation
- [ ] Initialize project with Vite + React + TypeScript
- [ ] Configure Tailwind CSS with custom theme
- [ ] Install and configure Shadcn/UI
- [ ] Set up React Router
- [ ] Configure TanStack Query
- [ ] Set up Zustand stores
- [ ] Create API client with Axios
- [ ] Set up Framer Motion

### Phase 2: Core Layout
- [ ] Create MainLayout component
- [ ] Build Sidebar with navigation
- [ ] Build TopNavbar
- [ ] Create responsive shell

### Phase 3: Authentication
- [ ] Build Login page
- [ ] Build Signup page
- [ ] Implement auth flow
- [ ] Create protected route wrapper

### Phase 4: Landing Page
- [ ] Hero section with animations
- [ ] Features grid
- [ ] How it works section
- [ ] Testimonials carousel
- [ ] Pricing section
- [ ] Footer

### Phase 5: Dashboard
- [ ] Stats cards with animations
- [ ] Quick actions
- [ ] Recent posts list
- [ ] Performance chart

### Phase 6: Post Generator (Core Feature)
- [ ] Step progress indicator
- [ ] Idea input step
- [ ] Validation step with loading
- [ ] Questions step
- [ ] Generation progress with agents
- [ ] Hook selection step
- [ ] Final output with preview

### Phase 7: Post History
- [ ] Filters and search
- [ ] Post cards grid
- [ ] Post detail view
- [ ] Pagination

### Phase 8: Brand Profile
- [ ] Profile editor
- [ ] Content pillars manager
- [ ] Voice settings

### Phase 9: Settings
- [ ] Account settings
- [ ] Subscription management
- [ ] API keys

### Phase 10: Polish
- [ ] Loading states everywhere
- [ ] Error boundaries
- [ ] Empty states
- [ ] Toast notifications
- [ ] Keyboard shortcuts
- [ ] Performance optimization

---

## 📋 Lovable AI Prompt Template

Use this prompt with Lovable AI to generate the frontend:

```
Create a premium React application for an AI-powered LinkedIn post generator.

TECH STACK:
- React 18 with TypeScript
- React Router v6 for routing
- Tailwind CSS for styling
- Shadcn/UI components
- Framer Motion for animations
- TanStack Query for data fetching
- Zustand for state management
- Lucide icons

DESIGN:
- Dark theme with deep purple (#0a0a0f) background
- Glassmorphism effects with frosted glass cards
- LinkedIn blue (#0077b5) primary color
- Purple/violet (#8b5cf6) accent color
- Inter font for body, Space Grotesk for headings
- Smooth micro-animations on all interactions
- Premium, enterprise-grade aesthetic
- NOT a simple website - this is a $100K premium SaaS product

PAGES NEEDED:
1. Landing page with hero, features, pricing
2. Login/Signup with social auth buttons
3. Dashboard with stats and recent activity
4. Post Generator with multi-step wizard flow
5. Post History with filters and search
6. Brand Profile editor
7. Settings page

KEY FEATURES:
- Multi-step post generation wizard
- Real-time agent progress visualization
- Hook selection carousel
- LinkedIn post preview
- Quality score display
- Performance predictions

The post generator is the hero feature - make it feel magical with 
animated progress states showing each AI agent working.
```

---

This document provides everything needed to build a $100K+ premium frontend. The key is attention to detail in animations, spacing, and micro-interactions that make the product feel polished and professional.
