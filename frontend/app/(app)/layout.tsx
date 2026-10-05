import { RequireAuth } from "@/components/require-auth";
import { Sidebar } from "@/components/sidebar";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <RequireAuth>
      <div className="flex min-h-screen bg-blush-50">
        <Sidebar />
        <main className="flex-1 min-w-0">{children}</main>
      </div>
    </RequireAuth>
  );
}