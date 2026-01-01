import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { NavLink, Outlet, Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Sparkles,
  FileText,
  History,
  User,
  BarChart3,
  Settings,
  LogOut,
  Menu,
  X,
  ChevronLeft,
  Home,
} from "lucide-react";
import { useState } from "react";
import { ThemeToggle } from "@/components/ThemeToggle";

import { CreditDisplay } from "@/components/shared/CreditDisplay";

const navItems = [
  { to: "/app/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/app/generate", icon: Sparkles, label: "New Post" },
  { to: "/app/generations", icon: History, label: "Generation History" },
  { to: "/app/posts", icon: FileText, label: "Post Library" },
  { to: "/app/brand-profile", icon: User, label: "Brand Profile" },
  { to: "/app/analytics", icon: BarChart3, label: "Analytics" },
  { to: "/app/settings", icon: Settings, label: "Settings" },
];

export default function AppLayout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  return (
    <div className="min-h-screen bg-background flex">
      {/* Desktop Sidebar */}
      <aside
        className={cn(
          "hidden lg:flex flex-col fixed left-0 top-0 bottom-0 z-40 bg-sidebar border-r border-sidebar-border transition-all duration-300",
          sidebarCollapsed ? "w-16" : "w-60"
        )}
      >
        {/* Logo */}
        <div className="h-14 flex items-center justify-between px-4 border-b border-sidebar-border">
          <Link to="/" className="flex items-center gap-2 group">
            <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center text-primary-foreground font-bold text-sm">
              G
            </div>
            {!sidebarCollapsed && (
              <span className="font-semibold text-sidebar-foreground group-hover:text-primary transition-colors">
                GhostWriter AI
              </span>
            )}
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200",
                  isActive
                    ? "bg-primary text-primary-foreground font-medium shadow-sm"
                    : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                  sidebarCollapsed && "justify-center px-2"
                )
              }
            >
              <item.icon className="h-4 w-4 flex-shrink-0" />
              {!sidebarCollapsed && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* Credit Display */}
        {!sidebarCollapsed && (
          <div className="px-3 mb-2">
            <CreditDisplay />
          </div>
        )}

        {/* Collapse toggle */}
        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="absolute -right-3 top-20 h-6 w-6 rounded-full bg-background border border-border flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted transition-colors shadow-sm"
        >
          <ChevronLeft
            className={cn(
              "h-3 w-3 transition-transform duration-200",
              sidebarCollapsed && "rotate-180"
            )}
          />
        </button>

        {/* Bottom section */}
        <div className="p-3 border-t border-sidebar-border space-y-1">
          {/* Back to Landing */}
          <Link
            to="/"
            className={cn(
              "flex items-center gap-2 px-3 py-2 text-sm text-muted-foreground hover:text-foreground hover:bg-sidebar-accent rounded-lg transition-colors",
              sidebarCollapsed && "justify-center px-2"
            )}
          >
            <Home className="h-4 w-4" />
            {!sidebarCollapsed && <span>Home</span>}
          </Link>
          
          <ThemeToggle collapsed={sidebarCollapsed} />
          
          <Button
            variant="ghost"
            size="sm"
            className={cn(
              "w-full justify-start gap-2 text-muted-foreground hover:text-foreground",
              sidebarCollapsed && "justify-center"
            )}
          >
            <LogOut className="h-4 w-4" />
            {!sidebarCollapsed && "Log out"}
          </Button>
        </div>
      </aside>

      {/* Mobile header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 h-14 bg-background/95 backdrop-blur-sm border-b border-border flex items-center justify-between px-4">
        <Link to="/" className="flex items-center gap-2">
          <div className="h-7 w-7 rounded-lg bg-primary flex items-center justify-center text-primary-foreground font-bold text-xs">
            G
          </div>
          <span className="font-semibold">GhostWriter AI</span>
        </Link>
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="h-9 w-9 flex items-center justify-center rounded-lg hover:bg-accent transition-colors"
        >
          {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Mobile menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden fixed inset-0 z-40 bg-background pt-14 flex flex-col">
          <nav className="p-4 space-y-1 flex-1 overflow-y-auto">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setMobileMenuOpen(false)}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-colors",
                    isActive
                      ? "bg-primary text-primary-foreground font-medium"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  )
                }
              >
                <item.icon className="h-4 w-4" />
                <span>{item.label}</span>
              </NavLink>
            ))}
            
            {/* Home link in mobile */}
            <Link
              to="/"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-3 px-4 py-3 rounded-lg text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            >
              <Home className="h-4 w-4" />
              <span>Back to Home</span>
            </Link>
          </nav>
          <div className="p-4 border-t border-border">
            <ThemeToggle />
          </div>
        </div>
      )}

      {/* Main content */}
      <main
        className={cn(
          "flex-1 min-h-screen pt-14 lg:pt-0 transition-all duration-300 flex flex-col",
          sidebarCollapsed ? "lg:ml-16" : "lg:ml-60"
        )}
      >
        <div className="p-6 lg:p-8 max-w-7xl flex-1">
          <Outlet />
        </div>
        <footer className="py-6 border-t border-border mt-auto">
          <div className="flex flex-col items-center justify-center gap-2 text-center">
            <p className="text-sm text-muted-foreground font-medium">GhostWriter AI</p>
            <p className="text-xs text-muted-foreground/60">Created by Partha Saradhi 2026</p>
          </div>
        </footer>
      </main>
    </div>
  );
}
