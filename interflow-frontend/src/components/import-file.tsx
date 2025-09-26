'use client';

import { useState, useRef } from 'react';
import { Button } from "@/components/ui/button";
import { Upload } from "lucide-react";
import { toast } from "@/components/ui/use-toast";

interface ImportFileProps {
  onImportSuccess: () => void;
  importFunction: (file: File) => Promise<unknown>;
  label?: string;
  acceptedFormats?: string[];
}

export default function ImportFile({ 
  onImportSuccess, 
  importFunction,
  label = "Importer fichier",
  acceptedFormats = ['.csv', '.xlsx', '.xls']
}: ImportFileProps) {
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (file: File) => {
    // Vérifier que c'est un fichier supporté
    const fileName = file.name.toLowerCase();
    const isSupportedFormat = acceptedFormats.some(format => 
      fileName.endsWith(format.toLowerCase())
    );

    if (!isSupportedFormat) {
      toast({
        title: "Erreur",
        description: `Veuillez sélectionner un fichier ${acceptedFormats.join(' ou ')}`,
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      await importFunction(file);
      toast({
        title: "Succès",
        description: "Import réussi !",
      });
      onImportSuccess();
      
      // Réinitialiser l'input file
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Erreur lors de l\'import:', error);
      toast({
        title: "Erreur",
        description: `Erreur lors de l'import: ${error instanceof Error ? error.message : 'Erreur inconnue'}`,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  // Créer la chaîne d'acceptation pour l'input file
  const acceptString = acceptedFormats.join(',');

  return (
    <>
      <Button
        onClick={handleButtonClick}
        disabled={isLoading}
        variant="outline"
        size="sm"
        className="flex items-center gap-2"
      >
        {isLoading ? (
          <>
            <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Import...
          </>
        ) : (
          <>
            <Upload className="h-4 w-4" />
            {label}
          </>
        )}
      </Button>

      {/* Input file caché */}
      <input
        ref={fileInputRef}
        type="file"
        accept={acceptString}
        onChange={handleFileChange}
        className="hidden"
      />
    </>
  );
} 