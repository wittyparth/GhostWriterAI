import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { CheckCircle2, XCircle, ArrowRight, Loader2 } from "lucide-react";
import { verifyEmail } from "@/services/auth";
import { toast } from "sonner";
import { useAuthStore } from "@/stores/authStore";

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const navigate = useNavigate();
  const { setUser } = useAuthStore();
  
  const [status, setStatus] = useState<"verifying" | "success" | "error">("verifying");
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setErrorMessage("Missing verification token.");
      return;
    }

    const verify = async () => {
      try {
        const tokens = await verifyEmail(token);
        // Auth store automatically stores tokens inside verifyEmail wrapper if implemented there, 
        // but here verifyEmail returns tokens.
        // We should ensure the store is updated.
        // wait, I updated verifyEmail in auth.ts to call storeTokens.
        // So I just need to update the zustand store state.
        setUser(tokens.user);
        
        setStatus("success");
      } catch (error: any) {
        setStatus("error");
        setErrorMessage(error.message || "Verification failed. The link may be expired.");
      }
    };

    verify();
  }, [token, setUser]);

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-background">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-md w-full text-center space-y-6"
      >
        <div className="flex justify-center">
          <div className="h-12 w-12 rounded-xl bg-primary flex items-center justify-center text-primary-foreground font-bold text-xl">
            G
          </div>
        </div>
        
        <h1 className="text-3xl font-bold tracking-tight">Email Verification</h1>
        
        {status === "verifying" && (
          <div className="flex flex-col items-center gap-4 py-8">
            <Loader2 className="h-12 w-12 animate-spin text-primary" />
            <p className="text-muted-foreground">Verifying your email address...</p>
          </div>
        )}
        
        {status === "success" && (
          <div className="flex flex-col items-center gap-4 py-6">
            <div className="h-16 w-16 bg-green-100 rounded-full flex items-center justify-center text-green-600">
              <CheckCircle2 className="h-8 w-8" />
            </div>
            <div className="space-y-2">
              <h2 className="text-xl font-semibold">Verification Successful!</h2>
              <p className="text-muted-foreground">
                Your email has been verified. You can now access your dashboard.
              </p>
            </div>
            <Button 
              className="w-full mt-4" 
              onClick={() => navigate("/app/dashboard")}
            >
              Go to Dashboard
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        )}
        
        {status === "error" && (
          <div className="flex flex-col items-center gap-4 py-6">
            <div className="h-16 w-16 bg-red-100 rounded-full flex items-center justify-center text-red-600">
              <XCircle className="h-8 w-8" />
            </div>
            <div className="space-y-2">
              <h2 className="text-xl font-semibold">Verification Failed</h2>
              <p className="text-muted-foreground">
                {errorMessage}
              </p>
            </div>
            <div className="space-y-3 w-full mt-4">
              <Button 
                variant="outline"
                className="w-full"
                onClick={() => navigate("/login")}
              >
                Back to Login
              </Button>
              <p className="text-xs text-muted-foreground">
                You can try logging in to request a new verification link.
              </p>
            </div>
          </div>
        )}
        
      </motion.div>
    </div>
  );
}
