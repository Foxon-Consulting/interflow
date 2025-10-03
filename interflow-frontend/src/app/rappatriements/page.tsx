"use client";

import { useState, useMemo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { ErrorMessage } from "@/components/ui/error-message";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import { Truck, Package, Calendar, MapPin, User, TestTube, FileDown } from "lucide-react";
import { TypeEmballage, ProduitRappatriement, Rappatriement } from "@/model/rappatriement";
import { ResourcePageLayout } from "@/components/layouts/resource-page-layout";
import { Button } from "@/components/ui/button";
import { SearchFilter, FilterConfig } from "@/components/filters";
import { fetchAllRappatriementData, importRappatriementsFromFile, flushRappatriements } from "@/services/rappatriement-service";
import { RappatriementExportService } from "@/services/rappatriement-export-service";
import { useRouter } from "next/navigation";

// Fonction utilitaire pour calculer le poids total d'un rapatriement
const calculerPoidsTotal = (produits: ProduitRappatriement[]) => {
  return produits.reduce((total, produit) => total + (produit.poids_net || 0), 0);
};

// Fonction utilitaire pour calculer le nombre total de palettes
const calculerPalettesTotal = (produits: ProduitRappatriement[]) => {
  return produits.reduce((total, produit) => total + (produit.nb_palettes || 0), 0);
};

// Fonction utilitaire pour calculer le nombre total de contenants
const calculerContenantsTotal = (produits: ProduitRappatriement[]) => {
  return produits.reduce((total, produit) => total + (produit.nb_contenants || 0), 0);
};

export default function RappatriementsPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  
  // Récupérer les données de rapatriement avec React Query
  const { data: rapatriementData, isLoading, error, refetch } = useQuery({
    queryKey: ['rappatriement-data'],
    queryFn: fetchAllRappatriementData,
    staleTime: Infinity, // Les données ne deviennent jamais obsolètes automatiquement
    gcTime: 1000 * 60 * 30, // Garder en cache pendant 30 minutes
    refetchOnMount: false, // Ne pas refetch au montage
    refetchOnWindowFocus: false, // Ne pas refetch au focus
    refetchOnReconnect: false, // Ne pas refetch à la reconnexion
    retry: 1, // Réessayer seulement 1 fois en cas d'erreur
  });

  // Fonction de rafraîchissement personnalisée
  const handleRefresh = async () => {
    console.log("🔄 [RAPPATRIEMENTS] Rafraîchissement manuel des données...");
    await queryClient.invalidateQueries({ queryKey: ['rappatriement-data'] });
    await refetch();
    console.log("✅ [RAPPATRIEMENTS] Données rafraîchies avec succès");
  };

  // Fonction de rafraîchissement après import
  const handleImportSuccess = async () => {
    console.log("📥 [RAPPATRIEMENTS] Import réussi, rafraîchissement des données...");
    await handleRefresh();
  };
  
  // Fonction d'export d'un rappatriement en XLSX
  const handleExport = async (rappatriement: Rappatriement) => {
    try {
      console.log("📄 [RAPPATRIEMENTS] Export du rappatriement:", rappatriement.numero_transfert);
      await RappatriementExportService.exportToXLSX(rappatriement);
    } catch (error) {
      console.error("❌ [RAPPATRIEMENTS] Erreur lors de l'export:", error);
      alert("Erreur lors de l'export du fichier. Voir la console pour plus de détails.");
    }
  };

  
  // États pour les filtres
  const [rechercheText, setRechercheText] = useState("");
  const [filtreTypeEmballage, setFiltreTypeEmballage] = useState<TypeEmballage | "tous">("tous");
  
  // Configuration des filtres
  const filterConfigs: FilterConfig[] = [
    {
      key: "typeEmballage",
      label: "Type d'emballage",
      options: [
        { value: TypeEmballage.CARTON, label: "Carton" },
        { value: TypeEmballage.SAC, label: "Sac" },
        { value: TypeEmballage.CONTENEUR, label: "Conteneur" },
        { value: TypeEmballage.AUTRE, label: "Autre" }
      ],
      placeholder: "Tous les types"
    }
  ];
  
  const filterValues = {
    typeEmballage: filtreTypeEmballage
  };
  
  const handleFilterChange = (filterKey: string, value: string) => {
    if (filterKey === "typeEmballage") {
      setFiltreTypeEmballage(value as TypeEmballage | "tous");
    }
  };

  // Filtrage des rapatriements
  const rapatriementsFiltres = useMemo(() => {
    if (!rapatriementData || !Array.isArray(rapatriementData)) {
      return [];
    }
    
    const filtered = rapatriementData.filter((item: Rappatriement) => {
      const matchRecherche = rechercheText === "" || 
        item.numero_transfert.toLowerCase().includes(rechercheText.toLowerCase()) ||
        item.responsable_diffusion.toLowerCase().includes(rechercheText.toLowerCase()) ||
        (item.contacts && item.contacts.toLowerCase().includes(rechercheText.toLowerCase())) ||
        item.produits.some((produit: ProduitRappatriement) => 
          produit.code_prdt.toLowerCase().includes(rechercheText.toLowerCase()) ||
          produit.designation_prdt.toLowerCase().includes(rechercheText.toLowerCase()) ||
          produit.lot.toLowerCase().includes(rechercheText.toLowerCase())
        );
      
      const matchTypeEmballage = filtreTypeEmballage === "tous" || 
        item.produits.some((produit: ProduitRappatriement) => produit.type_emballage === filtreTypeEmballage);
      
      return matchRecherche && matchTypeEmballage;
    });
    
    return filtered;
  }, [rapatriementData, rechercheText, filtreTypeEmballage]);

  // Afficher un état de chargement
  if (isLoading) {
    return (
      <div className="container py-10">
        <LoadingSpinner text="Chargement des rapatriements..." />
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

  // Vérifier que les données sont valides
  if (!rapatriementData || !Array.isArray(rapatriementData)) {
    // console.warn("⚠️ [RAPPATRIEMENTS-PAGE] Données invalides:", rapatriementData);
    return (
      <div className="container py-10">
        <Card className="bg-red-50 border-red-200">
          <CardHeader>
            <CardTitle className="text-red-800">Erreur de données</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-red-700">
              Les données reçues ne sont pas dans le format attendu. 
              Type: {typeof rapatriementData}, Est un tableau: {Array.isArray(rapatriementData) ? 'Oui' : 'Non'}
            </p>
            <button 
              onClick={handleRefresh}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Réessayer
            </button>
          </CardContent>
        </Card>
      </div>
    );
  }



  // Contenu principal de la page (filtres et liste des rapatriements)
  const rapatriementsContent = (
    <div className="space-y-6">
      


      {/* Section des filtres */}
      <SearchFilter
        searchValue={rechercheText}
        onSearchChange={setRechercheText}
        searchPlaceholder="Rechercher un rapatriement..."
        filters={filterConfigs}
        filterValues={filterValues}
        onFilterChange={handleFilterChange}
        onRefresh={handleRefresh}
        resultCount={rapatriementsFiltres.length}
        resultLabel="rapatriement(s) trouvé(s)"
        isLoading={isLoading}
      />

      {/* Liste des rapatriements */}
      <div className="space-y-6">
        {rapatriementsFiltres.map((rappatriement) => (
          <Card key={rappatriement.numero_transfert} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Truck className="h-5 w-5 text-blue-600" />
                    Transfert {rappatriement.numero_transfert}
                  </CardTitle>
                  <CardDescription className="flex items-center gap-4 mt-2">
                    <span className="flex items-center gap-1">
                      <User className="h-4 w-4" />
                      {rappatriement.responsable_diffusion}
                    </span>
                    {rappatriement.date_demande && (
                      <span className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        Demande: {format(rappatriement.date_demande, "dd/MM/yyyy", { locale: fr })}
                      </span>
                    )}
                    {rappatriement.date_reception_souhaitee && (
                      <span className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        Réception souhaitée: {format(rappatriement.date_reception_souhaitee, "dd/MM/yyyy", { locale: fr })}
                      </span>
                    )}
                    {rappatriement.date_derniere_maj && (
                      <span className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        Dernière MAJ: {format(rappatriement.date_derniere_maj, "dd/MM/yyyy HH:mm", { locale: fr })}
                      </span>
                    )}
                  </CardDescription>
                </div>
                <div className="flex gap-2 items-center">
                  <Badge variant="outline" className="text-xs">
                    {rappatriement.produits.length} produit(s)
                  </Badge>
                  <Badge variant="secondary" className="text-xs">
                    {calculerPoidsTotal(rappatriement.produits).toFixed(1)} kg
                  </Badge>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleExport(rappatriement)}
                    className="flex items-center gap-1 text-xs h-7 px-2"
                    title="Exporter en XLSX"
                  >
                    <FileDown className="h-3.5 w-3.5" />
                    Export
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Informations générales */}
                <div className="space-y-4">
                  <div>
                    <h4 className="font-semibold mb-2 flex items-center gap-2">
                      <MapPin className="h-4 w-4" />
                      Adresses
                    </h4>
                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="font-medium">Destinataire:</span>
                        <p className="text-muted-foreground">{rappatriement.adresse_destinataire}</p>
                      </div>
                      <div>
                        <span className="font-medium">Enlèvement:</span>
                        <p className="text-muted-foreground">{rappatriement.adresse_enlevement}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold mb-2">Contacts</h4>
                    <p className="text-sm text-muted-foreground">
                      {rappatriement.contacts.trim() ? rappatriement.contacts : "Aucun contact renseigné"}
                    </p>
                  </div>
                  
                  {rappatriement.remarques && (
                    <div>
                      <h4 className="font-semibold mb-2">Remarques</h4>
                      <p className="text-sm text-muted-foreground">{rappatriement.remarques}</p>
                    </div>
                  )}
                </div>
                
                {/* Liste des produits */}
                <div>
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <Package className="h-4 w-4" />
                    Produits ({rappatriement.produits.length})
                  </h4>
                  <div className="space-y-3 max-h-64 overflow-y-auto">
                    {rappatriement.produits.map((produit: ProduitRappatriement, index: number) => (
                      <div key={index} className="border rounded-lg p-3 bg-gray-50">
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex items-center gap-2">
                            <div>
                              <h5 className="font-medium text-sm">{produit.designation_prdt}</h5>
                              <p className="text-xs text-muted-foreground">Code: {produit.code_prdt}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-1">
                            <Badge variant="outline" className="text-xs">
                              {produit.type_emballage}
                            </Badge>
                            {produit.prelevement && (
                              <Badge variant="secondary" className="text-xs bg-orange-100 text-orange-800 border-orange-200">
                                <TestTube className="h-3 w-3 mr-1" />
                                Prélèvement
                              </Badge>
                            )}
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-xs">
                          <div>
                            <span className="font-medium">Lot:</span> {produit.lot}
                          </div>
                          <div>
                            <span className="font-medium">Poids:</span> {produit.poids_net} kg
                          </div>
                          <div>
                            <span className="font-medium">Contenants:</span> {produit.nb_contenants}
                          </div>
                          <div>
                            <span className="font-medium">Palettes:</span> {produit.nb_palettes}
                          </div>
                          <div>
                            <span className="font-medium">Code ONU:</span> {produit.code_onu}
                          </div>
                          <div>
                            <span className="font-medium">Groupe:</span> {produit.grp_emballage}
                          </div>
                          {produit.po && (
                            <div>
                              <span className="font-medium">PO:</span> {produit.po}
                            </div>
                          )}

                        </div>
                        {produit.stock_solde && (
                          <Badge variant="destructive" className="text-xs mt-2">
                            Stock soldé
                          </Badge>
                        )}
                      </div>
                    ))}
                  </div>
                  
                  {/* Résumé des totaux */}
                  <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                    <h5 className="font-semibold text-sm mb-2">Résumé</h5>
                    <div className="grid grid-cols-3 gap-4 text-xs">
                      <div>
                        <span className="font-medium">Poids total:</span>
                        <p className="text-blue-600 font-semibold">{calculerPoidsTotal(rappatriement.produits).toFixed(1)} kg</p>
                      </div>
                      <div>
                        <span className="font-medium">Palettes:</span>
                        <p className="text-blue-600 font-semibold">{calculerPalettesTotal(rappatriement.produits)}</p>
                      </div>
                      <div>
                        <span className="font-medium">Contenants:</span>
                        <p className="text-blue-600 font-semibold">{calculerContenantsTotal(rappatriement.produits)}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );

  return (
    <ResourcePageLayout
      title="Gestion des Rappatriements"
      actions={{
        add: {
          show: true,
          onClick: () => router.push("/rappatriements/create"),
          label: "Nouveau Rappatriement"
        },
        import: {
          show: true,
          importFunction: importRappatriementsFromFile,
          label: "Ajouter Rappatriement",
          onSuccess: handleImportSuccess
        },
        flush: {
          show: true,
          flushFunction: flushRappatriements,
          confirmMessage: "Êtes-vous sûr de vouloir vider tous les rapatriements ? Cette action est irréversible.",
          label: "Vider tous"
        },
        refresh: {
          show: true,
          onRefresh: refetch,
          isLoading: isLoading
        }
      }}
      queryKey={['rappatriement-data']}
      hasData={!!rapatriementData && Array.isArray(rapatriementData) && rapatriementData.length > 0}
      emptyMessage="Aucun rapatriement disponible"
      emptyDescription="Aucun rapatriement disponible pour le moment. Importez un fichier CSV pour commencer."
    >
      {rapatriementsContent}
    </ResourcePageLayout>
  );
} 