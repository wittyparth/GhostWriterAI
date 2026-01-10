/**
 * Protected Route wrapper component
 * 
 * Redirects unauthenticated users to landing page.
 */

import { Navigate, useLocation } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { getAccessToken } from "@/services/auth";
import { Loader2 } from "lucide-react";
import { useEffect, useState } from "react";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore();
  const location = useLocation();
  const [hasChecked, setHasChecked] = useState(false);

  useEffect(() => {
    const runCheck = async () => {
      await checkAuth();
      setHasChecked(true);
    };
    runCheck();
  }, [checkAuth]);

  // Show loading while checking authentication
  if (isLoading || !hasChecked) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  // Check both store state and token existence
  const hasToken = !!getAccessToken();
  
  if (!isAuthenticated || !hasToken) {
    // Redirect to landing page when not authenticated
    return <Navigate to="/" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}
