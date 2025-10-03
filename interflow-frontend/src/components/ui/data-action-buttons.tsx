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

interface S3ImportConfig extends ButtonConfig {
  importFromS3Function?: () => Promise<unknown>;
  onSuccess?: () => void;
}

interface DataActionButtonsProps {
  // Configuration par thème
  add?: ButtonConfig;
  import?: ImportConfig;
  flush?: FlushConfig;
  refresh?: RefreshConfig;
  s3Import?: S3ImportConfig;
  
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
  s3Import,
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
  
  const s3ImportDefaults = {
    show: false,
    label: "Importer depuis S3",
    ...s3Import
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

  // Mutation pour l'import S3
  const s3ImportMutation = useMutation({
    mutationFn: s3ImportDefaults.importFromS3Function || (() => Promise.resolve()),
    onSuccess: (data: unknown) => {
      // console.log("✅ [S3_IMPORT] Import S3 réussi");
      
      // Afficher les détails de l'import si disponibles
      if (data && typeof data === 'object') {
        const importData = data as { 
          besoins_importes?: number; 
          stocks_importes?: number; 
          receptions_importees?: number;
          message: string 
        };
        
        const count = importData.besoins_importes || importData.stocks_importes || importData.receptions_importees || 0;
        const label = importData.besoins_importes 
          ? 'besoin(s)' 
          : importData.stocks_importes 
            ? 'stock(s)' 
            : 'réception(s)';
        
        console.log(`✨ [S3_IMPORT] ${count} ${label} importé(s) avec succès`);
        alert(`✅ Import S3 réussi!\n\n${count} ${label} importé(s)`);
      }
      
      s3ImportDefaults.onSuccess?.();
      if (queryKey.length > 0) {
        queryClient.invalidateQueries({ queryKey });
      }
    },
    onError: (error) => {
      console.error("❌ [S3_IMPORT] Erreur lors de l'import S3:", error);
      alert(`❌ Erreur lors de l'import S3:\n${error instanceof Error ? error.message : 'Erreur inconnue'}`);
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

  const handleS3ImportClick = () => {
    // console.log("🔍 [ACTION] Bouton import S3 cliqué");
    s3ImportMutation.mutate();
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
      
      {/* Bouton Import from S3 */}
      {s3ImportDefaults.show && s3ImportDefaults.importFromS3Function && (
        <Button
          variant="default"
          size="sm"
          onClick={handleS3ImportClick}
          disabled={s3ImportMutation.isPending}
          className="flex items-center gap-2"
        >
          {s3ImportMutation.isPending ? (
            <LoadingSpinner size={16} />
          ) : (
            <span className="text-lg">☁️</span>
          )}
          {s3ImportDefaults.label}
        </Button>
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