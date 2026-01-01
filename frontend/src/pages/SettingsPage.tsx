import { motion } from "framer-motion";
import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger,
} from "@/components/ui/dialog";
import { User, Shield, Trash2, Save, Camera, AlertTriangle, Bell, Key } from "lucide-react";
import { Switch } from "@/components/ui/switch";
import { toast } from "sonner";
import { useQuery } from "@tanstack/react-query";
import { Skeleton } from "@/components/ui/skeleton";
import { getCurrentUser } from "@/services/auth";
import { useEffect } from "react";

export default function SettingsPage() {
  const [profile, setProfile] = useState({ name: "", email: "" });
  const { data: user, isLoading } = useQuery({ queryKey: ["me"], queryFn: getCurrentUser });

  useEffect(() => {
    if (user) {
      setProfile({ name: user.name, email: user.email });
    }
  }, [user]);
  const [notifications, setNotifications] = useState({ email: true, push: false, weekly: true });
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteConfirmation, setDeleteConfirmation] = useState("");

  const handleSaveProfile = () => {
    toast.success("Profile updated successfully!");
  };

  const handleDeleteAccount = () => {
    if (deleteConfirmation === "DELETE") {
      toast.success("Account deletion initiated...");
      setDeleteDialogOpen(false);
    } else {
      toast.error("Please type DELETE to confirm");
    }
  };

  if (isLoading) {
    return (
       <div className="max-w-4xl mx-auto space-y-6">
          <div className="space-y-2">
             <Skeleton className="h-8 w-32" />
             <Skeleton className="h-4 w-48" />
          </div>
          <div className="space-y-6">
             <Skeleton className="h-10 w-96 rounded-md" />
             <Card>
                 <CardContent className="p-6 space-y-6">
                     <Skeleton className="h-6 w-40" />
                     <div className="flex gap-6">
                         <Skeleton className="h-16 w-16 rounded-xl" />
                         <div className="space-y-2">
                             <Skeleton className="h-9 w-32" />
                             <Skeleton className="h-3 w-24" />
                         </div>
                     </div>
                     <div className="space-y-4">
                         <div className="space-y-2">
                             <Skeleton className="h-4 w-20" />
                             <Skeleton className="h-10 w-full" />
                         </div>
                         <div className="space-y-2">
                             <Skeleton className="h-4 w-20" />
                             <Skeleton className="h-10 w-full" />
                         </div>
                     </div>
                     <div className="flex justify-end">
                         <Skeleton className="h-10 w-32" />
                     </div>
                 </CardContent>
             </Card>
          </div>
       </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-1">Manage your account preferences</p>
      </div>

      <Tabs defaultValue="account" className="space-y-6">
        <TabsList className="grid grid-cols-3 lg:w-fit">
          <TabsTrigger value="account" className="gap-2">
            <User className="h-4 w-4" />
            <span className="hidden sm:inline">Account</span>
          </TabsTrigger>
          <TabsTrigger value="notifications" className="gap-2">
            <Bell className="h-4 w-4" />
            <span className="hidden sm:inline">Notifications</span>
          </TabsTrigger>
          <TabsTrigger value="danger" className="gap-2">
            <Shield className="h-4 w-4" />
            <span className="hidden sm:inline">Security</span>
          </TabsTrigger>
        </TabsList>

        {/* Account Tab */}
        <TabsContent value="account">
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <Card>
              <CardContent className="p-6 space-y-6">
                <h3 className="font-semibold">Profile Information</h3>
                <div className="flex items-center gap-6">
                  <div className="relative group">
                    <div className="h-16 w-16 rounded-xl bg-primary flex items-center justify-center text-xl font-bold text-primary-foreground">
                      {profile.name.charAt(0)}
                    </div>
                    <button className="absolute inset-0 bg-black/50 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white">
                      <Camera className="h-5 w-5" />
                    </button>
                  </div>
                  <div>
                    <Button variant="outline" size="sm">Upload Photo</Button>
                    <p className="text-xs text-muted-foreground mt-1">JPG, PNG. Max 2MB.</p>
                  </div>
                </div>
                <div className="grid gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name</Label>
                    <Input id="name" value={profile.name} onChange={(e) => setProfile({ ...profile, name: e.target.value })} />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address</Label>
                    <Input id="email" type="email" value={profile.email} onChange={(e) => setProfile({ ...profile, email: e.target.value })} />
                  </div>
                </div>
                <div className="flex justify-end">
                  <Button onClick={handleSaveProfile}>
                    <Save className="mr-2 h-4 w-4" /> Save Changes
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
          
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }} className="mt-6">
            <Card>
              <CardContent className="p-6 space-y-4">
                <div className="flex items-center gap-2">
                  <Key className="h-5 w-5 text-muted-foreground" />
                  <h3 className="font-semibold">Password</h3>
                </div>
                <p className="text-sm text-muted-foreground">Change your password to keep your account secure.</p>
                <Button variant="outline">Change Password</Button>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications">
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <Card>
              <CardContent className="p-6 space-y-6">
                <h3 className="font-semibold">Notification Preferences</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Email Notifications</p>
                      <p className="text-sm text-muted-foreground">Receive updates about your posts via email</p>
                    </div>
                    <Switch checked={notifications.email} onCheckedChange={(v) => setNotifications({ ...notifications, email: v })} />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Push Notifications</p>
                      <p className="text-sm text-muted-foreground">Get notified when your posts are ready</p>
                    </div>
                    <Switch checked={notifications.push} onCheckedChange={(v) => setNotifications({ ...notifications, push: v })} />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Weekly Summary</p>
                      <p className="text-sm text-muted-foreground">Receive a weekly digest of your content performance</p>
                    </div>
                    <Switch checked={notifications.weekly} onCheckedChange={(v) => setNotifications({ ...notifications, weekly: v })} />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        {/* Danger Zone Tab */}
        <TabsContent value="danger">
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <Card className="border-destructive/30">
              <CardContent className="p-6">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="h-5 w-5 text-destructive" />
                  <h3 className="font-semibold text-destructive">Danger Zone</h3>
                </div>
                <p className="text-muted-foreground text-sm mb-4">Once you delete your account, there is no going back. All your data will be permanently removed.</p>
                <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
                  <DialogTrigger asChild>
                    <Button variant="destructive">
                      <Trash2 className="mr-2 h-4 w-4" /> Delete Account
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Are you absolutely sure?</DialogTitle>
                      <DialogDescription>This action cannot be undone. This will permanently delete your account and remove all your data from our servers.</DialogDescription>
                    </DialogHeader>
                    <div className="py-4">
                      <Label htmlFor="delete-confirmation">Type <span className="font-bold">DELETE</span> to confirm</Label>
                      <Input id="delete-confirmation" className="mt-2" value={deleteConfirmation} onChange={(e) => setDeleteConfirmation(e.target.value)} placeholder="DELETE" />
                    </div>
                    <DialogFooter>
                      <Button variant="ghost" onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
                      <Button variant="destructive" onClick={handleDeleteAccount} disabled={deleteConfirmation !== "DELETE"}>Delete Account</Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
