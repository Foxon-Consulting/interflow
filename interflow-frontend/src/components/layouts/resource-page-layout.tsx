"use client";

import { ReactNode } from "react";
import { DataActionButtons } from "@/components/ui/data-action-buttons";

interface ResourcePageLayoutProps {
  // Titre de la page
  title: string;
  
  // Contenu principal de la page
  children: ReactNode;
  
  // Configuration des boutons d'action (nouvelle approche groupée)
  actions?: {
    add?: {
      show?: boolean;
      onClick?: () => void;
      label?: string;
    };
    import?: {
      show?: boolean;
      importFunction?: (file: File) => Promise<unknown>;
      label?: string;
      onSuccess?: () => void;
      acceptedFormats?: string[];
    };
    s3Import?: {
      show?: boolean;
      importFromS3Function?: () => Promise<unknown>;
      label?: string;
      onSuccess?: () => void;
    };
    flush?: {
      show?: boolean;
      flushFunction?: () => Promise<void>;
      confirmMessage?: string;
      label?: string;
    };
    refresh?: {
      show?: boolean;
      onRefresh?: () => void;
      isLoading?: boolean;
    };
  };
  
  // Configuration globale pour les boutons
  queryKey?: string[];
  orientation?: 'horizontal' | 'vertical';
  spacing?: 'sm' | 'md' | 'lg';
  
  // État des données pour gérer l'affichage vide
  hasData: boolean;
  
  // Message personnalisé quand il n'y a pas de données
  emptyMessage?: string;
  emptyDescription?: string;
}

export function ResourcePageLayout({
  title,
  children,
  actions,
  queryKey,
  orientation = 'horizontal',
  spacing = 'md',
  hasData,
  emptyMessage = "Aucune donnée",
  emptyDescription = "Aucune donnée disponible pour le moment. Importez un fichier CSV pour commencer."
}: ResourcePageLayoutProps) {

  return (
    <div className="container py-10">
      {/* En-tête commun avec titre et boutons d'action */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">{title}</h1>
        <DataActionButtons
          add={actions?.add}
          import={actions?.import}
          s3Import={actions?.s3Import}
          flush={actions?.flush}
          refresh={actions?.refresh}
          queryKey={queryKey}
          orientation={orientation}
          spacing={spacing}
        />
      </div>
      
      {/* Contenu principal */}
      {hasData ? (
        children
      ) : (
        <div className="mt-6">
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📊</div>
            <h2 className="text-xl font-semibold text-gray-700 mb-2">{emptyMessage}</h2>
            <p className="text-gray-500">{emptyDescription}</p>
          </div>
        </div>
      )}
    </div>
  );
} 