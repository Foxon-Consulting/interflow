import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";

interface RefreshButtonProps {
  onRefresh: () => void;
  isLoading?: boolean;
  label?: string;
  size?: "sm" | "default" | "lg";
  variant?: "outline" | "default" | "secondary";
}

export function RefreshButton({ 
  onRefresh, 
  isLoading = false, 
  label = "Rafraîchir",
  size = "sm",
  variant = "outline"
}: RefreshButtonProps) {
  return (
    <Button
      onClick={onRefresh}
      disabled={isLoading}
      variant={variant}
      size={size}
      className="flex items-center gap-2"
    >
      <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
      {label}
    </Button>
  );
} 