"use client"

import { useState, useMemo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchAllStockData, importStocksFromFile, flushStocks } from "@/services/stock-service";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { ErrorMessage } from "@/components/ui/error-message";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import { ResourcePageLayout } from "@/components/layouts/resource-page-layout";
import { useRouter } from "next/navigation";
import { BarChart3, Truck, ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react";
import { Stock } from "@/model/stock";
import { SearchFilter, FilterConfig } from "@/components/filters";

export default function StocksPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  
  // États pour les filtres
  const [rechercheText, setRechercheText] = useState("");
  const [filtreMagasin, setFiltreMagasin] = useState<string>("tous");
  const [filtreDivision, setFiltreDivision] = useState<string>("tous");
  const [filtreStatutLot, setFiltreStatutLot] = useState<string>("tous");
  
  // États pour le tri
  const [sortField, setSortField] = useState<string>('code_mp');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  
  // Récupérer les données de stock avec React Query
  const { data: stockData, isLoading, error, refetch } = useQuery({
    queryKey: ['stock-data'],
    queryFn: fetchAllStockData,
    staleTime: Infinity, // Les données ne deviennent jamais obsolètes automatiquement
    gcTime: 1000 * 60 * 30, // Garder en cache pendant 30 minutes
    refetchOnMount: false, // Ne pas refetch au montage
    refetchOnWindowFocus: false, // Ne pas refetch au focus
    refetchOnReconnect: false, // Ne pas refetch à la reconnexion
    retry: 1, // Réessayer seulement 1 fois en cas d'erreur
  });

  // Fonction de rafraîchissement personnalisée
  const handleRefresh = async () => {
    console.log("🔄 [STOCKS] Rafraîchissement manuel des données...");
    await queryClient.invalidateQueries({ queryKey: ['stock-data'] });
    await refetch();
    console.log("✅ [STOCKS] Données rafraîchies avec succès");
  };

  // Fonction de rafraîchissement après import
  const handleImportSuccess = async () => {
    console.log("📥 [STOCKS] Import réussi, rafraîchissement des données...");
    await handleRefresh();
  };
  
  // Créer des filtres dynamiques basés sur les données
  const filterConfigs: FilterConfig[] = useMemo(() => {
    if (!stockData) return [];
    
    const magasinsUniques = [...new Set(stockData.map(s => s.magasin))].filter(Boolean).sort();
    const divisionsUniques = [...new Set(stockData.map(s => s.division))].filter(Boolean).sort();
    const statutsUniques = [...new Set(stockData.map(s => s.statut_lot))].filter(Boolean).sort();
    
    return [
      {
        key: "magasin",
        label: "Magasin",
        options: magasinsUniques.map(m => ({ value: m, label: m }))
      },
      {
        key: "division", 
        label: "Division",
        options: divisionsUniques.map(d => ({ value: d, label: d }))
      },
      {
        key: "statutLot",
        label: "Statut Lot",
        options: statutsUniques.map(s => ({ value: s, label: s }))
      }
    ];
  }, [stockData]);
  
  const filterValues = {
    magasin: filtreMagasin,
    division: filtreDivision,
    statutLot: filtreStatutLot
  };
  
  const handleFilterChange = (filterKey: string, value: string) => {
    if (filterKey === "magasin") {
      setFiltreMagasin(value);
    } else if (filterKey === "division") {
      setFiltreDivision(value);
    } else if (filterKey === "statutLot") {
      setFiltreStatutLot(value);
    }
  };

  // Fonction pour naviguer vers la page Analyses avec le code MP
  const navigateToAnalyses = (codeMp: string) => {
    // console.log(`🔍 [NAVIGATION] Navigation vers Analyses avec code MP: ${codeMp}`);
    // Sauvegarder le code MP dans localStorage pour la page Analyses
    if (typeof window !== 'undefined') {
      localStorage.setItem('analyses_code_mp', codeMp);
    }
    // Naviguer vers la page Analyses
    router.push('/analyses');
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

  // Fonction pour filtrer et trier les stocks
  const sortedStocks = useMemo(() => {
    if (!stockData) return [];
    
    // Filtrage des stocks
    const stocksFiltres = stockData.filter((stock) => {
      const matchRecherche = rechercheText === "" || 
        (stock.matiere?.nom && stock.matiere.nom.toLowerCase().includes(rechercheText.toLowerCase())) ||
        (stock.matiere?.code_mp && stock.matiere.code_mp.toLowerCase().includes(rechercheText.toLowerCase())) ||
        stock.libelle_article.toLowerCase().includes(rechercheText.toLowerCase()) ||
        stock.magasin.toLowerCase().includes(rechercheText.toLowerCase()) ||
        stock.division.toLowerCase().includes(rechercheText.toLowerCase()) ||
        (stock.lot_fournisseur && stock.lot_fournisseur.toLowerCase().includes(rechercheText.toLowerCase())) ||
        stock.emplacement.toLowerCase().includes(rechercheText.toLowerCase());
      
      const matchMagasin = filtreMagasin === "tous" || stock.magasin === filtreMagasin;
      const matchDivision = filtreDivision === "tous" || stock.division === filtreDivision;
      const matchStatutLot = filtreStatutLot === "tous" || stock.statut_lot === filtreStatutLot;
      
      return matchRecherche && matchMagasin && matchDivision && matchStatutLot;
    });
    
    // Tri des stocks filtrés
    return stocksFiltres.sort((a, b) => {
      let aValue: string | number | boolean | Date | null | undefined;
      let bValue: string | number | boolean | Date | null | undefined;
      
      switch (sortField) {
        case 'code_mp':
          aValue = a.matiere?.code_mp || '';
          bValue = b.matiere?.code_mp || '';
          break;
        case 'matiere':
          aValue = a.matiere?.nom || a.libelle_article || '';
          bValue = b.matiere?.nom || b.libelle_article || '';
          break;
        case 'magasin':
          aValue = a.magasin || '';
          bValue = b.magasin || '';
          break;
        case 'division':
          aValue = a.division || '';
          bValue = b.division || '';
          break;
        case 'lot':
          aValue = a.lot_fournisseur || '';
          bValue = b.lot_fournisseur || '';
          break;
        case 'quantite':
          aValue = a.quantite || 0;
          bValue = b.quantite || 0;
          break;
        case 'statut':
          aValue = a.statut_lot || '';
          bValue = b.statut_lot || '';
          break;
        case 'emplacement':
          aValue = a.emplacement || '';
          bValue = b.emplacement || '';
          break;
        case 'date_creation':
          aValue = a.date_creation ? new Date(a.date_creation) : null;
          bValue = b.date_creation ? new Date(b.date_creation) : null;
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
  }, [stockData, sortField, sortDirection, rechercheText, filtreMagasin, filtreDivision, filtreStatutLot]);

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

  // Fonction pour créer un rapatriement à partir d'un stock externe
  const createRappatriementFromStock = (stock: Stock) => {
    // Sauvegarder les informations du stock dans localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('rappatriement_stock_data', JSON.stringify({
        code_prdt: stock.matiere?.code_mp || '',
        designation_prdt: stock.matiere?.nom || stock.libelle_article || '',
        lot: stock.du || '',
        poids_net: stock.quantite || 0,
        type_emballage: 'carton', // Valeur par défaut
        stock_solde: false,
        nb_contenants: 1, // Valeur par défaut
        nb_palettes: 1, // Valeur par défaut
        dimension_palettes: '',
        code_onu: 'SANS DANGER',
        grp_emballage: '',
        po: ''
      }));
    }
    // Naviguer vers la page de création de rapatriement
    router.push('/rappatriements/create');
  };

  // Afficher un état de chargement
  if (isLoading) {
    return (
      <div className="container py-10">
        <LoadingSpinner text="Chargement des données de stock..." />
      </div>
    );
  }

  // Gérer les erreurs
  if (error) {
    return (
      <div className="container py-10">
        <ErrorMessage 
          error={error} 
          resetFn={() => refetch()} 
        />
      </div>
    );
  }

  // Contenu principal de la page (tableau des stocks)
  const stocksContent = (
    <div className="space-y-6">
      {/* Section des filtres */}
      <SearchFilter
        searchValue={rechercheText}
        onSearchChange={setRechercheText}
        searchPlaceholder="Rechercher un stock..."
        filters={filterConfigs}
        filterValues={filterValues}
        onFilterChange={handleFilterChange}
        onRefresh={handleRefresh}
        resultCount={sortedStocks?.length || 0}
        resultLabel="stock(s) trouvé(s)"
        isLoading={isLoading}
      />
      
      <Card>
        <CardHeader>
          <CardTitle>Stocks INCONNUs</CardTitle>
          <CardDescription>Stocks internes et externes</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border border-gray-200">
              <thead>
                <tr className="bg-gray-50">
                  <SortableHeader field="code_mp">Code MP</SortableHeader>
                  <SortableHeader field="matiere">Matière</SortableHeader>
                  <SortableHeader field="magasin">Magasin</SortableHeader>
                  <SortableHeader field="division">Division</SortableHeader>
                  <SortableHeader field="lot">Lot</SortableHeader>
                  <SortableHeader field="quantite">Quantité</SortableHeader>
                  <SortableHeader field="statut">Statut</SortableHeader>
                  <SortableHeader field="emplacement">Emplacement</SortableHeader>
                  <SortableHeader field="date_creation">Date Creation</SortableHeader>
                  <th className="border border-gray-200 px-2 py-1 text-center text-sm">Actions</th>
                </tr>
              </thead>
              <tbody>
                {sortedStocks?.map((stock) => (
                  <tr key={stock.id} className="hover:bg-gray-50">
                    <td className="border border-gray-200 px-2 py-1 text-sm">{stock.matiere?.code_mp || 'N/A'}</td>
                    <td className="border border-gray-200 px-2 py-1 text-sm">{stock.matiere?.nom || stock.libelle_article}</td>
                    <td className="border border-gray-200 px-2 py-1 text-sm">{stock.magasin}</td>
                    <td className="border border-gray-200 px-2 py-1 text-sm">{stock.division}</td>
                    <td className="border border-gray-200 px-2 py-1 text-sm">
                      {stock.lot_fournisseur && stock.lot_fournisseur !== '0' && stock.lot_fournisseur !== 'NaN' && stock.lot_fournisseur !== 'nan' ? stock.lot_fournisseur : 'N/A'}
                    </td>
                    <td className="border border-gray-200 px-2 py-1 text-right text-sm">
                      {stock.quantite} {stock.udm}
                    </td>
                    <td className="border border-gray-200 px-2 py-1">
                      <span className={`px-1 py-0.5 rounded text-xs ${
                        stock.statut_lot === 'Actif' ? 'bg-green-100 text-green-800' :
                        stock.statut_lot === 'Épuisé' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {stock.statut_lot}
                      </span>
                    </td>
                    <td className="border border-gray-200 px-2 py-1 text-sm">
                      {stock.emplacement}
                    </td>
                    <td className="border border-gray-200 px-2 py-1 text-sm">
                      {stock.date_creation ? format(new Date(stock.date_creation), "dd/MM/yyyy", { locale: fr }) : 'N/A'}
                    </td>
                    <td className="border border-gray-200 px-2 py-1 text-center">
                                              <div className="flex flex-col gap-0.5">
                          {stock.matiere?.code_mp && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => navigateToAnalyses(stock.matiere!.code_mp)}
                              className="flex items-center gap-1 text-xs h-6 px-2"
                            >
                              <BarChart3 size={12} />
                              Analyser
                            </Button>
                          )}
                          {stock.magasin?.startsWith('EX') && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => createRappatriementFromStock(stock)}
                              className="flex items-center gap-1 text-blue-600 hover:text-blue-700 text-xs h-6 px-2"
                            >
                              <Truck size={12} />
                              Rapatrier
                            </Button>
                          )}
                        </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="text-xs text-gray-500 mt-2">
              Inventaire au {new Date().toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })}
            </p>
            <p className="text-xs text-gray-500 mt-1 italic">
              💡 Cliquez sur le bouton &quot;Analyser&quot; pour voir l&apos;analyse de couverture de cette matière
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  return (
    <ResourcePageLayout
      title="Gestion des Stocks"
      actions={{
        import: {
          show: true,
          importFunction: importStocksFromFile,
          label: "Importer Stocks",
          onSuccess: handleImportSuccess
        },
        flush: {
          show: true,
          flushFunction: flushStocks,
          confirmMessage: "Êtes-vous sûr de vouloir vider tous les stocks ? Cette action est irréversible.",
          label: "Vider tous"
        },
        refresh: {
          show: true,
          onRefresh: handleRefresh,
          isLoading: isLoading
        }
      }}
      queryKey={['stock-data']}
      hasData={!!stockData && stockData.length > 0}
      emptyMessage="Aucun stock disponible"
      emptyDescription="Aucun stock disponible pour le moment. Importez un fichier CSV pour commencer."
    >
      {stocksContent}
    </ResourcePageLayout>
  );
} 