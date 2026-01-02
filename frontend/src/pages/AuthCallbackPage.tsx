/**
 * OAuth Callback Page
 * 
 * Handles the redirect from Google OAuth with tokens in URL params.
 * Stores tokens and redirects to dashboard.
 */

import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { storeTokens } from "@/services/auth";
import { Loader2 } from "lucide-react";

export default function AuthCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { setUser } = useAuthStore();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const accessToken = searchParams.get("access_token");
    const refreshToken = searchParams.get("refresh_token");
    const userId = searchParams.get("user_id");
    const email = searchParams.get("email");
    const name = searchParams.get("name");

    if (accessToken && refreshToken && userId && email) {
      // Store tokens
      storeTokens({
        access_token: accessToken,
        refresh_token: refreshToken,
        token_type: "bearer",
        user: {
          user_id: userId,
          email: email,
          name: name || "",
          created_at: new Date().toISOString(),
        },
      });

      // Update auth store
      setUser({
        user_id: userId,
        email: email,
        name: name || "",
        created_at: new Date().toISOString(),
      });

      // Redirect to dashboard
      navigate("/app/dashboard", { replace: true });
    } else {
      setError("Authentication failed. Missing tokens.");
      setTimeout(() => {
        navigate("/login", { replace: true });
      }, 3000);
    }
  }, [searchParams, navigate, setUser]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center space-y-4">
          <p className="text-destructive font-medium">{error}</p>
          <p className="text-muted-foreground text-sm">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-4">
        <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
        <p className="text-muted-foreground">Completing authentication...</p>
      </div>
    </div>
  );
}
