"use client";

import { useState, useMemo, useCallback, useEffect } from "react";
import { BarChart3 } from "lucide-react";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchAllBesoinData, flushBesoins, importBesoinsFromFile } from "@/services/besoin-service";
import { AnalyseService, AnalyseBesoinsResponse } from "@/services/analyse-service";
import { BesoinModel } from "@/model/besoin";
import { CouvertureParBesoin } from "@/model/analyse";
import { ResourcePageLayout } from "@/components/layouts/resource-page-layout";
import { DataTable, DataRow } from "@/components/data-table";
import { useRouter } from "next/navigation";
import { SearchFilter, FilterConfig } from "@/components/filters";

export default function AgendaTest() {
  const router = useRouter();
  const queryClient = useQueryClient();
  
  // États pour les filtres
  const [rechercheText, setRechercheText] = useState("");
  const [filtreEtat, setFiltreEtat] = useState<string>("tous");
  
  // Récupérer directement les données besoins depuis le service besoins (SANS analyse automatique)
  const { data: besoinData, isLoading, error, refetch } = useQuery({
    queryKey: ['besoin-data'],
    queryFn: async () => {
      const data = await fetchAllBesoinData();
      return data;
    },
    staleTime: Infinity, // Les données ne deviennent jamais obsolètes automatiquement
    gcTime: 1000 * 60 * 30, // Garder en cache pendant 30 minutes même si pas utilisé
    refetchOnMount: false, // Ne pas refetch au montage du composant
    refetchOnWindowFocus: false, // Ne pas refetch quand la fenêtre reprend le focus
    refetchOnReconnect: false, // Ne pas refetch lors de la reconnexion réseau
    retry: 1, // Réessayer seulement 1 fois en cas d'erreur
  });

  // Fonctions pour gérer la persistance des données d'analyse
  const getSavedCouvertureData = (): CouvertureParBesoin[] => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('besoins_couverture_data');
      return saved ? JSON.parse(saved) : [];
    }
    return [];
  };

  const saveCouvertureData = (data: CouvertureParBesoin[]) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('besoins_couverture_data', JSON.stringify(data));
    }
  };

  // État pour stocker les données de couverture par besoin (chargées manuellement)
  const [couvertureParBesoin, setCouvertureParBesoin] = useState<CouvertureParBesoin[]>([]);
  // État pour l'analyse manuelle
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [analysisError, setAnalysisError] = useState<string>("");
  // État pour les statistiques d'analyse
  const [analysisStats, setAnalysisStats] = useState<AnalyseBesoinsResponse['statistiques'] | null>(null);

  // Effet pour charger les données sauvegardées au montage
  useEffect(() => {
    const savedData = getSavedCouvertureData();
    if (savedData.length > 0) {
      setCouvertureParBesoin(savedData);
    }
  }, []);

  // Fonction pour lancer l'analyse manuellement avec le nouvel endpoint
  const handleAnalysis = useCallback(async () => {
    setIsAnalyzing(true);
    setAnalysisError("");
    
    try {
      console.log("🔬 [BESOINS] Lancement de l'analyse complète des besoins...");
      
      // Utiliser le nouvel endpoint /analyse/besoins
      const analyseResponse: AnalyseBesoinsResponse = await AnalyseService.analyserTousLesBesoins();
      
      console.log(`📊 [BESOINS] Analyse terminée:`, {
        total_besoins: analyseResponse.metadata.total_besoins,
        taux_couverture: analyseResponse.statistiques.taux_couverture,
        date_analyse: analyseResponse.metadata.date_analyse
      });
      
      // Mettre à jour les données de besoins avec les états de couverture calculés
      // Invalider le cache pour forcer un nouveau fetch des données mises à jour
      await queryClient.invalidateQueries({ queryKey: ['besoin-data'] });
      await refetch();
      
             // Créer des données de couverture fictives pour maintenir la compatibilité avec l'ancien système
       const couverturesCompatibles: CouvertureParBesoin[] = analyseResponse.besoins.map(besoin => ({
         besoin_id: besoin.id || '',
         quantite: besoin.quantite,
         echeance: besoin.echeance.toISOString(),
         etat_couverture: besoin.etat,
         quantite_disponible: besoin.etat === 'couvert' ? besoin.quantite : 0,
         pourcentage_couverture: besoin.etat === 'couvert' ? 100 : (besoin.etat === 'partiel' ? 50 : 0),
         stock_restant: besoin.etat === 'couvert' ? besoin.quantite : 0
       }));
      
             setCouvertureParBesoin(couverturesCompatibles);
       saveCouvertureData(couverturesCompatibles); // Sauvegarder dans localStorage
       
       // Sauvegarder les statistiques
       setAnalysisStats(analyseResponse.statistiques);
       
       console.log(`✅ [BESOINS] Analyse terminée avec ${couverturesCompatibles.length} besoins analysés`);
      
    } catch (err) {
      console.error('❌ [BESOINS] Erreur lors de l\'analyse:', err);
      setAnalysisError(err instanceof Error ? err.message : 'Erreur lors de l\'analyse');
    } finally {
      setIsAnalyzing(false);
    }
  }, [queryClient, refetch]);




  
  // Fonction pour obtenir l'état de couverture d'un besoin
  const getEtatCouverture = useCallback((besoin: BesoinModel): string => {
    // Si aucune analyse n'a été faite, utiliser l'état du besoin
    if (couvertureParBesoin.length === 0) {
      return besoin.etat;
    }

    // Logique de recherche de couverture (identique à avant)
    let couverture = couvertureParBesoin.find(c => c.besoin_id === besoin.id);
    
    if (couverture) {
      return couverture.etat_couverture;
    }
    
    const besoinDate = besoin.echeance.toISOString().split('T')[0];
    couverture = couvertureParBesoin.find(c => {
      const couvertureDate = c.echeance.split('T')[0];
      const dateMatch = couvertureDate === besoinDate;
      const codeMatch = c.besoin_id.includes(besoin.matiere.code_mp);
      const quantiteMatch = Math.abs(c.quantite - besoin.quantite) < 0.01;
      
      return codeMatch && dateMatch && quantiteMatch;
    });
    
    if (couverture) {
      return couverture.etat_couverture;
    }
    
    couverture = couvertureParBesoin.find(c => {
      const couvertureDate = c.echeance.split('T')[0];
      return c.besoin_id.includes(besoin.matiere.code_mp) && couvertureDate === besoinDate;
    });
    
    if (couverture) {
      return couverture.etat_couverture;
    }

    // Si aucune correspondance exacte n'est trouvée, retourner l'état original du besoin
    // au lieu d'emprunter l'état d'autres besoins du même code MP
    return besoin.etat;
  }, [couvertureParBesoin]);

  // Fonction pour filtrer les besoins
  const filteredBesoins = useMemo(() => {
    if (!besoinData) return [];
    
    // Filtrage des besoins
    return besoinData.filter((besoin) => {
      const etatCouverture = getEtatCouverture(besoin);
      
      const matchRecherche = rechercheText === "" || 
        besoin.matiere.code_mp.toLowerCase().includes(rechercheText.toLowerCase()) ||
        besoin.matiere.nom.toLowerCase().includes(rechercheText.toLowerCase()) ||
        etatCouverture.toLowerCase().includes(rechercheText.toLowerCase()) ||
        besoin.echeance.toLocaleDateString('fr-FR').includes(rechercheText.toLowerCase());
      
      const matchEtat = filtreEtat === "tous" || etatCouverture === filtreEtat;
      
      return matchRecherche && matchEtat;
    });
  }, [besoinData, rechercheText, filtreEtat, getEtatCouverture]);

  // Préparer les données pour le DataTable en utilisant les besoins filtrés
  const tableData: DataRow[] = useMemo(() => {
    if (!filteredBesoins) return [];
    
    return filteredBesoins.map((besoin: BesoinModel) => {
      const etatCouverture = getEtatCouverture(besoin);
      const couvertureTrouvee = couvertureParBesoin.find(c => c.besoin_id === besoin.id) ||
        couvertureParBesoin.find(c => {
          const besoinDate = besoin.echeance.toISOString().split('T')[0];
          const couvertureDate = c.echeance.split('T')[0];
          return c.besoin_id.includes(besoin.matiere.code_mp) && couvertureDate === besoinDate;
        });
      
      return {
        id: besoin.id,
        code_mp: besoin.matiere.code_mp,
        matiere: besoin.matiere.nom,
        quantite: besoin.quantite,
        echeance: besoin.echeance.toLocaleDateString('fr-FR'),
        echeance_sort: besoin.echeance, // Valeur Date pour le tri
        etat: etatCouverture,
        etat_source: couvertureTrouvee ? 'analyse' : 'besoin',
        // Données complètes pour les fonctions de rendu
        _besoin: besoin,
        _etat_couverture: etatCouverture
      };
    });
  }, [filteredBesoins, getEtatCouverture, couvertureParBesoin]);

  // Colonnes du tableau avec tri
  const columns = [
    {
      key: 'code_mp',
      label: 'Code MP',
      align: 'left' as const,
      sortable: true,
      sortType: 'string' as const,
      secondarySortKey: 'echeance_sort', // Tri secondaire par échéance
      secondarySortType: 'date' as const,
      secondarySortDirection: 'asc' as const // Échéance la plus récente en premier
    },
    {
      key: 'matiere',
      label: 'Matière',
      align: 'left' as const,
      sortable: true,
      sortType: 'string' as const
    },
    {
      key: 'quantite',
      label: 'Quantité',
      align: 'right' as const,
      sortable: true,
      sortType: 'number' as const
    },
    {
      key: 'echeance',
      label: 'Échéance',
      align: 'left' as const,
      sortable: true,
      sortType: 'date' as const,
      sortKey: 'echeance_sort', // Utiliser la valeur Date pour le tri
      render: (value: unknown) => {
        // Afficher la date formatée
        return value as string;
      }
    },
    {
      key: 'etat',
      label: 'État',
      align: 'left' as const,
      sortable: true,
      sortType: 'string' as const,
      render: (value: unknown, row: DataRow) => {
        const etat = value as string;
        const etatSource = row.etat_source as string;
        
        return (
          <div className="flex items-center gap-1">
            <span className={`px-1 py-0.5 rounded text-xs ${
              etat === 'couvert' ? 'bg-green-100 text-green-800' :
              etat === 'partiel' ? 'bg-yellow-100 text-yellow-800' :
              etat === 'non_couvert' ? 'bg-red-100 text-red-800' :
              'bg-blue-100 text-blue-800'
            }`}>
              {etat}
            </span>
            {etatSource === 'analyse' ? (
              <span className="text-xs text-green-600" title="État calculé par l'analyse">
                📊
              </span>
            ) : (
              <span className="text-xs text-gray-500" title="État du besoin original">
                📋
              </span>
            )}
          </div>
        );
      }
    },
    {
      key: 'actions',
      label: 'Actions',
      align: 'center' as const,
      sortable: false, // Les actions ne sont pas triables
      render: (value: unknown, row: DataRow) => {
        const besoin = row._besoin as BesoinModel;
        
        return (
          <Button
            size="sm"
            variant="outline"
            onClick={(e) => {
              e.stopPropagation();
              router.push(`/analyses?mp=${encodeURIComponent(besoin.matiere.code_mp)}`);
            }}
            className="flex items-center gap-1 text-xs h-6 px-2"
          >
            <BarChart3 size={12} />
            Analyser
          </Button>
        );
      }
    }
  ];

  // Fonction de rafraîchissement personnalisée
  const handleRefresh = useCallback(async () => {
    console.log("🔄 [BESOINS] Rafraîchissement manuel des données...");
    
    // Invalider le cache pour forcer un nouveau fetch
    await queryClient.invalidateQueries({ queryKey: ['besoin-data'] });
    
    // Forcer un nouveau fetch
    await refetch();
    
    // Réinitialiser les données d'analyse
    setCouvertureParBesoin([]);
    setAnalysisError("");
    setAnalysisStats(null);
    
    console.log("✅ [BESOINS] Données rafraîchies avec succès");
  }, [queryClient, refetch]);

  // Fonction de rafraîchissement après import
  const handleImportSuccess = useCallback(async () => {
    console.log("📥 [BESOINS] Import réussi, rafraîchissement des données...");
    await handleRefresh();
  }, [handleRefresh]);

  // Créer des filtres dynamiques basés sur les données
  const filterConfigs: FilterConfig[] = useMemo(() => {
    if (!besoinData) return [];
    
    const etatsUniques = [...new Set(besoinData.map(b => b.etat))].filter(Boolean).sort();
    
    return [
      {
        key: "etat",
        label: "État",
        options: etatsUniques.map(e => ({ value: e, label: e }))
      }
    ];
  }, [besoinData]);
  
  const filterValues = {
    etat: filtreEtat
  };
  
  const handleFilterChange = (filterKey: string, value: string) => {
    if (filterKey === "etat") {
      setFiltreEtat(value);
    }
  };



  // Afficher un état de chargement
  if (isLoading) {
    return (
      <div className="space-y-6">
        <LoadingSpinner text="Chargement des données de besoins..." />
      </div>
    );
  }

  // Gérer les erreurs
  if (error) {
    return (
      <div className="space-y-6">
        <Alert variant="destructive">
          <AlertTitle>Erreur de chargement</AlertTitle>
          <AlertDescription>
            Impossible de charger les données de besoins. {error instanceof Error ? error.message : 'Erreur inconnue'}
          </AlertDescription>
        </Alert>
      </div>
    );
  }
  
  // Contenu principal de la page (tableau avec filtres et bouton d'analyse)
  const besoinsContent = (
    <div className="space-y-6">
      {/* Section des filtres */}
      <SearchFilter
        searchValue={rechercheText}
        onSearchChange={setRechercheText}
        searchPlaceholder="Rechercher un besoin..."
        filters={filterConfigs}
        filterValues={filterValues}
        onFilterChange={handleFilterChange}
        onRefresh={handleRefresh}
                 resultCount={filteredBesoins?.length || 0}
        resultLabel="besoin(s) trouvé(s)"
        isLoading={isLoading}
      />
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-xl font-semibold">Liste des Besoins Opérationnels</h2>
            <p className="text-gray-600">Vue détaillée des besoins - cliquez sur &quot;Analyse&quot; pour calculer la couverture</p>
            <p className="text-sm text-blue-600 mt-1">💡 Cliquez sur les en-têtes de colonnes pour trier (Code MP, Matière, Quantité, Échéance, État)</p>
          </div>
          
          {/* Indicateur d'analyse */}
          {couvertureParBesoin.length > 0 && (
            <div className="text-sm text-green-600 flex items-center gap-2">
              📊 Analyse effectuée ({couvertureParBesoin.length} données de couverture)
              {analysisStats && (
                <span className="ml-2 text-xs bg-green-100 px-2 py-1 rounded">
                  Taux: {analysisStats.taux_couverture.toFixed(1)}% | 
                  Couverts: {analysisStats.couvert} | 
                  Non couverts: {analysisStats.non_couvert}
                </span>
              )}
            </div>
          )}
        </div>
        
        {/* Message d'erreur d'analyse */}
        {analysisError && (
          <Alert variant="destructive" className="mb-4">
            <AlertTitle>Erreur d&apos;analyse</AlertTitle>
            <AlertDescription>{analysisError}</AlertDescription>
          </Alert>
        )}
        
        {tableData && tableData.length > 0 ? (
          <DataTable
            columns={columns}
            data={tableData}
            showAnalysisButton={true}
            onAnalysisClick={handleAnalysis}
            isAnalysisLoading={isAnalyzing}
            analysisButtonLabel="Analyser la couverture"
            defaultSortColumn="echeance"
            defaultSortDirection="asc"
            caption="💡 Cliquez sur le bouton 'Analyser la couverture' pour calculer l'état de couverture de tous les besoins. Cliquez sur les en-têtes de colonnes pour trier."
          />
        ) : (
          <p className="text-gray-500">Aucun besoin disponible</p>
        )}
      </div>
    </div>
  );

  return (
    <ResourcePageLayout
      title="Gestion des Besoins Opérationnels"
      actions={{
        add: {
          show: true,
          onClick: () => router.push("/besoins/create"),
          label: "Nouveau besoin"
        },
        import: {
          show: true,
          importFunction: importBesoinsFromFile,
          label: "Importer Besoins",
          onSuccess: () => handleImportSuccess()
        },
        flush: {
          show: true,
          flushFunction: flushBesoins,
          confirmMessage: "Êtes-vous sûr de vouloir vider tous les besoins ? Cette action est irréversible.",
          label: "Vider tous"
        },
        refresh: {
          show: true,
          onRefresh: () => handleRefresh(),
          isLoading: isLoading
        }
      }}
      queryKey={['besoin-data']}
      hasData={!!besoinData && besoinData.length > 0}
      emptyMessage="Aucun besoin disponible"
      emptyDescription="Aucun besoin disponible pour le moment. Importez un fichier CSV pour commencer."
    >
      {besoinsContent}
    </ResourcePageLayout>
  );
} 
