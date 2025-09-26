"use client";

import { AlertCircle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";

interface ErrorMessageProps {
  error: Error | unknown;
  resetFn?: () => void;
}

export function ErrorMessage({ error, resetFn }: ErrorMessageProps) {
  const errorMessage = error instanceof Error 
    ? error.message 
    : "Une erreur s'est produite";

  return (
    <Alert variant="destructive" className="my-4">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>Erreur</AlertTitle>
      <AlertDescription className="flex flex-col gap-2">
        <p>{errorMessage}</p>
        {resetFn && (
          <Button variant="outline" size="sm" onClick={resetFn} className="self-start">
            Réessayer
          </Button>
        )}
      </AlertDescription>
    </Alert>
  );
} 