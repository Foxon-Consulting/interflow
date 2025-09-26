"use client";

import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Package, Truck, ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react";

import { EtatReception, TypeReception } from "@/model/reception";
import { ResourcePageLayout } from "@/components/layouts/resource-page-layout";
import { importReceptionsFromFile, flushReceptions } from "@/services/reception-service";
import { SearchFilter, FilterConfig } from "@/components/filters";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchAllReceptionData } from "@/services/reception-service";


const getTypeIcon = (type: TypeReception) => {
  switch (type) {
    case TypeReception.EXTERNE:
      return <Truck className="h-4 w-4" />;
    case TypeReception.INTERNE:
      return <Package className="h-4 w-4" />;
    default:
      return <Package className="h-4 w-4" />;
  }
};


export default function ReceptionsPage() {
  const queryClient = useQueryClient();

  // Récupérer les données de réception avec React Query optimisé
  const { data: receptions, isLoading, refetch } = useQuery({
    queryKey: ['reception-data'],
    queryFn: fetchAllReceptionData,
    staleTime: Infinity, // Les données ne deviennent jamais obsolètes automatiquement
    gcTime: 1000 * 60 * 30, // Garder en cache pendant 30 minutes
    refetchOnMount: false, // Ne pas refetch au montage
    refetchOnWindowFocus: false, // Ne pas refetch au focus
    refetchOnReconnect: false, // Ne pas refetch à la reconnexion
    retry: 1, // Réessayer seulement 1 fois en cas d'erreur
  });

  // Fonction de rafraîchissement personnalisée
  const handleRefresh = async () => {
    console.log("🔄 [RECEPTIONS] Rafraîchissement manuel des données...");
    await queryClient.invalidateQueries({ queryKey: ['reception-data'] });
    await refetch();
    console.log("✅ [RECEPTIONS] Données rafraîchies avec succès");
  };

  // Fonction de rafraîchissement après import
  const handleImportSuccess = async () => {
    console.log("📥 [RECEPTIONS] Import réussi, rafraîchissement des données...");
    await handleRefresh();
  };
  
  // États pour les filtres
  const [rechercheText, setRechercheText] = useState("");
  const [filtreType, setFiltreType] = useState<TypeReception | "tous">("tous");
  const [filtreEtat, setFiltreEtat] = useState<EtatReception | "tous">("tous");
  
  // États pour le tri
  const [sortField, setSortField] = useState<string>('date_reception');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  
  // Configuration des filtres
  const filterConfigs: FilterConfig[] = [
    {
      key: "type",
      label: "Type",
      options: [
        { value: TypeReception.EXTERNE, label: "Externe" },
        { value: TypeReception.INTERNE, label: "Interne" }
      ]
    },
    {
      key: "etat",
      label: "État",
      options: [
        { value: EtatReception.EN_COURS, label: "En cours" },
        { value: EtatReception.TERMINEE, label: "Terminée" },
        { value: EtatReception.ANNULEE, label: "Annulée" },
        { value: EtatReception.RELACHE, label: "Relâché" },
        { value: EtatReception.EN_ATTENTE, label: "En attente" }
      ]
    }
  ];
  
  const filterValues = {
    type: filtreType,
    etat: filtreEtat
  };
  
  const handleFilterChange = (filterKey: string, value: string) => {
    if (filterKey === "type") {
      setFiltreType(value as TypeReception | "tous");
    } else if (filterKey === "etat") {
      setFiltreEtat(value as EtatReception | "tous");
    }
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

  // Filtrage et tri des réceptions
  const receptionsTriees = useMemo(() => {
    if (!receptions) return [];
    
    // Filtrage des réceptions
    const receptionsFiltrees = receptions.filter((reception) => {
      const matchRecherche = rechercheText === "" || 
        reception.matiere.nom.toLowerCase().includes(rechercheText.toLowerCase()) ||
        reception.matiere.code_mp.toLowerCase().includes(rechercheText.toLowerCase()) ||
        reception.lot.toLowerCase().includes(rechercheText.toLowerCase()) ||
        (reception.fournisseur && reception.fournisseur.toLowerCase().includes(rechercheText.toLowerCase())) ||
        (reception.ordre && reception.ordre.toLowerCase().includes(rechercheText.toLowerCase()));
      
      const matchType = filtreType === "tous" || reception.type === filtreType;
      const matchEtat = filtreEtat === "tous" || reception.etat === filtreEtat;
      
      return matchRecherche && matchType && matchEtat;
    });
    
    // Tri des réceptions filtrées
    return receptionsFiltrees.sort((a, b) => {
      let aValue: string | number | boolean | Date | null | undefined;
      let bValue: string | number | boolean | Date | null | undefined;
      
      switch (sortField) {
        case 'date_reception':
          aValue = a.date_reception ? new Date(a.date_reception) : null;
          bValue = b.date_reception ? new Date(b.date_reception) : null;
          break;
        case 'date_creation':
          aValue = a.date_creation;
          bValue = b.date_creation;
          break;
        case 'matiere':
          aValue = a.matiere.nom;
          bValue = b.matiere.nom;
          break;
        case 'code_mp':
          aValue = a.matiere.code_mp;
          bValue = b.matiere.code_mp;
          break;
        case 'quantite':
          aValue = a.quantite;
          bValue = b.quantite;
          break;

        case 'type':
          aValue = a.type;
          bValue = b.type;
          break;
        case 'etat':
          aValue = a.etat;
          bValue = b.etat;
          break;
        case 'fournisseur':
          aValue = a.fournisseur || '';
          bValue = b.fournisseur || '';
          break;
        case 'ordre':
          aValue = a.ordre || '';
          bValue = b.ordre || '';
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
  }, [receptions, sortField, sortDirection, rechercheText, filtreType, filtreEtat]);



  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Chargement des réceptions...</p>
        </div>
      </div>
    );
  }



  // Contenu principal de la page (filtres, liste et générateur de bon)
  const receptionsContent = (
    <div className="space-y-6">
      {/* Section des filtres */}
      <SearchFilter
        searchValue={rechercheText}
        onSearchChange={setRechercheText}
        searchPlaceholder="Rechercher une réception..."
        filters={filterConfigs}
        filterValues={filterValues}
        onFilterChange={handleFilterChange}
        onRefresh={handleRefresh}
        resultCount={receptionsTriees.length}
        resultLabel="réception(s) trouvée(s)"
        isLoading={isLoading}
      />




      {/* Liste des réceptions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="h-5 w-5" />
            Liste des Réceptions
          </CardTitle>
        </CardHeader>
        <CardContent>
          {receptionsTriees.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground">Aucune réception trouvée</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-200">
                <thead>
                  <tr className="bg-gray-50">
                    <SortableHeader field="date_reception">Date Réception</SortableHeader>
                    <SortableHeader field="matiere">Matière</SortableHeader>
                    <SortableHeader field="code_mp">Code MP</SortableHeader>
                    <SortableHeader field="quantite">Quantité</SortableHeader>
                    <SortableHeader field="type">Type</SortableHeader>
                    <SortableHeader field="etat">État</SortableHeader>
                    <SortableHeader field="fournisseur">Fournisseur/Ordre</SortableHeader>
                    <th className="border border-gray-200 px-2 py-1 text-center text-sm">Seveso</th>
                    <th className="border border-gray-200 px-2 py-1 text-center text-sm">Qualification</th>
                  </tr>
                </thead>
                <tbody>
                  {receptionsTriees.map((reception) => (
                    <tr key={reception.id} className="hover:bg-gray-50">
                      <td className="border border-gray-200 px-2 py-1 text-sm">
                        {reception.date_reception ? 
                          new Date(reception.date_reception).toLocaleDateString('fr-FR') : 
                          'Non définie'
                        }
                      </td>
                      <td className="border border-gray-200 px-2 py-1">
                        <div>
                          <div className="font-medium text-sm">{reception.matiere.nom}</div>
                          <div className="text-xs text-muted-foreground">
                            Créée le {reception.date_creation.toLocaleDateString('fr-FR')}
                          </div>
                        </div>
                      </td>
                      <td className="border border-gray-200 px-2 py-1 text-sm">{reception.matiere.code_mp}</td>
                      <td className="border border-gray-200 px-2 py-1 text-right text-sm">
                        {reception.quantite} {reception.udm || "unité(s)"}
                      </td>
                      <td className="border border-gray-200 px-2 py-1">
                        <div className="flex items-center gap-1">
                          {getTypeIcon(reception.type)}
                          <span className="text-xs">
                            {reception.type === TypeReception.EXTERNE ? 'Externe' : 'Interne'}
                          </span>
                        </div>
                      </td>
                      <td className="border border-gray-200 px-2 py-1">
                        <span className={`px-1 py-0.5 rounded text-xs ${
                          reception.etat === EtatReception.TERMINEE ? 'bg-green-100 text-green-800' :
                          reception.etat === EtatReception.EN_COURS ? 'bg-blue-100 text-blue-800' :
                          reception.etat === EtatReception.RELACHE ? 'bg-yellow-100 text-yellow-800' :
                          reception.etat === EtatReception.EN_ATTENTE ? 'bg-orange-100 text-orange-800' :
                          reception.etat === EtatReception.ANNULEE ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {reception.etat}
                        </span>
                      </td>
                      <td className="border border-gray-200 px-2 py-1 text-sm">
                        {reception.type === TypeReception.EXTERNE 
                          ? reception.fournisseur || "Non spécifié"
                          : reception.ordre || "Non spécifié"
                        }
                      </td>
                      <td className="border border-gray-200 px-2 py-1 text-center">
                        {reception.matiere.seveso ? (
                          <span className="px-1 py-0.5 bg-red-100 text-red-800 text-xs rounded-full">SEVESO</span>
                        ) : (
                          <span className="px-1 py-0.5 bg-gray-100 text-gray-800 text-xs rounded-full">Non</span>
                        )}
                      </td>
                      <td className="border border-gray-200 px-2 py-1 text-center">
                        {reception.qualification ? (
                          <span className="px-1 py-0.5 bg-green-100 text-green-800 text-xs rounded-full">✓ Qualifié</span>
                        ) : (
                          <span className="px-1 py-0.5 bg-gray-100 text-gray-800 text-xs rounded-full">Non</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="text-xs text-gray-500 mt-2 italic">
                💡 Cliquez sur les headers pour trier les réceptions
              </p>
            </div>
          )}
        </CardContent>
      </Card>


    </div>
  );

  return (
    <ResourcePageLayout
      title="Gestion des Réceptions"
      actions={{
        import: {
          show: true,
          importFunction: importReceptionsFromFile,
          label: "Importer Réceptions",
          onSuccess: handleImportSuccess
        },
        flush: {
          show: true,
          flushFunction: flushReceptions,
          confirmMessage: "Êtes-vous sûr de vouloir vider toutes les réceptions ? Cette action est irréversible.",
          label: "Vider toutes"
        },
        refresh: {
          show: true,
          onRefresh: handleRefresh,
          isLoading: isLoading
        }
      }}
      queryKey={['reception-data']}
      hasData={!!receptions && receptions.length > 0}
      emptyMessage="Aucune réception disponible"
      emptyDescription="Aucune réception disponible pour le moment. Importez un fichier CSV pour commencer."
    >
      {receptionsContent}
    </ResourcePageLayout>
  );
} 