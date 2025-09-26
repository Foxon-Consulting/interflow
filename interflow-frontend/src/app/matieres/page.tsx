"use client";

import { useState, useMemo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { toast } from "@/components/ui/use-toast";
import { 
  TestTube, 
  Download, 
  AlertTriangle, 
  Beaker,
  Zap,
  Droplets,
  Atom,
  Salad,
  ArrowUpDown,
  ArrowUp,
  ArrowDown
} from "lucide-react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchAllMatiereData, importMatieresFromFile, flushMatieres } from "@/services/matiere-service";
import { useDownloadFDS } from "@/hooks/use-matiere-data";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { ErrorMessage } from "@/components/ui/error-message";
import { Matiere } from "@/model/matiere";
import { ResourcePageLayout } from "@/components/layouts/resource-page-layout";
import { SearchFilter, FilterConfig } from "@/components/filters";

const getTypeIcon = (description: string) => {
  if (!description) return <TestTube className="w-4 h-4" />;
  
  const desc = description.toLowerCase();
  if (desc.includes('acide')) return <Droplets className="w-4 h-4 text-red-500" />;
  if (desc.includes('base')) return <Zap className="w-4 h-4 text-blue-500" />;
  if (desc.includes('solvant')) return <Beaker className="w-4 h-4 text-green-500" />;
  if (desc.includes('oxydant')) return <Atom className="w-4 h-4 text-orange-500" />;
  if (desc.includes('sel')) return <Salad className="w-4 h-4 text-purple-500" />;
  
  return <TestTube className="w-4 h-4" />;
};

const getTypeFromDescription = (description: string): string => {
  const desc = description.toLowerCase();
  if (desc.includes('acide') || desc.includes('acid')) return 'Acide';
  if (desc.includes('base') || desc.includes('hydroxyde') || desc.includes('ammoniac')) return 'Base';
  if (desc.includes('solvant') || desc.includes('éthanol') || desc.includes('acétone') || desc.includes('benzène')) return 'Solvant';
  if (desc.includes('oxydant') || desc.includes('peroxyde') || desc.includes('permanganate')) return 'Oxydant';
  if (desc.includes('chlorure') || desc.includes('sel')) return 'Sel';
  return 'Autre';
};

export default function MatieresPage() {
  const queryClient = useQueryClient();
  const downloadFDSMutation = useDownloadFDS();
  
  // États pour les filtres
  const [rechercheText, setRechercheText] = useState("");
  const [filtreSeveso, setFiltreSeveso] = useState<string>("tous");
  
  // États pour le tri
  const [sortField, setSortField] = useState<string>('code_mp');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  
  // Récupérer les données avec une configuration de cache optimisée
  const { data: matieres, isLoading, error, refetch } = useQuery({
    queryKey: ['matiere-data'],
    queryFn: fetchAllMatiereData,
    staleTime: Infinity, // Les données ne deviennent jamais obsolètes automatiquement
    gcTime: 1000 * 60 * 30, // Garder en cache pendant 30 minutes
    refetchOnMount: false, // Ne pas refetch au montage
    refetchOnWindowFocus: false, // Ne pas refetch au focus
    refetchOnReconnect: false, // Ne pas refetch à la reconnexion
    retry: 1, // Réessayer seulement 1 fois en cas d'erreur
  });

  // Fonction de rafraîchissement personnalisée
  const handleRefresh = async () => {
    console.log("🔄 [MATIERES] Rafraîchissement manuel des données...");
    await queryClient.invalidateQueries({ queryKey: ['matiere-data'] });
    await refetch();
    console.log("✅ [MATIERES] Données rafraîchies avec succès");
  };

  // Fonction de rafraîchissement après import
  const handleImportSuccess = async () => {
    console.log("📥 [MATIERES] Import réussi, rafraîchissement des données...");
    await handleRefresh();
  };

  // Fonction pour gérer le tri
  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Fonction pour obtenir l'icône de tri
  const getSortIcon = (field: string) => {
    if (sortField !== field) {
      return <ArrowUpDown className="h-4 w-4" />;
    }
    return sortDirection === 'asc' ? <ArrowUp className="h-4 w-4" /> : <ArrowDown className="h-4 w-4" />;
  };

  // Composant pour les headers triables
  const SortableHeader = ({ field, children }: { field: string; children: React.ReactNode }) => (
    <th 
      className="border border-gray-200 px-2 py-1 text-left cursor-pointer hover:bg-gray-100 transition-colors text-sm"
      onClick={() => handleSort(field)}
    >
      <div className="flex items-center gap-1">
        {children}
        {getSortIcon(field)}
      </div>
    </th>
  );

  // Tri des matières
  const matieresTriees = useMemo(() => {
    if (!matieres) return [];
    
    // Tri des matières
    return matieres.sort((a, b) => {
      let aValue: string | number | boolean | null | undefined;
      let bValue: string | number | boolean | null | undefined;
      
      switch (sortField) {
        case 'code_mp':
          aValue = a.code_mp;
          bValue = b.code_mp;
          break;
        case 'nom':
          aValue = a.nom;
          bValue = b.nom;
          break;
        case 'type':
          aValue = getTypeFromDescription(a.description || '');
          bValue = getTypeFromDescription(b.description || '');
          break;
        case 'seveso':
          aValue = a.seveso;
          bValue = b.seveso;
          break;
        case 'reference':
          aValue = a.internal_reference || '';
          bValue = b.internal_reference || '';
          break;
        default:
          return 0;
      }
      
      // Gérer les valeurs null/undefined
      if (aValue == null && bValue == null) return 0;
      if (aValue == null) return sortDirection === 'asc' ? -1 : 1;
      if (bValue == null) return sortDirection === 'asc' ? 1 : -1;
      
      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }, [matieres, sortField, sortDirection]);

  // Gestion du téléchargement FDS
  const handleDownloadFDS = async (code_mp: string, nom: string) => {
    try {
      await downloadFDSMutation.mutateAsync(code_mp);
      toast({
        title: "Téléchargement FDS",
        description: `FDS de ${nom} téléchargée avec succès.`,
      });
    } catch {
      toast({
        title: "Erreur",
        description: "Impossible de télécharger la FDS.",
        variant: "destructive",
      });
    }
  };

  // Statistiques
  const stats = useMemo(() => {
    if (!matieres) return { total: 0, seveso: 0, types: {} };
    
    const typeCount: Record<string, number> = {};
    let sevesoCount = 0;
    
    matieres.forEach(matiere => {
      const type = getTypeFromDescription(matiere.description || '');
      typeCount[type] = (typeCount[type] || 0) + 1;
      if (matiere.seveso) sevesoCount++;
    });
    
    return {
      total: matieres.length,
      seveso: sevesoCount,
      types: typeCount
    };
  }, [matieres]);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Chargement des matières...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-center">
          <p className="text-red-600 mb-4">Erreur lors du chargement des matières</p>
          <Button variant="outline" onClick={() => window.location.reload()}>
            Réessayer
          </Button>
        </div>
      </div>
    );
  }

  // Contenu principal de la page (statistiques, recherche et liste)
  const matieresContent = (
    <div className="space-y-6">
      {/* Statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total</p>
                <p className="text-2xl font-bold">{stats.total}</p>
              </div>
                             <TestTube className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">SEVESO</p>
                <p className="text-2xl font-bold text-red-600">{stats.seveso}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Acides</p>
                <p className="text-2xl font-bold text-red-500">{stats.types.Acide || 0}</p>
              </div>
              <Droplets className="h-8 w-8 text-red-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Solvants</p>
                <p className="text-2xl font-bold text-purple-500">{stats.types.Solvant || 0}</p>
              </div>
              <Beaker className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
      </div>



            {/* Liste des matières */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TestTube className="h-5 w-5" />
            Catalogue des Matières
          </CardTitle>
        </CardHeader>
        <CardContent>
          {matieresTriees.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground">Aucune matière trouvée</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-200">
                <thead>
                  <tr className="bg-gray-50">
                    <SortableHeader field="code_mp">Code MP</SortableHeader>
                    <SortableHeader field="nom">Nom</SortableHeader>
                    <SortableHeader field="type">Type</SortableHeader>
                    <SortableHeader field="reference">Référence</SortableHeader>
                    <SortableHeader field="seveso">Seveso</SortableHeader>
                    <th className="border border-gray-200 px-2 py-1 text-center text-sm">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {matieresTriees.map((matiere) => (
                    <tr key={matiere.code_mp} className="hover:bg-gray-50">
                      <td className="border border-gray-200 px-2 py-1 text-sm">
                        <div className="flex items-center gap-2">
                          <div className="flex items-center justify-center w-6 h-6 rounded-full bg-accent">
                            {getTypeIcon(matiere.description || '')}
                          </div>
                          {matiere.code_mp}
                        </div>
                      </td>
                      <td className="border border-gray-200 px-2 py-1">
                        <div>
                          <div className="font-medium text-sm">{matiere.nom}</div>
                          <div className="text-xs text-muted-foreground line-clamp-2">
                            {matiere.description}
                          </div>
                        </div>
                      </td>
                      <td className="border border-gray-200 px-2 py-1">
                        <span className="px-1 py-0.5 rounded text-xs bg-blue-100 text-blue-800">
                          {getTypeFromDescription(matiere.description || '')}
                        </span>
                      </td>
                      <td className="border border-gray-200 px-2 py-1 text-sm">
                        {matiere.internal_reference || "Non définie"}
                      </td>
                      <td className="border border-gray-200 px-2 py-1">
                        {matiere.seveso ? (
                          <span className="px-1 py-0.5 bg-red-100 text-red-800 text-xs rounded-full flex items-center gap-1">
                            <AlertTriangle className="h-3 w-3" />
                            SEVESO
                          </span>
                        ) : (
                          <span className="px-1 py-0.5 bg-gray-100 text-gray-800 text-xs rounded-full">Non</span>
                        )}
                      </td>
                      <td className="border border-gray-200 px-2 py-1 text-center">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDownloadFDS(matiere.code_mp, matiere.nom)}
                          disabled={downloadFDSMutation.isPending || !matiere.fds}
                          className="flex items-center gap-1 text-xs h-6 px-2"
                        >
                          <Download className="h-3 w-3" />
                          {downloadFDSMutation.isPending ? "..." : "FDS"}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="text-xs text-gray-500 mt-2 italic">
                💡 Cliquez sur les headers pour trier les matières
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );

  return (
    <ResourcePageLayout
      title="Gestion des Matières"
      actions={{
        import: {
          show: true,
          importFunction: importMatieresFromFile,
          label: "Importer Matières",
          onSuccess: () => window.location.reload()
        },
        flush: {
          show: true,
          flushFunction: flushMatieres,
          confirmMessage: "Êtes-vous sûr de vouloir vider toutes les matières ? Cette action est irréversible.",
          label: "Vider toutes"
        },
        refresh: {
          show: true,
          onRefresh: () => window.location.reload(),
          isLoading: isLoading
        }
      }}
      queryKey={['matiere-data']}
      hasData={!!matieres && matieres.length > 0}
      emptyMessage="Aucune matière disponible"
      emptyDescription="Aucune matière disponible pour le moment. Importez un fichier CSV pour commencer."
    >
      {matieresContent}
    </ResourcePageLayout>
  );
} 