"use client";

import { Button } from "@/components/ui/button";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { RefreshButton } from "@/components/ui/refresh-button";
import ImportFile from "@/components/import-file";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";

// Configuration de base pour tous les boutons
interface ButtonConfig {
  show?: boolean;
  label?: string;
  onClick?: () => void;
}

// Configuration spécialisée pour chaque type de bouton
interface ImportConfig extends ButtonConfig {
  importFunction?: (file: File) => Promise<unknown>;
  onSuccess?: () => void;
  acceptedFormats?: string[];
}

interface FlushConfig extends ButtonConfig {
  flushFunction?: () => Promise<void>;
  confirmMessage?: string;
}

interface RefreshConfig extends ButtonConfig {
  onRefresh?: () => void;
  isLoading?: boolean;
}

interface DataActionButtonsProps {
  // Configuration par thème
  add?: ButtonConfig;
  import?: ImportConfig;
  flush?: FlushConfig;
  refresh?: RefreshConfig;
  
  // Configuration globale
  queryKey?: string[];
  orientation?: 'horizontal' | 'vertical';
  spacing?: 'sm' | 'md' | 'lg';
}

export function DataActionButtons({
  add,
  import: importConfig,
  flush,
  refresh,
  queryKey = [],
  orientation = 'horizontal',
  spacing = 'md'
}: DataActionButtonsProps) {
  const queryClient = useQueryClient();
  
  // Valeurs par défaut pour chaque configuration
  const addDefaults = {
    show: false,
    label: "Ajouter",
    ...add
  };
  
  const importDefaults = {
    show: false,
    label: "Importer",
    acceptedFormats: ['.csv', '.xlsx', '.xls'],
    ...importConfig
  };
  
  const flushDefaults = {
    show: false,
    label: "Supprimer tous",
    confirmMessage: "Êtes-vous sûr de vouloir supprimer tous les éléments ?",
    ...flush
  };
  
  const refreshDefaults = {
    show: false,
    label: "Rafraîchir",
    isLoading: false,
    ...refresh
  };
  
  // Mutation pour le flush
  const flushMutation = useMutation({
    mutationFn: flushDefaults.flushFunction || (() => Promise.resolve()),
    onSuccess: () => {
      // console.log("✅ [FLUSH] Données vidées avec succès");
      // Invalider le cache pour forcer un refetch
      if (queryKey.length > 0) {
        queryClient.invalidateQueries({ queryKey });
      }
      // Rafraîchir la page après un délai pour s'assurer que les données sont mises à jour
      setTimeout(() => {
        // console.log("🔄 [FLUSH] Rafraîchissement automatique de la page");
        window.location.reload();
      }, 500);
    },
    onError: (error) => {
      console.error("❌ [FLUSH] Erreur lors du vidage des données:", error);
    }
  });

  // Gestionnaires d'événements
  const handleFlushClick = () => {
    // console.log("🔍 [ACTION] Bouton flush cliqué");
    if (flushDefaults.confirmMessage && window.confirm(flushDefaults.confirmMessage)) {
      flushMutation.mutate();
    }
  };

  const handleAddClick = () => {
    // console.log("🔍 [ACTION] Bouton ajouter cliqué");
    addDefaults.onClick?.();
  };

  // Classes CSS dynamiques
  const containerClasses = [
    'flex items-center',
    orientation === 'vertical' ? 'flex-col' : 'flex-row',
    spacing === 'sm' ? 'gap-1' : spacing === 'md' ? 'gap-2' : 'gap-4'
  ].join(' ');

  return (
    <div className={containerClasses}>
      {/* Bouton Ajouter */}
      {addDefaults.show && addDefaults.onClick && (
        <Button
          variant="default"
          size="sm"
          onClick={handleAddClick}
          className="flex items-center gap-2"
        >
          <Plus size={16} />
          {addDefaults.label}
        </Button>
      )}
      
      {/* Bouton Import */}
      {importDefaults.show && importDefaults.importFunction && (
        <ImportFile
          onImportSuccess={() => {
            // console.log("✅ [IMPORT] Import réussi, rafraîchissement des données");
            importDefaults.onSuccess?.();
          }}
          importFunction={importDefaults.importFunction}
          label={importDefaults.label}
          acceptedFormats={importDefaults.acceptedFormats}
        />
      )}
      
      {/* Bouton Supprimer tous */}
      {flushDefaults.show && flushDefaults.flushFunction && (
        <Button
          variant="destructive"
          size="sm"
          onClick={handleFlushClick}
          disabled={flushMutation.isPending}
          className="w-10 h-10 p-0 flex items-center justify-center"
          title={flushDefaults.label}
        >
          {flushMutation.isPending ? (
            <LoadingSpinner size={16} />
          ) : (
            <span className="text-lg">🗑️</span>
          )}
        </Button>
      )}
      
      {/* Bouton Rafraîchir */}
      {refreshDefaults.show && refreshDefaults.onRefresh && (
        <RefreshButton 
          onRefresh={() => {
            // console.log("🔍 [ACTION] Bouton de rafraîchissement cliqué");
            refreshDefaults.onRefresh?.();
          }}
          isLoading={refreshDefaults.isLoading}
        />
      )}
    </div>
  );
} 